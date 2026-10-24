# LEDGER — χ² Goodness-of-fit: Contingency tables

Etiketler: `[DOK]` kılavuzda geçen · `[AJAN]` ajanın çıkarımı, binary kanıtı yok · `[REA]` binary'den kanıtlı (yalnızca REA oturumu doldurur).

Oracle: 30 satır (`oracle/chisq_gof.csv`). 15 a priori sonuç (1–12, 14, 27, 28), 6 post hoc sonuç (15–20), 7 Input error (13, 21–26), 2 Determine paneli (29, 30; w hesaplanmamış). Sayısal sonuç veren 21 satırın 21'i scipy ile 7 basamak aynı.

## [DOK] Kılavuz bilgisi
Kaynak: G*Power 3.1 kılavuzu, "Goodness-of-fit tests: Contingency tables" bölümü; Faul ve ark. (2007). Sayfa numaraları **BELİRSİZ**, kılavuzdan eklenecek.

| # | iddia | not |
|---|---|---|
| D1 | Etki büyüklüğü w = √(Σ (p1ᵢ − p0ᵢ)² / p0ᵢ); p0 = H0, p1 = H1 hücre olasılıkları | kılavuzda formül olarak verilir |
| D2 | Cohen konvansiyonları: w = 0.1 küçük, 0.3 orta, 0.5 büyük | Programın kendi ipucu balonunda da görünüyor (id 11, 14: "Effect size conventions") |
| D3 | H1 altında test istatistiği merkezi olmayan χ² dağılımına uyar; λ = w²·N | |
| D4 | Girdiler: w, α, power (a priori) veya N (post hoc), Df | |
| D5 | Df kullanıcı tarafından girilir; r×c tablo için (r−1)(c−1) | |

## [AJAN] Veriden gözlenen kurallar — diferansiyel testle sınanmalı

