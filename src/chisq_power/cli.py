"""Thin command-line front end for :mod:`chisq_power.engine`.

Usage (SPEC.md section 1):
  gpower-clone --test chi2-contingency --mode a-priori --w W --alpha A --power P --df DF
  gpower-clone --test chi2-contingency --mode post-hoc --w W --alpha A --n_total N --df DF

stdout carries exactly one JSON line (result or error); anything else goes
to stderr.  Exit codes: 0 success, 2 invalid input, 1 internal error.
"""
from __future__ import annotations

import json
import sys
from typing import Dict, List, Optional

from . import engine

USAGE = (
    "usage: gpower-clone --test chi2-contingency --mode a-priori "
    "--w W --alpha A --power P --df DF\n"
    "       gpower-clone --test chi2-contingency --mode post-hoc "
    "--w W --alpha A --n_total N --df DF"
)

EXIT_OK, EXIT_INTERNAL, EXIT_INVALID = 0, 1, 2


def _emit(obj: Dict) -> None:
    sys.stdout.write(json.dumps(obj, allow_nan=False) + "\n")
    sys.stdout.flush()


def parse_args(argv: List[str]) -> Dict[str, str]:
    """Turn ``--name value`` / ``--name=value`` tokens into a raw dict.

    Only syntax is checked here; which names are allowed and what values
    mean is decided by the engine.
    """
    params: Dict[str, str] = {}
    i = 0
    while i < len(argv):
        tok = argv[i]
        if not tok.startswith("--") or len(tok) == 2:
            raise engine.EngineError("INVALID_VALUE", None, f"Unexpected argument '{tok}'.")
        name, eq, value = tok[2:].partition("=")
        if not eq:
            if i + 1 >= len(argv) or (argv[i + 1].startswith("--") and len(argv[i + 1]) > 2):
                field = name if name in engine.ALL_FIELDS else None
                if field is None:
                    raise engine.EngineError("UNKNOWN_PARAM", name, f"Unknown parameter '{name}'.")
                raise engine.EngineError("MISSING_PARAM", name, f"Flag '--{name}' needs a value.")
            value = argv[i + 1]
            i += 2
        else:
            i += 1
        if name not in engine.ALL_FIELDS:
            raise engine.EngineError("UNKNOWN_PARAM", name, f"Unknown parameter '{name}'.")
        if name in params:
            raise engine.EngineError("INVALID_VALUE", name, f"Flag '--{name}' given more than once.")
        params[name] = value
    return params


def main(argv: Optional[List[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv in (["-h"], ["--help"]):
        print(USAGE, file=sys.stderr)
        return EXIT_OK
    try:
        result = engine.run(parse_args(argv))
    except engine.EngineError as exc:
        _emit(exc.to_dict())
        return EXIT_INVALID
    except Exception as exc:  # pragma: no cover - defensive
        print(f"internal error: {exc!r}", file=sys.stderr)
        _emit({"error": "Internal error.", "code": "INTERNAL", "field": None})
        return EXIT_INTERNAL
    _emit(result)
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
