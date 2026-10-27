#!/usr/bin/env python3
"""Bounded MCP 2 downstream qualification for the PR5 candidate.

This checks the installed SDK's public contract, inspects MCP 2 API signatures,
and runs one synthetic in-memory client/server call. It never imports a consumer
checkout, invokes a transport server, or contacts hardware or a network service.

Dependency results are *constraint projections* of the observed consumer MCP
and SDK requirements. They are not complete consumer dependency graph solves.
"""

import asyncio
import importlib
import importlib.metadata as metadata
import importlib.util
import inspect
import json
from typing import Any

from packaging.requirements import Requirement
from packaging.version import Version


CONSUMER_MCP_REQUIREMENTS = {
    "kipilot": "mcp>=1.2.0",
    "caid-mcp": "mcp>=1.25,<2",
    "s32ds-mcp": "mcp==1.28.1",
}


def _mcp_requirement_from_sdk() -> Requirement:
    dist = metadata.distribution("adam-mcp-py")
    for raw in dist.requires or ():
        req = Requirement(raw)
        if req.name.lower().replace("_", "-") == "mcp":
            return req
    raise RuntimeError("adam-mcp-py distribution metadata has no mcp requirement")


def _constraint_projection(sdk_req: Requirement, consumer_text: str) -> dict[str, Any]:
    """Check overlap using installed SDK metadata and the consumer's MCP specifier."""
    consumer_req = Requirement(consumer_text)
    if consumer_req.name.lower() != "mcp":
        raise ValueError(f"Expected an MCP requirement, got {consumer_text!r}")
    sdk_spec = sdk_req.specifier
    consumer_spec = consumer_req.specifier

    # The candidate intentionally pins MCP exactly. Evaluate its one permitted
    # version against the actual downstream MCP specifier.
    exact_versions = [
        Version(spec.version)
        for spec in sdk_spec
        if spec.operator in {"==", "==="} and "*" not in spec.version
    ]
    exact_pin = exact_versions[0] if len(exact_versions) == 1 else None
    compatible = exact_pin is not None and consumer_spec.contains(exact_pin, prereleases=True)

    return {
        "classification": "constraint_projection",
        "complete_consumer_graph_solved": False,
        "consumer_mcp_requirement": consumer_text,
        "sdk_mcp_requirement_from_installed_metadata": str(sdk_req),
        "sdk_exact_mcp_version": str(exact_pin) if exact_pin is not None else None,
        "compatible": compatible,
        "verdict": "compatible_projection" if compatible else "blocked_projection",
    }


async def _in_memory_protocol_probe() -> dict[str, Any]:
    from adam_mcp_py import BaseServer, Result, validates
    from mcp import Client
    from pydantic import BaseModel

    class EchoInput(BaseModel):
        value: int

    server = BaseServer(name="downstream-qualification-fixture")

    @server.tool()
    @validates(EchoInput)
    def echo(input: EchoInput) -> Result[int]:
        return Result.ok(value=input.value * 2, mode_tag="[WORKFLOW:FIXTURE]")

    async with Client(server.mcp_server) as client:
        # The reviewed S32DS pattern exposes the validated model as one input
        # argument, so MCP transports that model under the parameter name.
        response = await client.call_tool("echo", {"input": {"value": 21}})

    structured = response.structured_content
    # MCP 2 structured results nest the SDK Result envelope under "result".
    envelope = structured.get("result") if isinstance(structured, dict) else None
    if not isinstance(envelope, dict):
        raise AssertionError(f"Unexpected MCP 2 structured result shape: {structured!r}")
    if envelope.get("status") != "OK" or envelope.get("value") != 42:
        raise AssertionError(f"Unexpected Result envelope: {envelope!r}")
    return {
        "status": "passed",
        "transport": "in_memory_client_server",
        "network_or_external_service": False,
        "tool_pattern": "BaseServer.tool + validates(Pydantic model) + Result",
        "structured_result_shape": "{result: Result envelope}",
        "envelope_status": envelope["status"],
        "envelope_value": envelope["value"],
        "is_error": bool(response.is_error),
    }


