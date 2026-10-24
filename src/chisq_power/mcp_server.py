"""MCP (stdio) adapter for the chi-square contingency power engine (SPEC.md section 6).

A thin adapter: it maps tool arguments onto the same parameter dict the CLI
builds and calls :func:`chisq_power.service.execute`, the same entry point
the CLI uses.  It does no validation or computation of its own, so for the
same input the tool result is the CLI's JSON object, byte for byte.

Run:  gpower-clone-mcp       (speaks MCP over stdin/stdout)
"""
from __future__ import annotations

import sys
from typing import Any, Dict

import anyio
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from . import __version__, service

TOOL_NAME = "chi2_contingency_power"
TEST_NAME = "chi2-contingency"   # the tool is bound to this one test

# Input schema as in SPEC.md section 6.  It is published for clients but
# deliberately NOT enforced by the SDK (no get_tool_input_schema): every
# argument goes to the engine, so errors are the CLI's error objects.
INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "mode": {"type": "string", "enum": ["a-priori", "post-hoc"],
                 "description": "Analysis mode."},
        "w": {"type": "number", "description": "Cohen's effect size w (>= 1e-06)."},
        "alpha": {"type": "number", "description": "Type I error rate, in (1e-07, 1)."},
        "power": {"type": "number",
                  "description": "Target power 1-beta, in (0, 1). Required for a-priori."},
        "n_total": {"type": "integer",
                    "description": "Total sample size, 2..2147483646. Required for post-hoc."},
        "df": {"type": "integer", "description": "Degrees of freedom (integer >= 1)."},
    },
    "required": ["mode", "w", "alpha", "df"],
}

TOOL = types.Tool(
    name=TOOL_NAME,
    title="Chi-square contingency table power analysis",
    description=(
        "Power analysis for the chi-square goodness-of-fit / contingency table test. "
        "a-priori: smallest total N reaching the target power -> "
        "{ncp, critical_chi2, n_total, actual_power}. "
        "post-hoc: power for a given N -> {ncp, critical_chi2, power}. "
        "Invalid input returns {error, code, field} with isError=true. "
        "Values are returned at full double precision (not rounded)."
    ),
    input_schema=INPUT_SCHEMA,
)


def tool_params(arguments: Dict[str, Any] | None) -> Dict[str, Any]:
    """Map MCP tool arguments to the CLI's parameter dict (no checks here).

    ``test`` is implied by the tool; a JSON ``null`` is treated as an absent
    argument.  Any other key is passed through, so the engine reports it
    exactly as the CLI would (e.g. UNKNOWN_PARAM).
    """
    params: Dict[str, Any] = {"test": TEST_NAME}
    for key, value in (arguments or {}).items():
        if value is not None:
            params[key] = value
    return params


def call(arguments: Dict[str, Any] | None) -> types.CallToolResult:
    """Run the tool: shared service entry point -> MCP result."""
    outcome = service.execute(tool_params(arguments))
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=service.to_json(outcome.payload))],
        structured_content=outcome.payload,
        is_error=outcome.is_error,
    )


async def _list_tools(ctx, params) -> types.ListToolsResult:
    return types.ListToolsResult(tools=[TOOL])


async def _call_tool(ctx, params: types.CallToolRequestParams) -> types.CallToolResult:
    if params.name != TOOL_NAME:
        payload = {"error": f"Unknown tool '{params.name}'.", "code": "UNSUPPORTED", "field": None}
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=service.to_json(payload))],
            structured_content=payload, is_error=True)
    return call(params.arguments)


def build_server() -> Server:
    return Server("chisq-power", version=__version__,
                  on_list_tools=_list_tools, on_call_tool=_call_tool)


async def _serve() -> None:
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> int:
    try:
        anyio.run(_serve)
    except KeyboardInterrupt:  # pragma: no cover
        pass
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
