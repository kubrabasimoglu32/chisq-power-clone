"""SPEC.md section 6: the MCP adapter returns exactly what the CLI returns.

(a) CLI (subprocess) == MCP tool result for every numeric and error row of
    oracle/chisq_gof.csv, the section 6 examples and contract edge cases.
(b) A real MCP client (SDK ClientSession + stdio_client) spawns
    ``gpower-clone-mcp`` and calls list_tools / call_tool.
(c) Architecture: the MCP layer contains no statistics of its own.
"""
import ast
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import anyio
import pytest

from chisq_power import mcp_server

ROOT = Path(__file__).resolve().parent.parent
ORACLE = ROOT / "oracle" / "chisq_gof.csv"
PKG = ROOT / "src" / "chisq_power"

_CLI = shutil.which("gpower-clone")
CLI = [_CLI] if _CLI else [sys.executable, "-m", "chisq_power.cli"]
_MCP = shutil.which("gpower-clone-mcp")


def run_cli(args):
    p = subprocess.run(CLI + ["--test", "chi2-contingency"] + args,
                       capture_output=True, text=True, timeout=10)
    assert p.stdout.count("\n") == 1, p.stdout
    return p.returncode, p.stdout.rstrip("\n")


def json_number(text):
    """How a JSON client would send a CSV value: integer when integral, else number."""
    value = float(text)
    return int(value) if value.is_integer() and "." not in text and "e" not in text.lower() else value


def case_from_oracle(r):
    """-> (cli_args, mcp_arguments) for one oracle row (as in tests/test_differential.py)."""
    w = r["w"] or "0.3"   # id 13: w hidden under the dialog; planned value 0.3
    mode = "a-priori" if r["mod"] == "apriori" else "post-hoc"
    cli = ["--mode", mode, "--w", w, "--alpha", r["alpha"], "--df", r["df"]]
    args = {"mode": mode, "w": json_number(w), "alpha": json_number(r["alpha"]),
            "df": json_number(r["df"])}
    if mode == "a-priori":
        cli += ["--power", r["power"]]
        args["power"] = json_number(r["power"])
    else:
        cli += ["--n_total", r["total_n"]]
        args["n_total"] = json_number(r["total_n"])
    return cli, args


ORACLE_CASES = [(f"oracle-{r['id']}",) + case_from_oracle(r)
                for r in csv.DictReader(ORACLE.open(encoding="utf-8"))
                if r["mod"] in ("apriori", "posthoc")]

SPEC6_CASES = [
    ("spec6-contract-N220",
     ["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.95", "--df", "5"],
     {"mode": "a-priori", "w": 0.3, "alpha": 0.05, "power": 0.95, "df": 5}),
    ("spec6-posthoc-88",
     ["--mode", "post-hoc", "--w", "0.3", "--alpha", "0.05", "--n_total", "88", "--df", "1"],
     {"mode": "post-hoc", "w": 0.3, "alpha": 0.05, "n_total": 88, "df": 1}),
    ("spec6-w0-OUT_OF_RANGE",
     ["--mode", "a-priori", "--w", "0", "--alpha", "0.05", "--power", "0.80", "--df", "1"],
     {"mode": "a-priori", "w": 0, "alpha": 0.05, "power": 0.80, "df": 1}),
    ("spec6-power-INCONSISTENT",
     ["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.04", "--df", "1"],
     {"mode": "a-priori", "w": 0.3, "alpha": 0.05, "power": 0.04, "df": 1}),
]

CONTRACT_CASES = [
    ("missing-df",
     ["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.8"],
     {"mode": "a-priori", "w": 0.3, "alpha": 0.05, "power": 0.8}),
    ("unknown-ratio",
     ["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.8", "--df", "1", "--ratio", "1"],
     {"mode": "a-priori", "w": 0.3, "alpha": 0.05, "power": 0.8, "df": 1, "ratio": 1}),
    ("bad-w",
     ["--mode", "a-priori", "--w", "abc", "--alpha", "0.05", "--power", "0.8", "--df", "1"],
     {"mode": "a-priori", "w": "abc", "alpha": 0.05, "power": 0.8, "df": 1}),
    ("unsupported-mode",
     ["--mode", "compromise", "--w", "0.3", "--alpha", "0.05", "--df", "1"],
     {"mode": "compromise", "w": 0.3, "alpha": 0.05, "df": 1}),
    ("internal-error-huge-df",
     ["--mode", "post-hoc", "--w", "0.3", "--alpha", "0.05", "--n_total", "100", "--df", "1000000000000"],
     {"mode": "post-hoc", "w": 0.3, "alpha": 0.05, "n_total": 100, "df": 1000000000000}),
]

