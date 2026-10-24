# EKSİK VAKALAR — G*Power'da girilecek vektörler

Test: **χ² tests → Goodness-of-fit tests: Contingency tables**

Alınan: 31 görsel (`oracle/chisq_gof.csv`, id 1–30). **Kalan: 3 görsel.**

## Kalan

| dosya adı | Type of power analysis | Effect size w | α err prob | Power (1−β err prob) | Df | ne yapılacak |
|---|---|---|---|---|---|---|
| X05.png | A priori | 0.3 | 0.05 | **1** | 1 | Calculate'e bas; hata çıkarsa ya da sonuç gelirse görüntüsünü al |
| D01b.png | A priori | — | 0.05 | 0.80 | 1 | Aşağıya bak |
| D02b.png | A priori | — | 0.05 | 0.80 | 2 | Aşağıya bak |

**D01b / D02b nasıl alınır:** Önceki görsellerde (D01a, D02a) olasılıkları doğru girmişsin, ama hesap düğmesine basılmamış; panelde `Effect size w` hâlâ "?" görünüyor.
1. **Determine =>** düğmesine bas; paneldeki değerler duruyorsa dokunma, yoksa D01a'daki gibi tekrar gir (D01: Number of cells 4, p(H0) 0.25 ×4, p(H1) 0.35 / 0.15 / 0.15 / 0.35).
2. Panelin altındaki **Calculate and transfer to main window** düğmesine bas. Paneldeki `Effect size w` dolacak ve ana penceredeki w alanına aktarılacak.
3. Ana pencerede **Calculate**'e bas.
4. Panel hâlâ açıkken görüntüyü al → `D01b.png`.
5. Aynısını D02 için yap (Number of cells 6, p(H0) 0.166667 ×6, p(H1) 0.10 / 0.15 / 0.25 / 0.20 / 0.15 / 0.15, Df **2**) → `D02b.png`.

## İsteğe bağlı (sınır değerleri netleştirir)

| dosya adı | Type | w | α | Power / N | Df | neyi sınar |
|---|---|---|---|---|---|---|
| X11.png | A priori | 0.3 | 0.0000001 | 0.80 | 1 | α alt sınırı tam 1e-07'de hata mı? |
| X12.png | A priori | 0.3 | 0.05 | 0.80 | 0.5 | Df < 1 kesirli → hata mı? |
| C15.png | A priori | 0.3 | 0.05 | 0.80 | 2.5 | kesirli Df ikinci örnek |
