from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


NAME = re.compile(r"^[a-z][a-z0-9_]*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
FIELD_TYPES = {"text", "integer", "number", "boolean", "timestamp", "date", "json", "reference"}
SOURCE_KINDS = {"observed", "supplied", "derived", "deterministic"}
SENSITIVITY = {"public", "internal", "confidential", "restricted"}
SCHEMA_VERSION = 1


REGISTRY_SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS ds_registry_meta(
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS ds_stores(
    store_name TEXT PRIMARY KEY,
    purpose TEXT NOT NULL,
    owner TEXT NOT NULL,
    default_sensitivity TEXT NOT NULL,
    store_path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('active','retired'))
) STRICT;
"""


STORE_SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS ds_meta(
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS ds_contracts(
    schema_version TEXT PRIMARY KEY,
    contract_json TEXT NOT NULL,
    contract_hash TEXT NOT NULL,
    installed_at TEXT NOT NULL,
    actor TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS ds_record_types(
    record_type TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL REFERENCES ds_contracts(schema_version),
    definition_json TEXT NOT NULL,
    installed_at TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS ds_records(
    record_id TEXT PRIMARY KEY,
    record_type TEXT NOT NULL REFERENCES ds_record_types(record_type),
    current_version INTEGER NOT NULL CHECK(current_version >= 1),
    status TEXT NOT NULL CHECK(status IN ('active','superseded','deleted')),
    sensitivity TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS ds_record_versions(
    record_id TEXT NOT NULL REFERENCES ds_records(record_id),
    version INTEGER NOT NULL CHECK(version >= 1),
    payload_json TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    actor TEXT NOT NULL,
    effective_at TEXT,
    recorded_at TEXT NOT NULL,
    supersedes_version INTEGER,
    reason TEXT,
    content_hash TEXT NOT NULL,
    PRIMARY KEY(record_id, version)
) STRICT;
CREATE TABLE IF NOT EXISTS ds_relations(
    relation_id TEXT PRIMARY KEY,
    relation_type TEXT NOT NULL,
    from_record_id TEXT NOT NULL REFERENCES ds_records(record_id),
    to_record_id TEXT NOT NULL REFERENCES ds_records(record_id),
    payload_json TEXT NOT NULL,
    actor TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('active','superseded','deleted'))
) STRICT;
CREATE TABLE IF NOT EXISTS ds_events(
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    record_id TEXT REFERENCES ds_records(record_id),
    payload_json TEXT NOT NULL,
    actor TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    effective_at TEXT,
    recorded_at TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS ds_audit(
    audit_id INTEGER PRIMARY KEY,
    action TEXT NOT NULL,
    subject_id TEXT,
    actor TEXT NOT NULL,
    details_json TEXT NOT NULL,
    recorded_at TEXT NOT NULL
) STRICT;
CREATE INDEX IF NOT EXISTS idx_record_type_status ON ds_records(record_type, status);
CREATE INDEX IF NOT EXISTS idx_versions_recorded ON ds_record_versions(recorded_at);
CREATE INDEX IF NOT EXISTS idx_relations_from ON ds_relations(from_record_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_relations_to ON ds_relations(to_record_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_events_type_time ON ds_events(event_type, recorded_at);
"""


class SubstrateError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def default_home() -> Path:
    explicit = os.environ.get("PRAXIS_MINE_DATA_HOME")
    if explicit:
        return Path(explicit).expanduser()
    return Path.home() / ".praxis-mine" / "data"


def validate_name(value: str, label: str) -> None:
    if not NAME.match(value):
        raise SubstrateError(f"{label} must use lowercase snake_case: {value!r}")


def connect(path: Path, *, read_only: bool = False) -> sqlite3.Connection:
    if read_only:
        resolved = path.resolve(strict=True)
        connection = sqlite3.connect(f"file:{resolved.as_posix()}?mode=ro", uri=True)
    else:
        connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA busy_timeout=5000")
    return connection


def initialize_home(home: Path) -> dict[str, str]:
    home = home.expanduser().resolve()
    home.mkdir(parents=True, exist_ok=True)
    for name in ("stores", "backups", "exports"):
        (home / name).mkdir(exist_ok=True)
    registry = home / "registry.sqlite"
    connection = connect(registry)
    try:
        connection.executescript(REGISTRY_SCHEMA)
        timestamp = now()
        connection.execute(
            "INSERT OR REPLACE INTO ds_registry_meta(key,value_json,updated_at) VALUES (?,?,?)",
            ("schema_version", canonical_json(SCHEMA_VERSION), timestamp),
        )
        connection.commit()
    finally:
        connection.close()
    return {"home": str(home), "registry": str(registry)}


def registry_path(home: Path) -> Path:
    return home.expanduser().resolve() / "registry.sqlite"


def store_path(home: Path, store_name: str) -> Path:
    validate_name(store_name, "store name")
    return home.expanduser().resolve() / "stores" / f"{store_name}.sqlite"


def create_store(home: Path, store_name: str, purpose: str, owner: str, sensitivity: str) -> dict[str, Any]:
    validate_name(store_name, "store name")
    if sensitivity not in SENSITIVITY:
        raise SubstrateError(f"invalid sensitivity: {sensitivity}")
    initialize_home(home)
    path = store_path(home, store_name)
    if path.exists():
        raise SubstrateError(f"store already exists: {store_name}")

    connection = connect(path)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.executescript(STORE_SCHEMA)
        timestamp = now()
        metadata = {
            "substrate_schema_version": SCHEMA_VERSION,
            "store_name": store_name,
            "purpose": purpose,
            "owner": owner,
            "default_sensitivity": sensitivity,
            "created_at": timestamp,
        }
        for key, value in metadata.items():
            connection.execute(
                "INSERT INTO ds_meta(key,value_json,updated_at) VALUES (?,?,?)",
                (key, canonical_json(value), timestamp),
            )
        connection.execute(
            "INSERT INTO ds_audit(action,subject_id,actor,details_json,recorded_at) VALUES (?,?,?,?,?)",
            ("store_created", store_name, owner, canonical_json(metadata), timestamp),
        )
        connection.commit()
    except Exception:
        connection.close()
        if path.exists():
            path.unlink()
        raise
    finally:
        try:
            connection.close()
        except Exception:
            pass

    registry = connect(registry_path(home))
    try:
        timestamp = now()
        registry.execute(
            "INSERT INTO ds_stores(store_name,purpose,owner,default_sensitivity,store_path,created_at,updated_at,status) "
            "VALUES (?,?,?,?,?,?,?,'active')",
            (store_name, purpose, owner, sensitivity, str(path), timestamp, timestamp),
        )
        registry.commit()
    except Exception:
        registry.close()
        if path.exists():
            path.unlink()
        raise
    finally:
        try:
            registry.close()
        except Exception:
            pass
    return {"store_name": store_name, "store_path": str(path), "status": "active"}


def list_stores(home: Path) -> list[dict[str, Any]]:
    connection = connect(registry_path(home), read_only=True)
    try:
        return [dict(row) for row in connection.execute("SELECT * FROM ds_stores ORDER BY store_name")]
    finally:
        connection.close()


def require_store(home: Path, store_name: str, *, read_only: bool = False) -> tuple[Path, sqlite3.Connection]:
    path = store_path(home, store_name)
    if not path.is_file():
        raise SubstrateError(f"unknown store: {store_name}")
    return path, connect(path, read_only=read_only)


def validate_contract(contract: Any, expected_store: str | None = None) -> None:
    if not isinstance(contract, dict) or contract.get("format") != "cd-data-contract/v1":
        raise SubstrateError("contract format must equal cd-data-contract/v1")
    version = contract.get("schema_version")
    if not isinstance(version, str) or not SEMVER.match(version):
        raise SubstrateError("contract schema_version must be semantic version syntax")
    system = contract.get("system")
    if not isinstance(system, dict):
        raise SubstrateError("contract system object required")
    name = system.get("name")
    if not isinstance(name, str) or not NAME.match(name):
        raise SubstrateError("contract system.name must use lowercase snake_case")
    if expected_store and name != expected_store:
        raise SubstrateError(f"contract system.name {name!r} does not match store {expected_store!r}")
    records = contract.get("record_types")
    if not isinstance(records, list) or not records:
        raise SubstrateError("contract requires non-empty record_types")
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise SubstrateError("record type must be an object")
        record_type = record.get("name")
        if not isinstance(record_type, str) or not NAME.match(record_type) or record_type in seen:
            raise SubstrateError(f"invalid or duplicate record type: {record_type!r}")
        seen.add(record_type)
        fields = record.get("fields")
        identity = record.get("identity")
        if not isinstance(fields, list) or not fields or not isinstance(identity, list) or not identity:
            raise SubstrateError(f"record type {record_type} requires fields and identity")
        field_map: dict[str, dict[str, Any]] = {}
        for field in fields:
            if not isinstance(field, dict):
                raise SubstrateError(f"record type {record_type} has invalid field")
            field_name = field.get("name")
            if not isinstance(field_name, str) or not NAME.match(field_name) or field_name in field_map:
                raise SubstrateError(f"record type {record_type} has invalid or duplicate field {field_name!r}")
            if field.get("type") not in FIELD_TYPES or not isinstance(field.get("required"), bool):
                raise SubstrateError(f"field {record_type}.{field_name} has invalid type or required flag")
            if field.get("source_kind") not in SOURCE_KINDS:
                raise SubstrateError(f"field {record_type}.{field_name} has invalid source_kind")
            field_map[field_name] = field
        for identity_field in identity:
            if identity_field not in field_map or field_map[identity_field].get("required") is not True:
                raise SubstrateError(f"identity field {record_type}.{identity_field} must exist and be required")
    entry = contract.get("entry_protocol")
    if not isinstance(entry, dict) or entry.get("actor_required") is not True or entry.get("provenance_required") is not True:
        raise SubstrateError("substrate requires actor and provenance in entry_protocol")


def install_contract(home: Path, store_name: str, contract: dict[str, Any], actor: str) -> dict[str, Any]:
    validate_contract(contract, store_name)
    _, connection = require_store(home, store_name)
    try:
        version = contract["schema_version"]
        contract_json = canonical_json(contract)
        timestamp = now()
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "INSERT INTO ds_contracts(schema_version,contract_json,contract_hash,installed_at,actor) VALUES (?,?,?,?,?)",
            (version, contract_json, content_hash(contract), timestamp, actor),
        )
        for record in contract["record_types"]:
            connection.execute(
                "INSERT INTO ds_record_types(record_type,schema_version,definition_json,installed_at) VALUES (?,?,?,?) "
                "ON CONFLICT(record_type) DO UPDATE SET schema_version=excluded.schema_version, "
                "definition_json=excluded.definition_json, installed_at=excluded.installed_at",
                (record["name"], version, canonical_json(record), timestamp),
            )
        connection.execute(
            "INSERT INTO ds_meta(key,value_json,updated_at) VALUES ('current_contract_version',?,?) "
            "ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at",
            (canonical_json(version), timestamp),
        )
        connection.execute(
            "INSERT INTO ds_audit(action,subject_id,actor,details_json,recorded_at) VALUES (?,?,?,?,?)",
            ("contract_installed", version, actor, canonical_json({"contract_hash": content_hash(contract)}), timestamp),
        )
        connection.commit()
        return {"store_name": store_name, "schema_version": version, "contract_hash": content_hash(contract)}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise SubstrateError(f"contract version already installed or invalid transition: {exc}") from exc
    finally:
        connection.close()


