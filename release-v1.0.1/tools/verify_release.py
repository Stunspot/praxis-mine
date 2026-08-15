#!/usr/bin/env python3
"""Verify the extracted Praxis Mine release with Python's standard library."""

from __future__ import annotations

import hashlib
import io
import json
import re
import struct
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


VERSION = "1.0.1"
SLUG = "praxis-mine"
SCHEMA = "praxis-mine-portable-verification/v1"
PRIVATE_TOPOLOGY_PATTERN = re.compile(
    r"(?i)(?:C:[\\/]+Users[\\/]+user(?:[\\/]+|$)|E:[\\/]+(?:Github|Indranet)(?:[\\/]+|$))"
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def safe_member_name(name: str) -> bool:
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        return False
    trimmed = name[:-1] if name.endswith("/") else name
    if not trimmed:
        return False
    return all(part and part not in {".", ".."} and ":" not in part for part in trimmed.split("/"))


def read_json(path: Path, findings: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        findings.append(f"{label}: invalid or missing JSON: {error}")
        return {}
    if not isinstance(value, dict):
        findings.append(f"{label}: JSON root must be an object")
        return {}
    return value


def file_inventory(root: Path) -> dict[str, dict[str, Any]]:
    return {
        path.relative_to(root).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix.lower() not in {".pyc", ".pyo"}
    }


def verify_inventory(
    root: Path,
    expected: object,
    findings: list[str],
    label: str,
) -> int:
    if not isinstance(expected, list):
        findings.append(f"{label}: inventory must be a list")
        return 0
    expected_map = {
        item.get("path"): item
        for item in expected
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    if len(expected_map) != len(expected):
        findings.append(f"{label}: inventory has malformed or duplicate entries")
    actual = file_inventory(root) if root.is_dir() else {}
    if set(actual) != set(expected_map):
        findings.append(f"{label}: file set differs from manifest")
    checked = 0
    for relative, record in expected_map.items():
        if not safe_member_name(relative):
            findings.append(f"{label}: unsafe manifest path: {relative}")
            continue
        current = actual.get(relative)
        if current != {"bytes": record.get("bytes"), "sha256": record.get("sha256")}:
            findings.append(f"{label}: byte/hash mismatch: {relative}")
        checked += 1
    return checked


def inspect_zip(
    path: Path,
    findings: list[str],
    label: str,
    expected_root: str | None = None,
    expected_files: dict[str, dict[str, Any]] | None = None,
) -> int:
    try:
        data = path.read_bytes()
    except OSError as error:
        findings.append(f"{label}: missing or unreadable archive: {error}")
        return 0
    members = 0
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos if not info.is_dir()]
            if len({name.casefold() for name in names}) != len(names):
                findings.append(f"{label}: duplicate or case-colliding members")
            for info in infos:
                members += 1
                if not safe_member_name(info.filename):
                    findings.append(f"{label}: unsafe member: {info.filename}")
                if info.flag_bits & 0x1:
                    findings.append(f"{label}: encrypted member: {info.filename}")
                if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                    findings.append(f"{label}: symlink member: {info.filename}")
            if expected_root:
                prefix = expected_root.rstrip("/") + "/"
                if not names or any(not name.startswith(prefix) for name in names):
                    findings.append(f"{label}: files must live under one {expected_root}/ root")
            if expected_files is not None:
                prefix = expected_root.rstrip("/") + "/" if expected_root else ""
                actual = {}
                for name in names:
                    relative = name[len(prefix):] if prefix and name.startswith(prefix) else name
                    payload = archive.read(name)
                    actual[relative] = {"bytes": len(payload), "sha256": sha256_bytes(payload)}
                if actual != expected_files:
                    findings.append(f"{label}: archive bytes differ from source tree")
    except zipfile.BadZipFile as error:
        findings.append(f"{label}: invalid ZIP: {error}")
    return members


def png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def verify_markdown_links(root: Path, docs: list[str], findings: list[str]) -> int:
    checked = 0
    for relative in docs:
        path = root / PurePosixPath(relative)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for target in MARKDOWN_LINK.findall(text):
            clean = target.strip().strip("<>")
            if not clean or clean.startswith(("#", "http://", "https://", "mailto:")):
                continue
            file_part = clean.split("#", 1)[0]
            if not file_part:
                continue
            checked += 1
            candidate = (path.parent / PurePosixPath(file_part)).resolve(strict=False)
            if not candidate.is_file():
                findings.append(f"docs: broken relative link in {relative}: {clean}")
    return checked


def verify(root: Path, *, require_complete: bool = True) -> dict[str, Any]:
    root = root.resolve()
    findings: list[str] = []
    counts = {
        "manifest_files_checked": 0,
        "archives_checked": 0,
        "zip_members_checked": 0,
        "documentation_links_checked": 0,
    }

    manifest = read_json(root / "manifest.json", findings, "manifest")
    if manifest.get("schema") != "praxis-mine-release/v1":
        findings.append("manifest: unexpected schema")
    if manifest.get("version") != VERSION or manifest.get("slug") != SLUG:
        findings.append("manifest: product identity differs from verifier")

    plugin_root = root / "codex" / SLUG
    plugin = read_json(plugin_root / ".codex-plugin" / "plugin.json", findings, "plugin")
    if plugin.get("name") != SLUG or plugin.get("version") != VERSION:
        findings.append("plugin: name or version mismatch")
    if not SEMVER.match(str(plugin.get("version", ""))):
        findings.append("plugin: version is not semantic version syntax")
    if plugin.get("skills") != "./skills/":
        findings.append("plugin: skills must equal ./skills/")
    interface = plugin.get("interface") if isinstance(plugin.get("interface"), dict) else {}
    short = interface.get("shortDescription")
    if not isinstance(short, str) or not 1 <= len(short) <= 30:
        findings.append("plugin: directory shortDescription must be 1-30 characters")
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3 or any(
        not isinstance(item, str) or not item or len(item) > 128 for item in prompts
    ):
        findings.append("plugin: defaultPrompt must contain 1-3 strings of at most 128 characters")
    for field in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
        value = interface.get(field)
        if not isinstance(value, str) or not value.startswith("https://"):
            findings.append(f"plugin: {field} must be an HTTPS URL")
    for field in ("composerIcon", "logo"):
        value = interface.get(field)
        if not isinstance(value, str) or not value.startswith("./"):
            findings.append(f"plugin: {field} must be a relative path")
            continue
        asset = plugin_root / PurePosixPath(value[2:])
        dimensions = png_dimensions(asset)
        if not dimensions or dimensions[0] != dimensions[1]:
            findings.append(f"plugin: {field} must reference a square PNG")

    skill_root = plugin_root / "skills" / SLUG
    skill_text = ""
    try:
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        findings.append(f"skill: SKILL.md missing or unreadable: {error}")
    if "name: praxis-mine" not in skill_text or "description:" not in skill_text:
        findings.append("skill: required front matter is missing")
    runtime_text = ""
    try:
        runtime_text = (skill_root / "scripts" / "praxis_mine.py").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        findings.append(f"runtime: main script missing or unreadable: {error}")
    for forbidden in ("CODEX_HOME", "CD_DATA_SUBSTRATE_ROOT", "Omnicompetence"):
        if forbidden in runtime_text:
            findings.append(f"runtime: private host dependency remains: {forbidden}")
    if "from praxis_store import storage" not in runtime_text:
        findings.append("runtime: embedded store import is missing")
    if not (skill_root / "scripts" / "vendor" / "praxis_store" / "storage.py").is_file():
        findings.append("runtime: embedded store file is missing")

    counts["manifest_files_checked"] += verify_inventory(
        plugin_root, manifest.get("plugin_files"), findings, "plugin"
    )
    counts["manifest_files_checked"] += verify_inventory(
        skill_root, manifest.get("skill_files"), findings, "skill"
    )

    doc_manifest = read_json(root / "documentation-manifest.json", findings, "documentation manifest")
    docs = doc_manifest.get("customer_docs")
    if not isinstance(docs, list) or not docs or any(not isinstance(item, str) for item in docs):
        findings.append("documentation manifest: customer_docs must be a non-empty string list")
        docs = []
    for relative in docs:
        if not safe_member_name(relative) or not (root / PurePosixPath(relative)).is_file():
            findings.append(f"docs: missing or unsafe customer document: {relative}")
    if manifest.get("customer_docs") != docs:
        findings.append("manifest: customer document inventory differs from documentation manifest")
    counts["documentation_links_checked"] = verify_markdown_links(root, docs, findings)

    source_skill = file_inventory(skill_root)
    source_plugin = file_inventory(plugin_root)
    archives = manifest.get("archives")
    if not isinstance(archives, list):
        findings.append("manifest: archives must be a list")
        archives = []
    for record in archives:
        if not isinstance(record, dict):
            findings.append("manifest: archive record must be an object")
            continue
        relative = record.get("path")
        kind = record.get("kind")
        if not isinstance(relative, str) or not safe_member_name(relative):
            findings.append("manifest: archive path is missing or unsafe")
            continue
        archive_path = root / PurePosixPath(relative)
        try:
            digest = sha256_file(archive_path)
        except OSError as error:
            findings.append(f"archive: missing {relative}: {error}")
            continue
        if digest != record.get("sha256"):
            findings.append(f"archive: digest mismatch: {relative}")
        if kind == "plugin":
            expected_root, expected = SLUG, source_plugin
        elif kind in {"claude-skill", "standalone-skill"}:
            expected_root, expected = SLUG, source_skill
        else:
            findings.append(f"archive: unknown kind for {relative}: {kind}")
            continue
        counts["archives_checked"] += 1
        counts["zip_members_checked"] += inspect_zip(
            archive_path, findings, relative, expected_root, expected
        )

    component_custody = read_json(
        root / "component-custody.json", findings, "component custody"
    )
    component_records = (
        component_custody.get("archives")
        if isinstance(component_custody.get("archives"), list)
        else []
    )
    component_by_name = {
        item.get("file"): item for item in component_records if isinstance(item, dict)
    }
    for record in archives:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            continue
        path = root / PurePosixPath(record["path"])
        custody_record = component_by_name.get(path.name)
        if (
            not isinstance(custody_record, dict)
            or custody_record.get("sha256") != record.get("sha256")
            or custody_record.get("kind") != record.get("kind")
        ):
            findings.append(f"component custody: missing or mismatched record for {path.name}")

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".png", ".zip", ".sqlite"}:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if PRIVATE_TOPOLOGY_PATTERN.search(data.decode("utf-8", errors="ignore")):
            findings.append(f"tree: private workstation path in {path.relative_to(root).as_posix()}")

    if require_complete:
        kit = root / f"Praxis-Mine-v{VERSION}.zip"
        checksum = root / f"Praxis-Mine-v{VERSION}.zip.sha256"
        custody = read_json(root / "archive-custody.json", findings, "archive custody")
        try:
            kit_hash = sha256_file(kit)
        except OSError as error:
            findings.append(f"complete kit: missing: {error}")
            kit_hash = ""
        try:
            checksum_text = checksum.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError) as error:
            findings.append(f"complete kit: checksum missing: {error}")
            checksum_text = ""
        if kit_hash and checksum_text != f"{kit_hash}  {kit.name}":
            findings.append("complete kit: detached checksum mismatch")
        custody_records = custody.get("archives") if isinstance(custody.get("archives"), list) else []
        custody_by_name = {
            item.get("file"): item for item in custody_records if isinstance(item, dict)
        }
        for path in [kit] + [root / PurePosixPath(item.get("path")) for item in archives if isinstance(item, dict) and isinstance(item.get("path"), str)]:
            record = custody_by_name.get(path.name)
            if not isinstance(record, dict) or record.get("sha256") != sha256_file(path):
                findings.append(f"archive custody: missing or mismatched record for {path.name}")
        counts["archives_checked"] += 1
        counts["zip_members_checked"] += inspect_zip(kit, findings, kit.name)

    findings = sorted(set(findings))
    return {"schema": SCHEMA, "ok": not findings, "counts": counts, "findings": findings}


def main(argv: list[str] | None = None) -> int:
    arguments = argv if argv is not None else sys.argv[1:]
    component_only = False
    if "--component-only" in arguments:
        component_only = True
        arguments = [item for item in arguments if item != "--component-only"]
    if len(arguments) > 1 or any(item.startswith("-") for item in arguments):
        report = {
            "schema": SCHEMA,
            "ok": False,
            "counts": {},
            "findings": ["usage: verify_release.py [release-root] [--component-only]"],
        }
    else:
        report = verify(
            Path(arguments[0]) if arguments else Path.cwd(),
            require_complete=not component_only,
        )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
