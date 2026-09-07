import json
from pathlib import Path
import pytest
from mini_commerce_mcp import tooling
from mini_commerce_mcp.security import redact, validate_readonly_sql


@pytest.fixture(autouse=True)
def audit_location(tmp_path, monkeypatch):
    monkeypatch.setattr(tooling, "AUDIT", tmp_path / "audit.jsonl")


def test_nested_redaction_is_structural_and_keeps_valid_json():
    value = {
        "password": "plain",
        "nested": [{"access_token": "abc"}],
        "text": "AWS=" + "AKIA" + "A" * 16,
        "normal": 'quoted " data',
    }
    result = redact(value)
    assert result["password"] == "<redacted>"
    assert result["nested"][0]["access_token"] == "<redacted>"
    assert "AKIA" not in result["text"]
    assert json.loads(json.dumps(result)) == result


@pytest.mark.parametrize(
    "sql",
    [
        "EXPLAIN SELECT 1",
        "EXPLAIN ANALYZE SELECT 1",
        "select * into new_table from orders",
        "select 1 -- comment",
        "with x as (delete from orders returning *) select * from x",
    ],
)
def test_unsupported_or_executable_sql_is_rejected(sql):
    with pytest.raises(ValueError):
        validate_readonly_sql(sql)


def test_search_cannot_follow_outside_symlink(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    docs = root / "mini-commerce/docs"
    docs.mkdir(parents=True)
    outside = tmp_path / "outside.md"
    outside.write_text("needle private content")
    (docs / "leak.md").symlink_to(outside)
    monkeypatch.setattr(tooling, "ROOT", root)
    assert tooling.search_docs("needle")["data"] == []


def test_offline_schema_includes_later_migrations(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    folder = root / "mini-commerce/backend/src/main/resources/db/migration"
    folder.mkdir(parents=True)
    (folder / "V001__initial.sql").write_text("create table a(id int);")
    (folder / "V003__refunds.sql").write_text("create table refunds(id int);")
    monkeypatch.setattr(tooling, "ROOT", root)
    monkeypatch.delenv("DATABASE_READONLY_URL", raising=False)
    assert len(tooling.database_schema()["data"]["migrations"]) == 2


def test_execution_off_by_default_and_denials_audited(monkeypatch):
    monkeypatch.delenv("MCP_ENABLE_TEST_EXECUTION", raising=False)
    with pytest.raises(ValueError, match="execution disabled"):
        tooling.run_suite("backend-all")
    assert json.loads(tooling.AUDIT.read_text())["status"] == "error"


def test_http_never_enables_test_execution(monkeypatch):
    monkeypatch.setenv("MCP_ENABLE_TEST_EXECUTION", "true")
    monkeypatch.setenv("MCP_TRANSPORT", "streamable-http")
    assert not tooling.execution_enabled()


def test_runbook_escape_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(tooling, "ROOT", tmp_path)
    with pytest.raises(ValueError):
        tooling.read_runbook("../other.md")