def record_definition(connection: sqlite3.Connection, record_type: str) -> dict[str, Any]:
    row = connection.execute(
        "SELECT definition_json FROM ds_record_types WHERE record_type=?", (record_type,)
    ).fetchone()
    if row is None:
        raise SubstrateError(f"undefined record type: {record_type}")
    return json.loads(row[0])


def valid_field_value(field_type: str, value: Any) -> bool:
    if value is None:
        return True
    if field_type in {"text", "timestamp", "date", "reference"}:
        return isinstance(value, str)
    if field_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if field_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if field_type == "boolean":
        return isinstance(value, bool)
    if field_type == "json":
        return isinstance(value, (dict, list, str, int, float, bool))
    return False


def validate_payload(definition: dict[str, Any], payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SubstrateError("record payload must be a JSON object")
    field_map = {field["name"]: field for field in definition["fields"]}
    unknown = sorted(set(payload) - set(field_map))
    if unknown:
        raise SubstrateError(f"unknown fields for {definition['name']}: {', '.join(unknown)}")
    missing = [name for name, field in field_map.items() if field.get("required") and payload.get(name) is None]
    if missing:
        raise SubstrateError(f"missing required fields for {definition['name']}: {', '.join(missing)}")
    for name, value in payload.items():
        if not valid_field_value(field_map[name]["type"], value):
            raise SubstrateError(f"field {definition['name']}.{name} does not match type {field_map[name]['type']}")


def audit(connection: sqlite3.Connection, action: str, subject: str | None, actor: str, details: Any) -> None:
    connection.execute(
        "INSERT INTO ds_audit(action,subject_id,actor,details_json,recorded_at) VALUES (?,?,?,?,?)",
        (action, subject, actor, canonical_json(details), now()),
    )


def add_record(
    home: Path,
    store_name: str,
    record_type: str,
    payload: dict[str, Any],
    actor: str,
    source_kind: str,
    provenance: dict[str, Any],
    *,
    record_id: str | None = None,
    effective_at: str | None = None,
    sensitivity: str | None = None,
) -> dict[str, Any]:
    if source_kind not in SOURCE_KINDS:
        raise SubstrateError(f"invalid source_kind: {source_kind}")
    _, connection = require_store(home, store_name)
    try:
        definition = record_definition(connection, record_type)
        validate_payload(definition, payload)
        record_id = record_id or str(uuid.uuid4())
        default_sensitivity = json.loads(connection.execute(
            "SELECT value_json FROM ds_meta WHERE key='default_sensitivity'"
        ).fetchone()[0])
        sensitivity = sensitivity or default_sensitivity
        if sensitivity not in SENSITIVITY:
            raise SubstrateError(f"invalid sensitivity: {sensitivity}")
        timestamp = now()
        payload_json = canonical_json(payload)
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "INSERT INTO ds_records(record_id,record_type,current_version,status,sensitivity,created_at,updated_at) "
            "VALUES (?,?,1,'active',?,?,?)",
            (record_id, record_type, sensitivity, timestamp, timestamp),
        )
        connection.execute(
            "INSERT INTO ds_record_versions(record_id,version,payload_json,source_kind,provenance_json,actor,effective_at,recorded_at,supersedes_version,reason,content_hash) "
            "VALUES (?,1,?,?,?,?,?,?,NULL,?,?)",
            (record_id, payload_json, source_kind, canonical_json(provenance), actor, effective_at, timestamp, "created", content_hash(payload)),
        )
        audit(connection, "record_created", record_id, actor, {"record_type": record_type, "version": 1})
        connection.commit()
        return get_record_connection(connection, record_id)
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise SubstrateError(f"record could not be created: {exc}") from exc
    finally:
        connection.close()