ALL_CASES = ORACLE_CASES + SPEC6_CASES + CONTRACT_CASES


def test_case_counts():
    # 29 oracle rows (31 minus the 2 Determine-panel rows) + 4 section 6 examples + 5 contract cases
    assert len(ORACLE_CASES) == 29 and len(ALL_CASES) == 38


# --- (a) CLI == MCP -------------------------------------------------------------
@pytest.mark.parametrize("name,cli_args,mcp_args", ALL_CASES, ids=[c[0] for c in ALL_CASES])
def test_cli_equals_mcp(name, cli_args, mcp_args):
    code, cli_line = run_cli(cli_args)
    res = mcp_server.call(mcp_args)
    assert res.content[0].text == cli_line                     # byte-identical JSON text
    assert res.structured_content == json.loads(cli_line)      # same object
    assert res.is_error == (code != 0)
    if code != 0:
        assert set(res.structured_content) == {"error", "code", "field"}


# --- (b) real stdio client --------------------------------------------------------
async def _session_calls(calls):
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    server = StdioServerParameters(command=_MCP) if _MCP else \
        StdioServerParameters(command=sys.executable, args=["-m", "chisq_power.mcp_server"])
    with anyio.fail_after(60):
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                results = [await session.call_tool(mcp_server.TOOL_NAME, args) for args in calls]
    return tools, results


def test_real_stdio_client():
    picks = [SPEC6_CASES[0], SPEC6_CASES[1], SPEC6_CASES[2], SPEC6_CASES[3],
             next(c for c in ORACLE_CASES if c[0] == "oracle-31")]
    tools, results = anyio.run(_session_calls, [c[2] for c in picks])
    assert [t.name for t in tools.tools] == [mcp_server.TOOL_NAME]
    schema = tools.tools[0].input_schema
    assert set(schema["properties"]) == {"mode", "w", "alpha", "power", "n_total", "df"}
    assert schema["properties"]["n_total"]["type"] == "integer"
    assert schema["properties"]["df"]["type"] == "integer"
    assert set(schema["required"]) == {"mode", "w", "alpha", "df"}
    for (name, cli_args, _), res in zip(picks, results):
        code, cli_line = run_cli(cli_args)
        assert res.content[0].text == cli_line, name
        assert res.structured_content == json.loads(cli_line), name
        assert bool(res.is_error) == (code != 0), name


# --- (c) architecture: no statistics outside the engine ------------------------------
def _imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            names |= {f"{'.' * node.level}{mod}:{a.name}" for a in node.names}
            names.add("." * node.level + mod)
    return names, tree


FORBIDDEN = ("scipy", "numpy", "math", "statistics", "statsmodels")


@pytest.mark.parametrize("module", ["mcp_server.py", "cli.py", "service.py"])
def test_front_ends_do_no_math(module):
    names, tree = _imports(PKG / module)
    assert not [n for n in names if n.split(".")[0].split(":")[0] in FORBIDDEN], names
    # no references to the engine's numeric helpers
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not attrs & {"a_priori", "post_hoc", "power_at", "critical_value", "noncentrality",
                        "_sf", "validate"}, attrs


def test_mcp_goes_through_shared_entry_point_only():
    names, tree = _imports(PKG / "mcp_server.py")
    assert ".:service" in names
    assert ".:engine" not in names and ".engine" not in names   # never talks to the engine directly
    calls = {f"{n.func.value.id}.{n.func.attr}" for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and isinstance(n.func.value, ast.Name)}
    assert "service.execute" in calls
    # the CLI uses the very same entry point
    _, cli_tree = _imports(PKG / "cli.py")
    cli_calls = {f"{n.func.value.id}.{n.func.attr}" for n in ast.walk(cli_tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and isinstance(n.func.value, ast.Name)}
    assert "service.execute" in cli_calls


def test_scipy_only_in_engine():
    users = [p.name for p in PKG.glob("*.py") if "scipy" in p.read_text(encoding="utf-8")
             and any(l.lstrip().startswith(("import scipy", "from scipy"))
                     for l in p.read_text(encoding="utf-8").splitlines())]
    assert users == ["engine.py"]
