"""Diferansiyel test: CLI'ı (sözleşmeye göre) G*Power oracle vektörlerine karşı çalıştırır.

Motor kodu içermez; yalnızca `gpower-clone` komutunu çağırır ve çıktısını
oracle/chisq_gof.csv ile karşılaştırır. Beklenen değeri G*Power belirler.

Kullanım:
    python tests/test_differential.py                 # oracle (G*Power) vektörleri
    python tests/test_differential.py --scale         # + statsmodels ölçek vektörleri (kâhin değil)
    GPOWER_CLONE="python -m src.cli" python tests/test_differential.py

Kurallar (SPEC.md):
  - n_total TAM eşleşmeli.
  - Ondalık alanlar: mutlak ya da göreli fark ≤ 1e-6.
  - Geçersiz girdi: çıkış kodu 2, stdout'ta {"error","code","field"}.
  - Her çağrı ≤ 2 saniye.
Çıktı: tests/uyum_raporu_cli.md
"""
import csv
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORACLE = ROOT / "oracle" / "chisq_gof.csv"
SCALE = ROOT / "oracle" / "scale_statsmodels.csv"
OUT = ROOT / "tests" / "uyum_raporu_cli.md"
CMD = shlex.split(os.environ.get("GPOWER_CLONE", "gpower-clone"))
TOL = 1e-6
TIME_LIMIT = 2.0

# SPEC.md §2 ve §3'teki kararlar: oracle id -> beklenen hata kodu
EXPECTED_ERROR = {
    "13": "INCONSISTENT",   # power < alpha
    "21": "OUT_OF_RANGE",   # w = 0
    "22": "OUT_OF_RANGE",   # w < 0
    "23": "OUT_OF_RANGE",   # alpha = 0
    "24": "OUT_OF_RANGE",   # alpha = 1
    "25": "OUT_OF_RANGE",   # df = 0
    "26": "OUT_OF_RANGE",   # post-hoc n_total = 0
    "19": "OUT_OF_RANGE",   # S2: post-hoc n_total = 1, sözleşme alt sınırı 2 (G*Power hesaplıyor)
    "27": "INVALID_VALUE",  # S1: df = 1.5, sözleşme tam sayı istiyor (G*Power hesaplıyor)
}
# id 13: w ekranda hata diyaloğunun altında kaldı (CSV'de boş). Vektör planındaki değer (EKSIK_VAKALAR C13) kullanılır;
# beklenen hata power < alpha olduğundan w'den bağımsızdır.
INPUT_OVERRIDE = {"13": {"w": "0.3"}}
AMBIGUOUS = {"12": "S2", "28": "S2"}  # a priori sonuç N = 1: G*Power 1, sözleşme alt sınırı 2
SKIP = {"29", "30"}                  # Determine paneli, sayısal sonuç yok

# Sözleşmedeki örnek vektör (G*Power değeri; scipy ile de doğrulandı)
CONTRACT_EXAMPLE = {
    "id": "K1", "mod": "apriori", "w": "0.3", "alpha": "0.05", "power": "0.95", "df": "5",
    "total_n": "220", "actual_power": "0.9502155", "critical_chi2": "11.0704977", "lambda": "19.8",
}


def run(args):
    t0 = time.perf_counter()
    try:
        p = subprocess.run(CMD + args, capture_output=True, text=True, timeout=10)
    except FileNotFoundError:
        sys.exit(f"CLI bulunamadı: {' '.join(CMD)} (GPOWER_CLONE ortam değişkeniyle ayarlayın)")
    except subprocess.TimeoutExpired:
        return None, None, 10.0
    dt = time.perf_counter() - t0
    out = p.stdout.strip()
    try:
        data = json.loads(out) if out and "\n" not in out else None
    except json.JSONDecodeError:
        data = None
    return p.returncode, data, dt


def close(got, exp):
    if got is None:
        return False
    got, exp = float(got), float(exp)
    return abs(got - exp) <= TOL or abs(got - exp) <= TOL * abs(exp)