def get_record_connection(connection: sqlite3.Connection, record_id: str) -> dict[str, Any]:
    row = connection.execute(
        "SELECT r.*,v.payload_json,v.source_kind,v.provenance_json,v.actor,v.effective_at,v.recorded_at,v.reason,v.content_hash "
        "FROM ds_records r JOIN ds_record_versions v ON v.record_id=r.record_id AND v.version=r.current_version "
        "WHERE r.record_id=?",
        (record_id,),
    ).fetchone()
    if row is None:
        raise SubstrateError(f"unknown record: {record_id}")
    result = dict(row)
    result["payload"] = json.loads(result.pop("payload_json"))
    result["provenance"] = json.loads(result.pop("provenance_json"))
    return result


def get_record(home: Path, store_name: str, record_id: str) -> dict[str, Any]:
    _, connection = require_store(home, store_name, read_only=True)
    try:
        return get_record_connection(connection, record_id)
    finally:
        connection.close()


def revise_record(
    home: Path,
    store_name: str,
    record_id: str,
    payload: dict[str, Any],
    actor: str,
    source_kind: str,
    provenance: dict[str, Any],
    reason: str,
    *,
    effective_at: str | None = None,
    status: str = "active",
) -> dict[str, Any]:
    if source_kind not in SOURCE_KINDS:
        raise SubstrateError(f"invalid source_kind: {source_kind}")
    if status not in {"active", "superseded", "deleted"}:
        raise SubstrateError(f"invalid status: {status}")
    _, connection = require_store(home, store_name)
    try:
        current = get_record_connection(connection, record_id)
        definition = record_definition(connection, current["record_type"])
        validate_payload(definition, payload)
        next_version = current["current_version"] + 1
        timestamp = now()
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "INSERT INTO ds_record_versions(record_id,version,payload_json,source_kind,provenance_json,actor,effective_at,recorded_at,supersedes_version,reason,content_hash) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (record_id, next_version, canonical_json(payload), source_kind, canonical_json(provenance), actor, effective_at, timestamp, current["current_version"], reason, content_hash(payload)),
        )
        connection.execute(
            "UPDATE ds_records SET current_version=?,status=?,updated_at=? WHERE record_id=?",
            (next_version, status, timestamp, record_id),
        )
        audit(connection, "record_revised", record_id, actor, {"version": next_version, "status": status, "reason": reason})
        connection.commit()
        return get_record_connection(connection, record_id)
    finally:
        connection.close()


