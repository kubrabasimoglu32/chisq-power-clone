"""SPEC.md section 3 Gherkin scenarios as pytest tests.

Every scenario drives the real CLI in a subprocess (Background: the CLI is
called as "gpower-clone --test chi2-contingency").  The minimality scenario
additionally evaluates power at N-1 through the engine.
"""
import json
import math
import shutil
import subprocess
import sys

import pytest

from chisq_power import engine

TOL = 1e-6
_EXE = shutil.which("gpower-clone")
BASE = ([_EXE] if _EXE else [sys.executable, "-m", "chisq_power.cli"]) + ["--test", "chi2-contingency"]


def cli(*args):
    p = subprocess.run(BASE + [str(a) for a in args], capture_output=True, text=True, timeout=10)
    lines = p.stdout.splitlines()
    assert len(lines) == 1, f"stdout must be exactly one line: {p.stdout!r}"
    return p.returncode, json.loads(lines[0]), p.stdout


def apriori(w, alpha, power, df):
    return cli("--mode", "a-priori", "--w", w, "--alpha", alpha, "--power", power, "--df", df)


def posthoc(w, alpha, n, df):
    return cli("--mode", "post-hoc", "--w", w, "--alpha", alpha, "--n_total", n, "--df", df)


def approx(got, exp):
    return abs(got - exp) <= TOL or abs(got - exp) <= TOL * abs(exp)


# --- Scenario Outline: A priori örneklem büyüklüğü --------------------------
APRIORI = [
    # id, w, alpha, power, df, n_total, actual_power, critical_chi2, ncp
    (1, "0.3", "0.05", "0.80", 1, 88, 0.8035275, 3.8414588, 7.92),
    (2, "0.3", "0.05", "0.80", 2, 108, 0.8036939, 5.9914645, 9.72),
    (3, "0.3", "0.05", "0.80", 4, 133, 0.8013043, 9.4877290, 11.97),
    (4, "0.1", "0.05", "0.80", 1, 785, 0.8000569, 3.8414588, 7.85),
    (5, "0.5", "0.05", "0.80", 1, 32, 0.8074304, 3.8414588, 8.0),
    (6, "0.3", "0.05", "0.95", 3, 191, 0.9502399, 7.8147279, 17.19),
    (7, "0.3", "0.01", "0.90", 5, 245, 0.9003979, 15.0862725, 22.05),
    (8, "0.3", "0.05", "0.80", 10, 181, 0.8014702, 18.3070381, 16.29),
    (9, "0.3", "0.05", "0.80", 50, 336, 0.8006734, 67.5048065, 30.24),
    (10, "0.01", "0.05", "0.80", 1, 78489, 0.8000020, 3.8414588, 7.8489),
    (11, "2", "0.05", "0.80", 1, 2, 0.8074304, 3.8414588, 8.0),
]


@pytest.mark.parametrize("row", APRIORI, ids=[f"id{r[0]}" for r in APRIORI])
def test_apriori_sample_size(row):
    _, w, alpha, power, df, n, ap, crit, ncp = row
    code, data, out = apriori(w, alpha, power, df)
    assert code == 0
    assert out.endswith("\n") and out.count("\n") == 1
    assert set(data) == {"ncp", "critical_chi2", "n_total", "actual_power"}
    assert isinstance(data["n_total"], int) and data["n_total"] == n
    assert approx(data["actual_power"], ap)
    assert approx(data["critical_chi2"], crit)
    assert approx(data["ncp"], ncp)


# --- Scenario Outline: Post hoc güç -----------------------------------------
POSTHOC = [
    # id, w, alpha, n_total, df, power, critical_chi2, ncp
    (15, "0.3", "0.05", 88, 1, 0.8035275, 3.8414588, 7.92),
    (16, "0.3", "0.05", 50, 2, 0.4604212, 5.9914645, 4.5),
    (17, "0.5", "0.05", 10, 1, 0.3526081, 3.8414588, 2.5),
    (18, "0.1", "0.05", 100, 1, 0.1700750, 3.8414588, 1.0),
    (20, "0.3", "0.01", 200, 3, 0.8732131, 11.3448667, 18.0),
]