def args_for(r):
    w, a, df = r["w"], r["alpha"], r["df"]
    base = ["--test", "chi2-contingency"]
    if r["mod"] == "apriori":
        return base + ["--mode", "a-priori", "--w", w, "--alpha", a, "--power", r["power"], "--df", df]
    return base + ["--mode", "post-hoc", "--w", w, "--alpha", a, "--n_total", r["total_n"], "--df", df]


def check_row(r):
    """(durum, n_eslesti|None, açıklama)"""
    rid = r["id"]
    code, data, dt = run(args_for(r))
    slow = f" (yavaş: {dt:.2f}s)" if dt > TIME_LIMIT else ""
    if code is None:
        return "ZAMAN AŞIMI", False, ""
    if rid in EXPECTED_ERROR:
        want = EXPECTED_ERROR[rid]
        ok = code == 2 and data and data.get("code") == want and "error" in data and "field" in data
        return ("GEÇTİ" if ok and not slow else "KALDI"), None, f"beklenen {want}, gelen kod {code} {data}{slow}"
    if rid in AMBIGUOUS:
        return f"BELİRSİZ ({AMBIGUOUS[rid]})", None, f"kod {code} {data}"
    if code != 0 or not data:
        return "KALDI", False, f"kod {code}, çıktı {data}"
    if r["mod"] == "apriori":
        n_ok = data.get("n_total") == int(r["total_n"])
        checks = {"n_total": n_ok,
                  "actual_power": close(data.get("actual_power"), r["actual_power"]),
                  "critical_chi2": close(data.get("critical_chi2"), r["critical_chi2"]),
                  "ncp": close(data.get("ncp"), r["lambda"])}
    else:
        n_ok = None
        checks = {"power": close(data.get("power"), r["actual_power"]),
                  "critical_chi2": close(data.get("critical_chi2"), r["critical_chi2"]),
                  "ncp": close(data.get("ncp"), r["lambda"])}
    bad = [k for k, v in checks.items() if not v]
    status = "GEÇTİ" if not bad and not slow else "KALDI"
    return status, n_ok, (f"farklı: {', '.join(bad)} → {data}" if bad else "") + slow


def main():
    rows = [r for r in csv.DictReader(ORACLE.open(encoding="utf-8")) if r["id"] not in SKIP]
    for r in rows:
        r.update(INPUT_OVERRIDE.get(r["id"], {}))
    rows.append(CONTRACT_EXAMPLE)
    lines = ["# Diferansiyel test raporu (CLI ↔ G*Power oracle)", "",
             f"Komut: `{' '.join(CMD)}` · tolerans: n_total tam, ondalık ≤ {TOL} (mutlak ya da göreli)", "",
             "| id | mod | durum | not |", "|---|---|---|---|"]
    n_total = n_hit = passed = counted = 0
    for r in rows:
        status, n_ok, note = check_row(r)
        lines.append(f"| {r['id']} | {r['mod']} | {status} | {note} |")
        if not status.startswith("BELİRSİZ"):
            counted += 1
            passed += status == "GEÇTİ"
        if n_ok is not None:
            n_total += 1
            n_hit += n_ok
    rate = 100 * n_hit / n_total if n_total else 0
    lines += ["", f"**Oracle: {passed}/{counted} satır geçti.**",
              f"**N tam eşleşme (kapı ≥ %90): {n_hit}/{n_total} = %{rate:.1f}**"]

    if "--scale" in sys.argv and SCALE.exists():
        srows = list(csv.DictReader(SCALE.open(encoding="utf-8")))
        hit = 0
        for s in srows:
            code, data, _ = run(["--test", "chi2-contingency", "--mode", "a-priori", "--w", s["w"],
                                 "--alpha", s["alpha"], "--power", s["power"], "--df", s["df"]])
            hit += bool(data) and data.get("n_total") == int(s["n_scan"])
        lines += ["", "## Ölçek (statsmodels/scipy — kâhin değil)",
                  f"N eşleşme: {hit}/{len(srows)} = %{100 * hit / len(srows):.1f}"]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    sys.exit(0 if passed == counted else 1)


if __name__ == "__main__":
    main()
