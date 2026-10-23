"""Ölçek vektörleri: statsmodels ile 500+ a priori vektör üretir (KÂHİN DEĞİL).

statsmodels N'yi kesirli verir; G*Power ise güç ≥ hedef koşulunu sağlayan en küçük
tam sayıyı gösterir (LEDGER A3). Bu betik iki değeri yan yana yazar:
  n_frac   : statsmodels'in kesirli çözümü
  n_ceil   : kesirli çözümün yukarı yuvarlanmışı
  n_scan   : scipy ile güç ≥ hedef olan en küçük tam sayı (bağımsız tarama)
n_ceil ile n_scan'in ayrıştığı satırlar ayrıca işaretlenir.

Çıktı: oracle/scale_statsmodels.csv
"""
import csv
import itertools
import math
from pathlib import Path

from scipy.stats import chi2, ncx2
from statsmodels.stats.power import GofChisquarePower

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "oracle" / "scale_statsmodels.csv"

W = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.5]
ALPHA = [0.01, 0.05, 0.10]
POWER = [0.50, 0.80, 0.90, 0.95, 0.99]
DF = [1, 2, 3, 4, 6, 10, 20]


def power(w, a, df, n):
    return ncx2.sf(chi2.isf(a, df), df, w * w * n)


def scan_n(w, a, p, df):
    lo, hi = 1, 1
    while power(w, a, df, hi) < p:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if power(w, a, df, mid) >= p:
            hi = mid
        else:
            lo = mid + 1
    return lo


def main():
    solver = GofChisquarePower()
    rows = []
    for w, a, p, df in itertools.product(W, ALPHA, POWER, DF):
        n_frac = solver.solve_power(effect_size=w, nobs=None, alpha=a, power=p, n_bins=df + 1)
        n_frac = float(n_frac)
        n_scan = scan_n(w, a, p, df)
        if math.isnan(n_frac):
            rows.append({"w": w, "alpha": a, "power": p, "df": df,
                         "n_frac": "", "n_ceil": "", "n_scan": n_scan, "ayni": "statsmodels çözemedi"})
            continue
        n_ceil = math.ceil(n_frac)
        rows.append({
            "w": w, "alpha": a, "power": p, "df": df,
            "n_frac": f"{n_frac:.6f}", "n_ceil": n_ceil, "n_scan": n_scan,
            "ayni": "evet" if n_ceil == n_scan else "HAYIR",
        })
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    diff = [r for r in rows if r["ayni"] == "HAYIR"]
    fail = [r for r in rows if r["ayni"] == "statsmodels çözemedi"]
    print(f"statsmodels çözemedi: {len(fail)} (ör. {fail[:1]})")
    print(f"{len(rows)} vektör yazıldı -> {OUT.relative_to(ROOT)}; n_ceil ≠ n_scan: {len(diff)}")
    for r in diff[:10]:
        print("  ", r)


if __name__ == "__main__":
    main()