@pytest.mark.parametrize("row", POSTHOC, ids=[f"id{r[0]}" for r in POSTHOC])
def test_posthoc_power(row):
    _, w, alpha, n, df, power, crit, ncp = row
    code, data, _ = posthoc(w, alpha, n, df)
    assert code == 0
    assert set(data) == {"ncp", "critical_chi2", "power"}
    assert approx(data["power"], power)
    assert approx(data["critical_chi2"], crit)
    assert approx(data["ncp"], ncp)


# --- Scenario: Noncentrality parametresi w² × N'dir --------------------------
@pytest.mark.parametrize("mode,args,w,n", [
    ("a-priori", ("0.1", "0.05", "0.80", 1), 0.1, 785),   # id 4
    ("post-hoc", ("0.3", "0.01", 200, 3), 0.3, 200),      # id 20
    ("post-hoc", ("0.7", "0.05", 37, 2), 0.7, 37),
])
def test_ncp_is_w_squared_times_n(mode, args, w, n):
    code, data, _ = (apriori if mode == "a-priori" else posthoc)(*args)
    assert code == 0
    n_used = data["n_total"] if mode == "a-priori" else n
    assert n_used == n
    assert math.isclose(data["ncp"], w * w * n_used, rel_tol=1e-12)


# --- Scenario: Kritik değer yalnızca α ve df'ye bağlıdır ---------------------
def test_critical_value_depends_only_on_alpha_df():
    calls = [apriori("0.3", "0.05", "0.80", 1), apriori("0.1", "0.05", "0.80", 1),
             apriori("0.5", "0.05", "0.80", 1), apriori("0.01", "0.05", "0.80", 1),
             apriori("2", "0.05", "0.80", 1), posthoc("0.3", "0.05", 88, 1),
             posthoc("0.5", "0.05", 10, 1), posthoc("0.1", "0.05", 100, 1)]
    crits = {c[1]["critical_chi2"] for c in calls}
    assert all(c[0] == 0 for c in calls)
    assert len(crits) == 1
    assert approx(crits.pop(), 3.8414588)


# --- Scenario: A priori N en küçük tam sayıdır; kat kuralı yoktur -------------
@pytest.mark.parametrize("w,alpha,power,df,n", [
    (0.3, 0.05, 0.80, 4, 133), (0.3, 0.05, 0.95, 3, 191), (0.01, 0.05, 0.80, 1, 78489),
])
def test_apriori_n_is_minimal_no_multiple_rule(w, alpha, power, df, n):
    code, data, _ = apriori(w, alpha, power, df)
    assert code == 0 and data["n_total"] == n
    assert engine.power_at(w, alpha, df, n) >= power
    assert engine.power_at(w, alpha, df, n - 1) < power
    # 133, 191 and 78489 are not multiples of the cell count (df + 1)
    assert n % (df + 1) != 0


# --- Scenario: A priori ve post hoc tutarlıdır --------------------------------
def test_apriori_posthoc_consistent():
    c1, a, _ = apriori("0.3", "0.05", "0.80", 1)
    c2, p, _ = posthoc("0.3", "0.05", a["n_total"], 1)
    assert c1 == c2 == 0
    assert a["n_total"] == 88
    assert p["power"] == a["actual_power"]
    assert approx(p["power"], 0.8035275)


# --- Scenario: w > 1 kabul edilir ---------------------------------------------
def test_w_greater_than_one_accepted():
    code, data, _ = apriori("2", "0.05", "0.80", 1)
    assert code == 0 and data["n_total"] == 2


# --- Scenario: Deterministik çıktı --------------------------------------------
def test_deterministic_output():
    out1 = apriori("0.1", "0.05", "0.80", 1)[2]   # id 4
    out2 = apriori("0.1", "0.05", "0.80", 1)[2]   # id 14
    assert out1 == out2