def record_history(home: Path, store_name: str, record_id: str) -> list[dict[str, Any]]:
    _, connection = require_store(home, store_name, read_only=True)
    try:
        rows = connection.execute(
            "SELECT * FROM ds_record_versions WHERE record_id=? ORDER BY version", (record_id,)
        ).fetchall()
        if not rows:
            raise SubstrateError(f"unknown record: {record_id}")
        result = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item.pop("payload_json"))
            item["provenance"] = json.loads(item.pop("provenance_json"))
            result.append(item)
        return result
    finally:
        connection.close()


def list_records(home: Path, store_name: str, record_type: str | None = None, status: str | None = "active") -> list[dict[str, Any]]:
    _, connection = require_store(home, store_name, read_only=True)
    try:
        where: list[str] = []
        params: list[Any] = []
        if record_type:
            where.append("r.record_type=?")
            params.append(record_type)
        if status:
            where.append("r.status=?")
            params.append(status)
        clause = " WHERE " + " AND ".join(where) if where else ""
        rows = connection.execute(
            "SELECT r.*,v.payload_json,v.source_kind,v.provenance_json,v.actor,v.effective_at,v.recorded_at,v.reason,v.content_hash "
            "FROM ds_records r JOIN ds_record_versions v ON v.record_id=r.record_id AND v.version=r.current_version" + clause + " ORDER BY r.updated_at DESC",
            params,
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item.pop("payload_json"))
            item["provenance"] = json.loads(item.pop("provenance_json"))
            result.append(item)
        return result
    finally:
        connection.close()


