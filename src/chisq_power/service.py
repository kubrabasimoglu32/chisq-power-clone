"""Single front-end entry point: raw parameters -> (status, JSON object).

Both the CLI and the MCP server call :func:`execute` and serialise with
:func:`to_json`, so for the same input they produce byte-identical JSON.
Validation and computation stay in :mod:`chisq_power.engine`; this module
only maps outcomes (result / input error / internal error) to objects.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, Mapping, NamedTuple

from . import engine

OK, INTERNAL, INVALID = 0, 1, 2   # same numbers as the CLI exit codes


class Outcome(NamedTuple):
    status: int                   # OK, INVALID or INTERNAL
    payload: Dict[str, Any]       # result object or {"error","code","field"}

    @property
    def is_error(self) -> bool:
        return self.status != OK


def execute(params: Mapping[str, Any]) -> Outcome:
    """Run the engine on raw ``params`` (strings or JSON numbers)."""
    try:
        result = engine.run(params)
        to_json(result)           # fail here (not later) if a value is not JSON-safe
        return Outcome(OK, result)
    except engine.EngineError as exc:
        return Outcome(INVALID, exc.to_dict())
    except engine.NumericalError as exc:
        print(f"internal error: {exc}", file=sys.stderr)
        return Outcome(INTERNAL, {"error": str(exc), "code": "INTERNAL", "field": None})
    except Exception as exc:  # pragma: no cover - defensive
        print(f"internal error: {exc!r}", file=sys.stderr)
        return Outcome(INTERNAL, {"error": "Internal error.", "code": "INTERNAL", "field": None})


def to_json(obj: Mapping[str, Any]) -> str:
    """The one-line JSON text written by every front end."""
    return json.dumps(obj, allow_nan=False)
