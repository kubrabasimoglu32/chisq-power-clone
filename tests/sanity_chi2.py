"""Bağımsız sanity kontrolü (kâhin DEĞİL). oracle/chisq_gof.csv -> tests/uyum_raporu.md

λ = w²·N, kritik = chi2.isf(α, df), güç = ncx2.sf(kritik, df, λ).
G*Power değeri her zaman geçerlidir; farklar yalnızca raporlanır.
"""
import csv
from pathlib import Path
from scipy.stats import chi2, ncx2

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "oracle" / "chisq_gof.csv"
OUT = ROOT / "tests" / "uyum_raporu.md"


def power(w, a, df, n):
    return ncx2.sf(chi2.isf(a, df), df, w * w * n)


def apriori_n(w, a, p, df, n_max=10**16):
    lo, hi = 1, 1
    while power(w, a, df, hi) < p:
        hi *= 2
        if hi > n_max:
            return None
    while lo < hi:
        mid = (lo + hi) // 2
        if power(w, a, df, mid) >= p:
            hi = mid
        else:
            lo = mid + 1
    return lo


def decimals(s):
    return len(s.split(".")[1]) if "." in s else 0


def main():
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    lines = ["# Uyum raporu (scipy sanity — kâhin değil)", "",
             "| id | mod | G*Power | scipy | fark | durum |", "|---|---|---|---|---|---|"]
    fark = []
    for r in rows:
        if r["mod"] == "determine":
            lines.append(f"| {r['id']} | determine | panel | — | — | KARŞILAŞTIRILMADI (w hesaplanmamış) |")
            continue
        if not r["total_n"] or (r["total_n"] and not r["actual_power"]):
            lines.append(f"| {r['id']} | {r['mod']} | Input error | — | — | GİRDİ HATASI (oracle; karşılaştırılmadı) |")
            continue
        try:
            w, a, df = float(r["w"]), float(r["alpha"]), float(r["df"])
            if r["mod"] == "apriori":
                s = apriori_n(w, a, float(r["power"]), df)
                if "e" in r["total_n"]:  # ekran büyük N'yi %.5g gösteriyor
                    g = r["total_n"]
                    ok = s is not None and f"{s:.5g}" == f"{float(g):.5g}"
                    d = "—" if ok else "≠"
                    gs, ss = g, f"{s} (≈{s:.5g})"
                else:
                    g = int(float(r["total_n"]))
                    d = None if s is None else s - g
                    ok = d == 0
                    gs, ss = str(g), str(s)
            else:
                g_str = r["actual_power"]
                g = float(g_str)
                s = round(power(w, a, df, int(float(r["total_n"]))), decimals(g_str))
                d = round(s - g, 10)
                ok = d == 0
                gs, ss = g_str, str(s)
        except (ValueError, KeyError) as e:
            lines.append(f"| {r.get('id')} | {r.get('mod')} | — | — | — | OKUNAMADI ({e}) |")
            continue
        durum = "EŞLEŞTİ" if ok else "FARK"
        if not ok:
            fark.append(r["id"])
        lines.append(f"| {r['id']} | {r['mod']} | {gs} | {ss} | {d} | {durum} |")
    lines += ["", f"Toplam: {len(rows)} satır, FARK: {len(fark)}", "",
              "## Ayrıntı: λ, kritik χ², actual power (G*Power / scipy, 7 basamak)", "",
              "| id | λ G*P | λ scipy | krit G*P | krit scipy | güç G*P | güç scipy | N−1 güç (scipy) | hedef |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if not r["actual_power"]:
            continue
        w, a, df = float(r["w"]), float(r["alpha"]), float(r["df"])
        n = apriori_n(w, a, float(r["power"]), df) if "e" in r["total_n"] else int(float(r["total_n"]))
        c = chi2.isf(a, df)
        lines.append(f"| {r['id']} | {r['lambda']} | {w*w*n:.7f} | {r['critical_chi2']} | {c:.7f} | "
                     f"{r['actual_power']} | {power(w, a, df, n):.7f} | {power(w, a, df, n-1):.7f} | {r['power']} |")
    if fark:
        lines += ["", "FARK olan satırlar (önce görseli tekrar oku): " + ", ".join(fark)]
    if not rows:
        lines += ["", "Oracle CSV boş — görseller bekleniyor."]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