def search_records(home: Path, store_name: str, query: str, record_type: str | None = None) -> list[dict[str, Any]]:
    _, connection = require_store(home, store_name, read_only=True)
    try:
        params: list[Any] = [f"%{query.lower()}%"]
        type_clause = ""
        if record_type:
            type_clause = " AND r.record_type=?"
            params.append(record_type)
        rows = connection.execute(
            "SELECT r.*,v.payload_json,v.source_kind,v.provenance_json,v.actor,v.effective_at,v.recorded_at,v.reason,v.content_hash "
            "FROM ds_records r JOIN ds_record_versions v ON v.record_id=r.record_id AND v.version=r.current_version "
            "WHERE r.status='active' AND lower(v.payload_json) LIKE ?" + type_clause + " ORDER BY r.updated_at DESC",
            params,
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item.pop("payload_json"))
            item["provenance"] = json.loads(item.pop("provenance_json"))
            result.append(item)
        return result
    finally:
        connection.close()


def add_relation(
    home: Path,
    store_name: str,
    relation_type: str,
    from_record_id: str,
    to_record_id: str,
    actor: str,
    provenance: dict[str, Any],
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_name(relation_type, "relation type")
    _, connection = require_store(home, store_name)
    try:
        get_record_connection(connection, from_record_id)
        get_record_connection(connection, to_record_id)
        relation_id = str(uuid.uuid4())
        timestamp = now()
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "INSERT INTO ds_relations(relation_id,relation_type,from_record_id,to_record_id,payload_json,actor,provenance_json,recorded_at,status) "
            "VALUES (?,?,?,?,?,?,?,?,'active')",
            (relation_id, relation_type, from_record_id, to_record_id, canonical_json(payload or {}), actor, canonical_json(provenance), timestamp),
        )
        audit(connection, "relation_created", relation_id, actor, {"relation_type": relation_type})
        connection.commit()
        return {"relation_id": relation_id, "relation_type": relation_type, "from_record_id": from_record_id, "to_record_id": to_record_id, "recorded_at": timestamp}
    finally:
        connection.close()


