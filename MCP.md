# MCP server: `gpower-clone-mcp`

A thin Model Context Protocol adapter over the same engine as the
`gpower-clone` CLI (SPEC.md §6). It does no computation or validation of its
own: tool arguments go to `chisq_power.service.execute`, the same entry
point the CLI calls. For the same input, the tool result is the CLI's JSON
object, byte for byte.

## Running

```bash
pip install --break-system-packages -e .   # installs gpower-clone and gpower-clone-mcp
gpower-clone-mcp                           # speaks MCP over stdin/stdout (stdio transport)
```

Without installing: `python -m chisq_power.mcp_server` (with `src/` on `PYTHONPATH`).
Requires Python ≥ 3.10 and the official `mcp` SDK (≥ 2.3; a regular dependency).

## Tool: `chi2_contingency_power`

### Input

| field | type | required | meaning |
|---|---|---|---|
| `mode` | string, `"a-priori"` \| `"post-hoc"` | yes | analysis mode |
| `w` | number | yes | Cohen's w (≥ 1e-06) |
| `alpha` | number | yes | type I error, in (1e-07, 1) |
| `power` | number | in a-priori | target power 1−β, in (0, 1), ≥ alpha |
| `n_total` | integer | in post-hoc | total sample size, 2 … 2147483646 |
| `df` | integer | yes | degrees of freedom, integer ≥ 1 |

The schema is published in `tools/list` but is **not enforced by the SDK**.
Every argument goes to the engine, so an invalid value (e.g. `df: 1.5`,
`w: "abc"`, an extra `ratio`) gets the same error object as the CLI would
give. A JSON `null` counts as an absent argument. The test
(`chi2-contingency`) is implied by the tool name.

### Output

A successful call returns `isError: false`. `structuredContent` holds the
result object, and `content[0].text` holds its one-line JSON, the same text
the CLI writes to stdout:

| mode | fields |
|---|---|
| a-priori | `ncp`, `critical_chi2`, `n_total` (integer), `actual_power` |
| post-hoc | `ncp`, `critical_chi2`, `power` |

Values are full double precision, never rounded.

```json
{"ncp": 19.8, "critical_chi2": 11.070497693516355, "n_total": 220, "actual_power": 0.9502155018970163}
```

### Errors

A failed call returns `isError: true`. `structuredContent` and
`content[0].text` hold the CLI's error object:

```json
{"error": "Effect size w must be greater than or equal to 1e-06.", "code": "OUT_OF_RANGE", "field": "w"}
```

Codes: `MISSING_PARAM`, `UNKNOWN_PARAM`, `INVALID_VALUE`, `OUT_OF_RANGE`,
`INCONSISTENT`, `UNSUPPORTED`, `NO_SOLUTION`. On a numerical failure
(CLI exit code 1), the code is `INTERNAL`, with `field: null`.

## Claude Desktop configuration

Add this to `claude_desktop_config.json`. Use the absolute path from
`which gpower-clone-mcp` if the app's PATH does not include it:

```json
{
  "mcpServers": {
    "chisq-power": {
      "command": "gpower-clone-mcp",
      "args": []
    }
  }
}
```

Without the console script:

```json
{
  "mcpServers": {
    "chisq-power": {
      "command": "python3",
      "args": ["-m", "chisq_power.mcp_server"],
      "env": {"PYTHONPATH": "/home/claude/klon-oturum2/src"}
    }
  }
}
```

## Tests

`tests/test_mcp.py`:

- **CLI ≡ MCP:** 38 cases. They cover all 29 numeric and error rows of
  `oracle/chisq_gof.csv`, the 4 §6 examples, and 5 contract edge cases.
- **Real stdio client:** the SDK's `ClientSession` with `stdio_client`.
- **Architecture:** no scipy or math outside `engine.py`; the CLI and MCP
  both go through `service.execute`.