def _mcp_api_probe() -> dict[str, Any]:
    server_api = importlib.import_module("mcp.server")
    mcp_server_cls = getattr(server_api, "MCPServer", None)
    if mcp_server_cls is None:
        raise RuntimeError("Installed mcp.server does not export MCPServer")

    fastmcp_available = importlib.util.find_spec("mcp.server.fastmcp") is not None
    run_signature = inspect.signature(mcp_server_cls.run)
    tool_signature = inspect.signature(mcp_server_cls.tool)
    # Bind the legacy keyword without invoking run() or starting a server.
    run_signature.bind(object(), transport="stdio")

    return {
        "mcp_server_exported": True,
        "fastmcp_module_available": fastmcp_available,
        "legacy_fastmcp_import": "available" if fastmcp_available else "blocked_module_removed",
        "mcp_server_tool_signature": str(tool_signature),
        "mcp_server_run_signature": str(run_signature),
        "run_transport_stdio_keyword_accepted_by_signature": True,
        "run_invoked": False,
        "server_started": False,
    }


def qualify() -> dict[str, Any]:
    sdk_dist = metadata.distribution("adam-mcp-py")
    mcp_version = Version(metadata.version("mcp"))
    sdk_version = sdk_dist.version
    sdk_mcp_req = _mcp_requirement_from_sdk()
    projections = {
        name: _constraint_projection(sdk_mcp_req, requirement)
        for name, requirement in CONSUMER_MCP_REQUIREMENTS.items()
    }

    api = _mcp_api_probe()
    protocol = asyncio.run(_in_memory_protocol_probe())
    fastmcp_absent = not api["fastmcp_module_available"]

    consumers = {
        "kipilot": {
            "dependency_projection": projections["kipilot"],
            "public_sdk_helpers": "not exhaustively exercised here; no BaseServer use in reviewed consumer",
            "native_runtime_verdict": "blocked_mcp2_port_required"
            if fastmcp_absent
            else "needs_consumer_suite",
            "remaining_scope": [
                "port or replace direct mcp.server.fastmcp imports",
                "replace audited FastMCP private _tool_manager/_tools/Tool.fn access",
                "port and qualify low-level mcp.server.Server and stdio code",
                "rerun selected deterministic consumer tests and isolated stdio smoke",
            ],
        },
        "caid-mcp": {
            "dependency_projection": projections["caid-mcp"],
            "direct_adam_mcp_py_consumer": False,
            "native_runtime_verdict": "blocked_mcp2_port_required",
            "remaining_scope": [
                "relax mcp>=1.25,<2 only with an explicit MCP2 migration decision",
                "port or replace FastMCP usage and private _tool_manager/Tool.fn mutation",
                "qualify selected deterministic tests and isolated stdio smoke",
            ],
        },
        "s32ds-mcp": {
            "dependency_projection": projections["s32ds-mcp"],
            "public_sdk_contract_verdict": "passed_fixture"
            if protocol["status"] == "passed"
            else "failed_fixture",
            "native_runtime_verdict": "blocked_dependency_alignment",
            "remaining_scope": [
                "align its exact MCP 1.28.1 and SDK 0.3.2 pins before SDK 0.3.3 adoption",
                "verify Result field behavior and no private BaseServer access",
                "qualify local stdio transport in its isolated environment after port",
            ],
        },
    }

    expected_blocks_detected = (
        projections["kipilot"]["compatible"]
        and not projections["caid-mcp"]["compatible"]
        and not projections["s32ds-mcp"]["compatible"]
    )
    return {
        "schema_version": 1,
        "qualification": "downstream_mcp2_constraint_and_public_contract_projection",
        "overall_verdict": "expected_blocks_detected"
        if expected_blocks_detected
        else "unexpected_constraint_matrix",
        "scope_note": "Constraint projections use installed adam-mcp-py metadata and observed downstream MCP specifiers; they are not complete consumer graph solves.",
        "environment": {
            "adam_mcp_py_version": sdk_version,
            "mcp_version": str(mcp_version),
            "sdk_mcp_requirement": str(sdk_mcp_req),
            "pydantic_version": metadata.version("pydantic"),
        },
        "constraint_projections": projections,
        "mcp2_api_probe": api,
        "public_contract_protocol_probe": protocol,
        "consumers": consumers,
        "expected_blocks_detected": expected_blocks_detected,
        "full_native_consumer_runtime_qualified": False,
        "live_server_or_hardware_calls": False,
    }


if __name__ == "__main__":
    print(json.dumps(qualify(), indent=2, sort_keys=True))