def add_event(
    home: Path,
    store_name: str,
    event_type: str,
    payload: dict[str, Any],
    actor: str,
    source_kind: str,
    provenance: dict[str, Any],
    *,
    record_id: str | None = None,
    effective_at: str | None = None,
) -> dict[str, Any]:
    validate_name(event_type, "event type")
    if source_kind not in SOURCE_KINDS:
        raise SubstrateError(f"invalid source_kind: {source_kind}")
    _, connection = require_store(home, store_name)
    try:
        if record_id:
            get_record_connection(connection, record_id)
        event_id = str(uuid.uuid4())
        timestamp = now()
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "INSERT INTO ds_events(event_id,event_type,record_id,payload_json,actor,source_kind,provenance_json,effective_at,recorded_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (event_id, event_type, record_id, canonical_json(payload), actor, source_kind, canonical_json(provenance), effective_at, timestamp),
        )
        audit(connection, "event_created", event_id, actor, {"event_type": event_type, "record_id": record_id})
        connection.commit()
        return {"event_id": event_id, "event_type": event_type, "record_id": record_id, "recorded_at": timestamp}
    finally:
        connection.close()


def check_store(home: Path, store_name: str) -> dict[str, Any]:
    path, connection = require_store(home, store_name, read_only=True)
    try:
        integrity = [row[0] for row in connection.execute("PRAGMA integrity_check")]
        foreign_keys = [dict(row) for row in connection.execute("PRAGMA foreign_key_check")]
        pointer_errors = connection.execute(
            "SELECT COUNT(*) FROM ds_records r LEFT JOIN ds_record_versions v "
            "ON v.record_id=r.record_id AND v.version=r.current_version WHERE v.record_id IS NULL"
        ).fetchone()[0]
        contract_count = connection.execute("SELECT COUNT(*) FROM ds_contracts").fetchone()[0]
        return {
            "store_name": store_name,
            "store_path": str(path),
            "integrity": integrity,
            "foreign_key_violations": foreign_keys,
            "current_pointer_errors": pointer_errors,
            "contract_versions": contract_count,
            "healthy": integrity == ["ok"] and not foreign_keys and pointer_errors == 0,
        }
    finally:
        connection.close()