# --- Scenario Outline: Geçersiz girdi reddedilir --------------------------------
VALID_APRIORI = {"w": "0.3", "alpha": "0.05", "power": "0.80", "df": "1"}
VALID_POSTHOC = {"w": "0.3", "alpha": "0.05", "n_total": "88", "df": "1"}
INVALID = [
    ("21", "a-priori", "w", "0", "OUT_OF_RANGE"),
    ("22", "a-priori", "w", "-0.3", "OUT_OF_RANGE"),
    ("23", "a-priori", "alpha", "0", "OUT_OF_RANGE"),
    ("24", "a-priori", "alpha", "1", "OUT_OF_RANGE"),
    ("25", "a-priori", "df", "0", "OUT_OF_RANGE"),
    ("26", "post-hoc", "n_total", "0", "OUT_OF_RANGE"),
    ("X05", "a-priori", "power", "1", "OUT_OF_RANGE"),
    # SPEC section 4 decisions
    ("S1", "a-priori", "df", "1.5", "INVALID_VALUE"),
    ("S2", "post-hoc", "n_total", "1", "OUT_OF_RANGE"),
    ("S3", "a-priori", "w", "1e-06", "OUT_OF_RANGE"),
    ("S6", "a-priori", "alpha", "1e-07", "OUT_OF_RANGE"),
]


@pytest.mark.parametrize("oid,mode,field,value,want", INVALID, ids=[r[0] for r in INVALID])
def test_invalid_input_rejected(oid, mode, field, value, want):
    params = dict(VALID_APRIORI if mode == "a-priori" else VALID_POSTHOC)
    params[field] = value
    args = ["--mode", mode]
    for k, v in params.items():
        args += [f"--{k}", v]
    code, data, _ = cli(*args)
    assert code == 2
    assert set(data) == {"error", "code", "field"}
    assert data["code"] == want and data["field"] == field
    assert isinstance(data["error"], str) and data["error"]


# --- Scenario: Hedef güç α'dan küçük ------------------------------------------
def test_power_below_alpha_inconsistent():
    code, data, _ = apriori("0.3", "0.05", "0.04", 1)
    assert code == 2
    assert data["code"] == "INCONSISTENT" and data["field"] == "power"


# --- Scenario Outline: Eksik, bilinmeyen ya da bozuk bayrak ---------------------
@pytest.mark.parametrize("args,want", [
    (["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.8"], "MISSING_PARAM"),
    (["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.8", "--df", "1",
      "--ratio", "1"], "UNKNOWN_PARAM"),
    (["--mode", "a-priori", "--w", "abc", "--alpha", "0.05", "--power", "0.8", "--df", "1"],
     "INVALID_VALUE"),
], ids=["missing-df", "unknown-ratio", "bad-w"])
def test_missing_unknown_malformed_flag(args, want):
    code, data, _ = cli(*args)
    assert code == 2 and data["code"] == want


# --- SPEC section 4 provisional decisions (not Gherkin, recorded here) ---------
def test_s5_other_modes_unsupported():
    code, data, _ = cli("--mode", "compromise", "--w", "0.3", "--alpha", "0.05", "--df", "1")
    assert code == 2 and data["code"] == "UNSUPPORTED" and data["field"] == "mode"


def test_s7_n_beyond_limit_no_solution():
    code, data, _ = apriori("0.00001", "0.05", "0.80", 1)
    assert code == 2 and data["code"] == "NO_SOLUTION" and data["field"] == "n_total"


def test_s2_apriori_never_below_contract_minimum():
    # G*Power returns N = 1 here (oracle id 12, 28); the contract minimum is 2.
    for power in ("0.06", "0.05"):
        code, data, _ = apriori("0.3", "0.05", power, 1)
        assert code == 0 and data["n_total"] == 2
