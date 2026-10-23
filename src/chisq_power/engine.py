"""Calculation engine for chi-square contingency table power analysis.

All computation and input validation live here so that every front end
(CLI today, MCP later) shares exactly the same behaviour.  Front ends only
translate their own syntax into a ``dict`` of raw values and call
:func:`run`.

Definitions (SPEC.md section 2):
  * ncp           = w**2 * N
  * critical_chi2 = upper-alpha point of the central chi2(df) distribution
  * power         = P(X > critical_chi2), X ~ noncentral chi2(df, ncp)
  * a-priori N    = smallest integer N whose power >= target power
"""
from __future__ import annotations

import math
from typing import Any, Dict, Mapping, Optional

# scipy.special is used instead of scipy.stats: same numerics, but importing
# scipy.stats costs ~1 s, which would eat half of the 2 s per-call budget.
from scipy.special import chdtri, chndtr

TEST_NAME = "chi2-contingency"
MODES = ("a-priori", "post-hoc")
UNSUPPORTED_MODES = ("compromise", "criterion", "sensitivity")

# Admissible ranges (SPEC.md sections 3 and 4).
W_MIN_EXCLUSIVE = 1e-6          # S3: w must be greater than 1e-06
ALPHA_MIN_EXCLUSIVE = 1e-7      # S6: alpha in (1e-07, 1)
N_MIN = 2                       # S2: contract lower bound for n_total
N_MAX = 2147483646              # S7: largest admissible sample size

REQUIRED = {
    "a-priori": ("w", "alpha", "power", "df"),
    "post-hoc": ("w", "alpha", "n_total", "df"),
}
ALL_FIELDS = ("test", "mode", "w", "alpha", "power", "n_total", "df")


class EngineError(Exception):
    """Invalid input (exit code 2 in the CLI)."""

    def __init__(self, code: str, field: Optional[str], message: str):
        super().__init__(message)
        self.code = code
        self.field = field
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {"error": self.message, "code": self.code, "field": self.field}


# --------------------------------------------------------------------------
# Core statistics
# --------------------------------------------------------------------------
def noncentrality(w: float, n: int) -> float:
    return w * w * n


def critical_value(alpha: float, df: int) -> float:
    """Upper-alpha point of the central chi-square(df) distribution."""
    return float(chdtri(df, alpha))


def _sf(x: float, df: int, ncp: float) -> float:
    """P(X > x) for X ~ noncentral chi-square(df, ncp)."""
    return float(1.0 - chndtr(x, df, ncp))


def power_at(w: float, alpha: float, df: int, n: int) -> float:
    crit = critical_value(alpha, df)
    return _sf(crit, df, noncentrality(w, n))


def post_hoc(w: float, alpha: float, n_total: int, df: int) -> Dict[str, Any]:
    crit = critical_value(alpha, df)
    ncp = noncentrality(w, n_total)
    return {
        "ncp": ncp,
        "critical_chi2": crit,
        "power": _sf(crit, df, ncp),
    }


def a_priori(w: float, alpha: float, power: float, df: int) -> Dict[str, Any]:
    """Smallest integer N in [N_MIN, N_MAX] with power(N) >= target.

    Power is strictly increasing in N, so an exponential search followed by
    an integer bisection finds the exact minimum without any rounding rule.
    """
    crit = critical_value(alpha, df)

    def pw(n: int) -> float:
        return _sf(crit, df, noncentrality(w, n))

    lo = N_MIN
    if pw(lo) >= power:
        n = lo
    else:
        # Exponential search for an upper bracket: pw(lo) < power <= pw(hi).
        hi = lo * 2
        while True:
            if hi >= N_MAX:
                hi = N_MAX
                if pw(hi) < power:
                    raise EngineError(
                        "NO_SOLUTION", "n_total",
                        f"Required sample size exceeds the maximum of {N_MAX}.")
                break
            if pw(hi) >= power:
                break
            lo, hi = hi, hi * 2
        # Invariant: pw(lo) < power <= pw(hi).
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if pw(mid) >= power:
                hi = mid
            else:
                lo = mid
        n = hi

    ncp = noncentrality(w, n)
    return {
        "ncp": ncp,
        "critical_chi2": crit,
        "n_total": n,
        "actual_power": _sf(crit, df, ncp),
    }


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def _to_float(field: str, raw: Any) -> float:
    if isinstance(raw, bool):
        raise EngineError("INVALID_VALUE", field, f"'{field}' must be a number.")
    if isinstance(raw, (int, float)):
        value = float(raw)
    else:
        text = str(raw).strip()
        try:
            value = float(text)
        except ValueError:
            raise EngineError("INVALID_VALUE", field,
                              f"'{field}' must be a number (decimal separator '.'), got '{raw}'.")
    if not math.isfinite(value):
        raise EngineError("INVALID_VALUE", field, f"'{field}' must be a finite number.")
    return value