def backup_store(home: Path, store_name: str, destination: Path | None = None) -> dict[str, Any]:
    source = store_path(home, store_name).resolve(strict=True)
    if destination is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        destination = home.expanduser().resolve() / "backups" / f"{store_name}-{stamp}.sqlite"
    destination = destination.expanduser().resolve(strict=False)
    if destination.exists():
        raise SubstrateError(f"backup destination already exists: {destination}")
    if not destination.parent.is_dir():
        raise SubstrateError(f"backup destination parent does not exist: {destination.parent}")
    source_connection = connect(source, read_only=True)
    destination_connection = connect(destination)
    try:
        source_connection.backup(destination_connection)
        destination_connection.commit()
        integrity = [row[0] for row in destination_connection.execute("PRAGMA integrity_check")]
        foreign_keys = list(destination_connection.execute("PRAGMA foreign_key_check"))
        if integrity != ["ok"] or foreign_keys:
            raise SubstrateError("backup artifact failed integrity or foreign-key verification")
    finally:
        source_connection.close()
        destination_connection.close()
    return {
        "store_name": store_name,
        "source": str(source),
        "destination": str(destination),
        "sha256": file_hash(destination),
        "integrity": ["ok"],
        "claim": "backup artifact created and structurally verified; restoration is a separate claim",
    }


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def restore_as_store(home: Path, backup: Path, new_store_name: str, owner: str) -> dict[str, Any]:
    validate_name(new_store_name, "new store name")
    initialize_home(home)
    backup = backup.expanduser().resolve(strict=True)
    destination = store_path(home, new_store_name)
    if destination.exists():
        raise SubstrateError(f"restore destination already exists: {destination}")
    source_connection = connect(backup, read_only=True)
    destination_connection = connect(destination)
    try:
        source_connection.backup(destination_connection)
        destination_connection.commit()
        integrity = [row[0] for row in destination_connection.execute("PRAGMA integrity_check")]
        foreign_keys = list(destination_connection.execute("PRAGMA foreign_key_check"))
        if integrity != ["ok"] or foreign_keys:
            raise SubstrateError("restored store failed structural verification")
        metadata = {row["key"]: json.loads(row["value_json"]) for row in destination_connection.execute("SELECT key,value_json FROM ds_meta")}
        timestamp = now()
        destination_connection.execute(
            "INSERT INTO ds_meta(key,value_json,updated_at) VALUES ('store_name',?,?) "
            "ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at",
            (canonical_json(new_store_name), timestamp),
        )
        audit(destination_connection, "store_restored", new_store_name, owner, {"backup": str(backup), "backup_sha256": file_hash(backup)})
        destination_connection.commit()
    except Exception:
        source_connection.close()
        destination_connection.close()
        if destination.exists():
            destination.unlink()
        raise
    finally:
        try:
            source_connection.close()
            destination_connection.close()
        except Exception:
            pass

    registry = connect(registry_path(home))
    try:
        timestamp = now()
        registry.execute(
            "INSERT INTO ds_stores(store_name,purpose,owner,default_sensitivity,store_path,created_at,updated_at,status) VALUES (?,?,?,?,?,?,?,'active')",
            (new_store_name, metadata.get("purpose", "restored store"), owner, metadata.get("default_sensitivity", "internal"), str(destination), timestamp, timestamp),
        )
        registry.commit()
    finally:
        registry.close()
    return {"store_name": new_store_name, "store_path": str(destination), "backup_sha256": file_hash(backup), "healthy": True}


def export_store(home: Path, store_name: str, destination: Path | None = None) -> dict[str, Any]:
    path, connection = require_store(home, store_name, read_only=True)
    if destination is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        destination = home.expanduser().resolve() / "exports" / f"{store_name}-{stamp}.jsonl"
    destination = destination.expanduser().resolve(strict=False)
    if destination.exists():
        connection.close()
        raise SubstrateError(f"export destination already exists: {destination}")
    if not destination.parent.is_dir():
        connection.close()
        raise SubstrateError(f"export destination parent does not exist: {destination.parent}")
    tables = ["ds_meta", "ds_contracts", "ds_record_types", "ds_records", "ds_record_versions", "ds_relations", "ds_events", "ds_audit"]
    counts: dict[str, int] = {}
    try:
        with destination.open("x", encoding="utf-8", newline="\n") as stream:
            header = {"kind": "cd-data-export", "format": "cd-data-export/v1", "store_name": store_name, "source_hash": file_hash(path), "exported_at": now()}
            stream.write(canonical_json(header) + "\n")
            for table in tables:
                rows = connection.execute(f"SELECT * FROM {table}").fetchall()
                counts[table] = len(rows)
                for row in rows:
                    stream.write(canonical_json({"kind": "row", "table": table, "data": dict(row)}) + "\n")
    finally:
        connection.close()
    return {"store_name": store_name, "destination": str(destination), "sha256": file_hash(destination), "counts": counts}