| # | iddia | tutan / sınanan | kanıt (oracle id) | durum |
|---|---|---|---|---|
| A1 | Kritik χ² yalnızca α ve Df'ye bağlıdır | 12/12 (α=0.05, Df=1 satırlarının hepsinde 3.8414588); ayrıca α=0.05, Df=2 için 2 ve 16 aynı (5.9914645) | 1, 4, 5, 10, 11, 12, 14, 15, 17, 18, 19, 28; 2, 16 | tutuyor |
| A1b | Kritik χ², merkezi χ²(Df) dağılımının üst α noktasıdır (scipy `chi2.isf` ile 7 basamak aynı) | 21/21 | 1–12, 14–20, 27, 28 | tutuyor |
| A2 | λ = w²·N (ekranda 7 ondalık) | 21/21 | 1–12, 14–20, 27, 28 | tutuyor |
| A3 | A priori N, güç ≥ hedef koşulunu sağlayan en küçük tam sayıdır | 15/15 (scipy N ile birebir; N−1'de scipy gücü hedefin altında) | 1–12, 14, 27, 28 | tutuyor. N−1 değeri G*Power'da doğrudan gözlenmedi |
| A3b | ANOVA'daki gibi bir kat/yuvarlama kuralı yok; N herhangi bir tam sayı olabilir | 15/15 (ör. 99, 133, 191, 245, 78489) | 3, 6, 7, 10, 27 | tutuyor |
| A3c | En küçük N = 1'dir. Hedef güç = α iken de N = 1 döner (N = 0'da güç tam α olurdu, ama 0 izinli değil) | 2/2 | 12, 28 | tutuyor |
| A4 | Actual power ≥ hedef power | 15/15 | 1–12, 14, 27, 28 | tutuyor |
| A4b | Güç, scipy `ncx2.sf` ile 7 basamak aynı (a priori ve post hoc) | 21/21 | 1–12, 14–20, 27, 28 | tutuyor |
| A5 | Post hoc güç, aynı girdili a priori actual power'a eşittir | 2/2 çift | 1↔15, 12↔19 | tutuyor |
| A6 | Hedef power < α → Input error: "Power must be greater than or equal to alpha." | 1/1 | 13 | tutuyor |
| A6b | Hedef power = α kabul edilir (hata yok) | 1/1 | 28 | tutuyor |
| A6c | w ≤ 1e-06 (0 ve negatif dahil) → "Effect size w must be greater 1e-06." | 2/2 | 21, 22 | tutuyor. Tam eşik (1e-06'nın kendisi) sınanmadı |
| A6d | α ∉ (1e-07, 1) → "Alpha is outside the admissible range (1e-07, 1)." | 2/2 (α=0, α=1) | 23, 24 | tutuyor. Sınırların açık/kapalı olduğu sınanmadı |
| A6e | Df < 1 → "Degrees of Freedom must be greater or equal one." | 1/1 | 25 | tutuyor |
| A6f | Post hoc N ∉ [1, 2147483646] → "Total sample size is outside the admissible range (1, 2147483646)" | 1/1 (N=0) | 26 | tutuyor |
| A6g | Hata durumunda tüm çıktı alanları "?" gösterir ve grafik boşalır | 7/7 | 13, 21–26 | tutuyor |
| A7 | w > 1 kabul edilir | 1/1 | 11 | tutuyor |
| A8 | Aynı girdi aynı çıktıyı verir (deterministik) | 2/2 çift | 4↔14, 12↔19↔28 (güç) | tutuyor |
| A9 | Grafik başlığındaki kritik χ² 6 anlamlı basamakla gösterilir (3.84146, 15.0863, 18.307, 4.9802) | 21/21 | 1–12, 14–20, 27, 28 | gözlem; çıktı alanı 7 ondalık |
| A10 | Kesirli Df kabul edilir ve sürekli Df ile hesaplanır (Df=1.5 → N 99; scipy kesirli df ile birebir) | 1/1 | 27 | tutuyor. Kılavuzla çelişip çelişmediği BELİRSİZ |
| A11 | Determine paneli: "Number of cells", hücre başına p(H0)/p(H1), "Equal", "Normalize", "Auto calc last cell", "Calculate", "Calculate and transfer to main window" düğmeleri var | 2/2 | 29, 30 | gözlem. Panelin w hesaplaması henüz görülmedi |
| A12 | Ölçek: statsmodels'in kesirli N'sinin yukarı yuvarlanmışı, scipy taramasıyla bulunan en küçük tam sayı N'ye eşittir (G*Power davranışı A3 ile uyumlu) | 1046/1046 (4 vektörde statsmodels çözüm bulamadı; hepsinde gerçek N = 2) | `oracle/scale_statsmodels.csv` | tutuyor. Kâhin değil; G*Power ile yalnızca 15 a priori satırda doğrulandı |

## [REA] Binary kanıtı

İncelenen binary: `GPowerNT.exe` (G*Power 3.1.9.7), Ghidra projesi `gpower`. Arama: Search → For Strings (min. uzunluk 5, 3984 dize). Decompile çıktısı bu dosyaya konmaz; yalnızca adres ve kısa alıntı.

### R5 — Girdi doğrulama dizeleri

Durum sütunu: **DİZE** = dize binary'de bulundu, ekrandaki mesajla eşleşti. **XREF** = dizeyi kullanan fonksiyon da bulundu (henüz bekliyor).

| id | iddia | dize adresi | alıntı (binary) | oracle | durum |
|---|---|---|---|---|---|
| R5a | power < α hatası | `005c6220` | `"Power must be greater than or equal to alpha."` | 13 | DİZE ✓ · XREF bekliyor |
| R5b | Df < 1 hatası | `005c615c` | `"Degrees of Freedom must be greater or equal one."` | 25 | DİZE ✓ · XREF bekliyor |
| R5c | α aralık hatası; sınırlar dizede yok, çalışma anında ekleniyor | `005c6100` | `"Alpha is outside the admissible range ("` | 23, 24 | DİZE ✓ (önek) · XREF ve sabitler (1e-07, 1) bekliyor |
| R5d | N aralık hatası; sınırlar çalışma anında ekleniyor | `005c6524` | `"Total sample size is outside the admissible range ("` | 26 | DİZE ✓ (önek) · XREF ve sabit (2147483646) bekliyor |
| R5e | w alt sınır hatası; mesaj parçalardan birleştiriliyor | `005c55a8` + `005c61c4` | `"Effect size w"` + `" must be greater "` | 21, 22 | DİZE ✓ (parçalar) · XREF ve sabit (1e-06) bekliyor |
| R5f | power aralık hatası (X05 için beklenen mesaj) | `005c60d8` | `"Power is outside the admissible range ("` | — | DİZE ✓ · oracle X05 ve XREF bekliyor |

**Bulgu (kılavuzda yok):** Aralık hatalarında sınır değerleri dize içinde değil. Mesaj "önek + sayılar + ')'" biçiminde çalışma anında birleştiriliyor. w mesajı da genel bir `" must be greater "` parçasıyla kuruluyor; bu parça başka testlerle ortak. Ekrandaki "greater 1e-06." yazımındaki eksik "than" bu birleştirmeden kaynaklanıyor.

### Bekleyen

| id | iddia | fonksiyon adresi / dize ref | alıntı | durum |
|---|---|---|---|---|
| R1 | λ = w²·N hesabı | | | TODO |
| R2 | Kritik χ²'nin hesaplandığı yer (ters χ² dağılımı) | | | TODO |
| R3 | Merkezi olmayan χ² CDF yöntemi ve hassasiyeti | | | TODO |
| R4 | A priori N arama yöntemi, alt sınır (N=1) ve tam sayıya yuvarlama | | | TODO |
| R6 | Determine penceresinde oranlardan w hesabı | | | TODO |
| R7 | "Effect size conventions" ipucu dizesi | | | TODO |
| R8 | Kesirli Df'nin neden kabul edildiği (Df alanının tipi; float mu?) | | | TODO |
| R9 | N üst sınırı 2147483646 (int32 sınırı −1?) | | | TODO |