def _to_int(field: str, raw: Any) -> int:
    value = _to_float(field, raw)
    if value != math.floor(value):
        raise EngineError("INVALID_VALUE", field, f"'{field}' must be an integer, got '{raw}'.")
    return int(value)


def validate(params: Mapping[str, Any]) -> Dict[str, Any]:
    """Check raw parameters and return typed values.

    ``params`` maps field names (see ALL_FIELDS) to raw values (strings or
    numbers).  Raises :class:`EngineError` on the first problem, checked in
    the order: unknown → missing → test/mode → value syntax → range →
    consistency.
    """
    for key in params:
        if key not in ALL_FIELDS:
            raise EngineError("UNKNOWN_PARAM", key, f"Unknown parameter '{key}'.")

    for key in ("test", "mode"):
        if key not in params:
            raise EngineError("MISSING_PARAM", key, f"Missing required parameter '{key}'.")

    test = str(params["test"]).strip()
    if test != TEST_NAME:
        raise EngineError("UNSUPPORTED", "test",
                          f"Test '{test}' is not supported; only '{TEST_NAME}' is available.")

    mode = str(params["mode"]).strip()
    if mode in UNSUPPORTED_MODES:
        raise EngineError("UNSUPPORTED", "mode",
                          f"Mode '{mode}' is not supported in this version.")
    if mode not in MODES:
        raise EngineError("INVALID_VALUE", "mode",
                          f"Mode must be one of {', '.join(MODES)}, got '{mode}'.")

    required = REQUIRED[mode]
    for key in params:
        if key not in ("test", "mode") and key not in required:
            raise EngineError("UNKNOWN_PARAM", key,
                              f"Parameter '{key}' is not used in mode '{mode}'.")
    for key in required:
        if key not in params:
            raise EngineError("MISSING_PARAM", key, f"Missing required parameter '{key}'.")

    # Syntax (type) checks, in field order.
    typed: Dict[str, Any] = {"test": test, "mode": mode}
    for key in required:
        if key in ("df", "n_total"):
            typed[key] = _to_int(key, params[key])
        else:
            typed[key] = _to_float(key, params[key])

    # Range checks.
    w = typed["w"]
    if not w > W_MIN_EXCLUSIVE:
        raise EngineError("OUT_OF_RANGE", "w", "Effect size w must be greater than 1e-06.")
    alpha = typed["alpha"]
    if not (ALPHA_MIN_EXCLUSIVE < alpha < 1):
        raise EngineError("OUT_OF_RANGE", "alpha",
                          "Alpha is outside the admissible range (1e-07, 1).")
    if mode == "a-priori":
        power = typed["power"]
        if not (0 < power < 1):
            raise EngineError("OUT_OF_RANGE", "power",
                              "Power is outside the admissible range (0, 1).")
    else:
        n_total = typed["n_total"]
        if not (N_MIN <= n_total <= N_MAX):
            raise EngineError("OUT_OF_RANGE", "n_total",
                              f"Total sample size is outside the admissible range [{N_MIN}, {N_MAX}].")
    if typed["df"] < 1:
        raise EngineError("OUT_OF_RANGE", "df", "Degrees of freedom must be greater or equal one.")

    # Consistency checks.
    if mode == "a-priori" and typed["power"] < alpha:
        raise EngineError("INCONSISTENT", "power", "Power must be greater than or equal to alpha.")

    return typed


def run(params: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate ``params`` and compute the result for the requested mode."""
    p = validate(params)
    if p["mode"] == "a-priori":
        return a_priori(p["w"], p["alpha"], p["power"], p["df"])
    return post_hoc(p["w"], p["alpha"], p["n_total"], p["df"])
