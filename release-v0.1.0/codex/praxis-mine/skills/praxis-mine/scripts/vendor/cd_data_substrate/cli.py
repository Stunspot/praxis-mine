from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .storage import (
    SOURCE_KINDS,
    SENSITIVITY,
    SubstrateError,
    add_event,
    add_record,
    add_relation,
    backup_store,
    check_store,
    create_store,
    default_home,
    export_store,
    get_record,
    initialize_home,
    install_contract,
    list_records,
    list_stores,
    record_history,
    restore_as_store,
    revise_record,
    search_records,
)


def json_value(text: str | None, file: Path | None, label: str) -> Any:
    if (text is None) == (file is None):
        raise SubstrateError(f"provide exactly one of --{label} or --{label}-file")
    try:
        raw = text if text is not None else file.read_text(encoding="utf-8")
        return json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SubstrateError(f"invalid {label} JSON: {exc}") from exc


def add_json_input(parser: argparse.ArgumentParser, label: str) -> None:
    parser.add_argument(f"--{label}")
    parser.add_argument(f"--{label}-file", type=Path)


def provenance(args: argparse.Namespace) -> dict[str, Any]:
    value = json_value(args.provenance, args.provenance_file, "provenance")
    if not isinstance(value, dict) or not value:
        raise SubstrateError("provenance must be a non-empty JSON object")
    return value


def payload(args: argparse.Namespace) -> dict[str, Any]:
    value = json_value(args.data, args.data_file, "data")
    if not isinstance(value, dict):
        raise SubstrateError("data must be a JSON object")
    return value


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Collaborative Dynamics harness data substrate")
    root.add_argument("--home", type=Path, default=default_home(), help="Substrate home (default: CD_DATA_HOME, CODEX_HOME/data, or ~/.codex/data)")
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)

    commands.add_parser("init", help="Initialize the harness registry and data directories")
    commands.add_parser("stores", help="List registered bounded stores")

    create = commands.add_parser("create-store", help="Create one capability-owned SQLite store")
    create.add_argument("store")
    create.add_argument("--purpose", required=True)
    create.add_argument("--owner", required=True)
    create.add_argument("--sensitivity", choices=sorted(SENSITIVITY), default="internal")

    define = commands.add_parser("install-contract", help="Validate and install a cd-data-contract/v1 contract")
    define.add_argument("store")
    define.add_argument("contract", type=Path)
    define.add_argument("--actor", required=True)

    add = commands.add_parser("add", help="Create a typed record with provenance")
    add.add_argument("store")
    add.add_argument("record_type")
    add_json_input(add, "data")
    add_json_input(add, "provenance")
    add.add_argument("--actor", required=True)
    add.add_argument("--source-kind", choices=sorted(SOURCE_KINDS), required=True)
    add.add_argument("--id")
    add.add_argument("--effective-at")
    add.add_argument("--sensitivity", choices=sorted(SENSITIVITY))

    revise = commands.add_parser("revise", help="Append a new complete version of a record")
    revise.add_argument("store")
    revise.add_argument("record_id")
    add_json_input(revise, "data")
    add_json_input(revise, "provenance")
    revise.add_argument("--actor", required=True)
    revise.add_argument("--source-kind", choices=sorted(SOURCE_KINDS), required=True)
    revise.add_argument("--reason", required=True)
    revise.add_argument("--effective-at")
    revise.add_argument("--status", choices=["active", "superseded", "deleted"], default="active")

    get = commands.add_parser("get", help="Get the current version of a record")
    get.add_argument("store")
    get.add_argument("record_id")

    history = commands.add_parser("history", help="Get all versions of a record")
    history.add_argument("store")
    history.add_argument("record_id")

    listing = commands.add_parser("list", help="List current records")
    listing.add_argument("store")
    listing.add_argument("--type", dest="record_type")
    listing.add_argument("--status", choices=["active", "superseded", "deleted", "all"], default="active")

    search = commands.add_parser("search", help="Search current JSON payloads")
    search.add_argument("store")
    search.add_argument("query")
    search.add_argument("--type", dest="record_type")

    relate = commands.add_parser("relate", help="Create a provenance-bearing relationship")
    relate.add_argument("store")
    relate.add_argument("relation_type")
    relate.add_argument("from_record_id")
    relate.add_argument("to_record_id")
    add_json_input(relate, "provenance")
    relate.add_argument("--actor", required=True)
    relate.add_argument("--data", default="{}")

    event = commands.add_parser("event", help="Append an operational event")
    event.add_argument("store")
    event.add_argument("event_type")
    add_json_input(event, "data")
    add_json_input(event, "provenance")
    event.add_argument("--actor", required=True)
    event.add_argument("--source-kind", choices=sorted(SOURCE_KINDS), required=True)
    event.add_argument("--record-id")
    event.add_argument("--effective-at")

    check = commands.add_parser("check", help="Run integrity, foreign-key, and current-pointer checks")
    check.add_argument("store")

    backup = commands.add_parser("backup", help="Create a new non-overwriting verified SQLite backup")
    backup.add_argument("store")
    backup.add_argument("--destination", type=Path)

    restore = commands.add_parser("restore", help="Restore a backup as a new bounded store")
    restore.add_argument("backup", type=Path)
    restore.add_argument("new_store")
    restore.add_argument("--owner", required=True)

    export = commands.add_parser("export", help="Export a portable JSONL snapshot with custody metadata")
    export.add_argument("store")
    export.add_argument("--destination", type=Path)
    return root


def run(args: argparse.Namespace) -> Any:
    home = args.home
    if args.command == "init":
        return initialize_home(home)
    if args.command == "stores":
        return list_stores(home)
    if args.command == "create-store":
        return create_store(home, args.store, args.purpose, args.owner, args.sensitivity)
    if args.command == "install-contract":
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        return install_contract(home, args.store, contract, args.actor)
    if args.command == "add":
        return add_record(home, args.store, args.record_type, payload(args), args.actor, args.source_kind, provenance(args), record_id=args.id, effective_at=args.effective_at, sensitivity=args.sensitivity)
    if args.command == "revise":
        return revise_record(home, args.store, args.record_id, payload(args), args.actor, args.source_kind, provenance(args), args.reason, effective_at=args.effective_at, status=args.status)
    if args.command == "get":
        return get_record(home, args.store, args.record_id)
    if args.command == "history":
        return record_history(home, args.store, args.record_id)
    if args.command == "list":
        return list_records(home, args.store, args.record_type, None if args.status == "all" else args.status)
    if args.command == "search":
        return search_records(home, args.store, args.query, args.record_type)
    if args.command == "relate":
        relation_payload = json.loads(args.data)
        if not isinstance(relation_payload, dict):
            raise SubstrateError("relation --data must be a JSON object")
        return add_relation(home, args.store, args.relation_type, args.from_record_id, args.to_record_id, args.actor, provenance(args), relation_payload)
    if args.command == "event":
        return add_event(home, args.store, args.event_type, payload(args), args.actor, args.source_kind, provenance(args), record_id=args.record_id, effective_at=args.effective_at)
    if args.command == "check":
        return check_store(home, args.store)
    if args.command == "backup":
        return backup_store(home, args.store, args.destination)
    if args.command == "restore":
        return restore_as_store(home, args.backup, args.new_store, args.owner)
    if args.command == "export":
        return export_store(home, args.store, args.destination)
    raise SubstrateError(f"unsupported command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = run(args)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        if args.command == "check" and not result["healthy"]:
            return 1
        return 0
    except (SubstrateError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

