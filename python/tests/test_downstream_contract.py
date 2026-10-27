"""Guard the expected MCP2 downstream block matrix without importing consumers."""

from __future__ import annotations

import importlib.util
from pathlib import Path


QUALIFICATION_SCRIPT = Path(__file__).resolve().parents[2] / "qualification" / "check_downstream.py"
SPEC = importlib.util.spec_from_file_location("check_downstream", QUALIFICATION_SCRIPT)
assert SPEC is not None and SPEC.loader is not None
check_downstream = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_downstream)


def test_actual_sdk_metadata_projects_expected_consumer_constraint_blocks():
    sdk_requirement = check_downstream._mcp_requirement_from_sdk()
    kipilot = check_downstream._constraint_projection(sdk_requirement, "mcp>=1.2.0")
    caid = check_downstream._constraint_projection(sdk_requirement, "mcp>=1.25,<2")
    s32ds = check_downstream._constraint_projection(sdk_requirement, "mcp==1.28.1")

    assert kipilot["classification"] == "constraint_projection"
    assert kipilot["complete_consumer_graph_solved"] is False
    assert kipilot["compatible"] is True
    assert caid["compatible"] is False
    assert s32ds["compatible"] is False


def test_mcp2_api_probe_detects_fastmcp_removal_and_safe_stdio_signature():
    api = check_downstream._mcp_api_probe()

    assert api["mcp_server_exported"] is True
    assert api["legacy_fastmcp_import"] == "blocked_module_removed"
    assert api["run_transport_stdio_keyword_accepted_by_signature"] is True
    assert api["run_invoked"] is False
    assert api["server_started"] is False


def test_public_base_server_protocol_fixture_uses_nested_result_envelope():
    import asyncio

    probe = asyncio.run(check_downstream._in_memory_protocol_probe())

    assert probe["status"] == "passed"
    assert probe["transport"] == "in_memory_client_server"
    assert probe["network_or_external_service"] is False
    assert probe["structured_result_shape"] == "{result: Result envelope}"
    assert probe["envelope_status"] == "OK"
    assert probe["envelope_value"] == 42


def test_report_records_expected_blocks_and_keeps_native_runtime_open():
    report = check_downstream.qualify()

    assert report["overall_verdict"] == "expected_blocks_detected"
    assert report["expected_blocks_detected"] is True
    assert report["full_native_consumer_runtime_qualified"] is False
    assert report["live_server_or_hardware_calls"] is False
