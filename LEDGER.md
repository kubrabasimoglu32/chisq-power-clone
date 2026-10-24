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
| A6 | Hedef power < α → Input error: "Power must be greater than or equal to alpha." | 1/1 | 13 | **[REA] R5a ile kanıtlandı** |
| A6b | Hedef power = α kabul edilir (hata yok) | 1/1 | 28 | **[REA] R5a ile kanıtlandı** (`<=`) |
| A6c | w < 1e-06 (0 ve negatif dahil) → "Effect size w must be greater 1e-06."; **w = 1e-06 kabul** | 2/2 | 21, 22 | **[REA] R5e ile kanıtlandı** (`<`); tam eşik için oracle X10 bekleniyor |
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
| R5a | power < α hatası; **power = α kabul** (karşılaştırma `<=`) | `005c6220` → **`FUN_004880e0`** @ `004880e6` (`COMISD` + `JC`) | `if (param_2 <= param_3) return 1;` — aksi halde `FUN_00437db0(..., "Power must be greater than or equal to alpha.")` | 13, 28 | **KANITLANDI** |
| R5b | Df < 1 hatası | `005c615c` | `"Degrees of Freedom must be greater or equal one."` | 25 | DİZE ✓ · XREF bekliyor |
| R5c | α aralık hatası; sınırlar dizede yok, çalışma anında ekleniyor | `005c6100` | `"Alpha is outside the admissible range ("` | 23, 24 | DİZE ✓ (önek) · XREF ve sabitler (1e-07, 1) bekliyor |
| R5d | N aralık hatası; sınırlar çalışma anında ekleniyor | `005c6524` | `"Total sample size is outside the admissible range ("` | 26 | DİZE ✓ (önek) · XREF ve sabit (2147483646) bekliyor |
| R5e | Etki büyüklüğü alt sınır kontrolü: hata yalnızca **değer < sınır**; **eşitlik kabul** (kılavuzda yok, mesaj metniyle çelişiyor) | `005c61c4` → **`FUN_00487880`** (`PUSH s_must_be_greater` @ `00487903`) | `if (in_stack_0000001c < in_stack_00000024) { ... "Effect size " ... " must be greater " ... }` | 21, 22 | **KANITLANDI** · sınır sabitinin (1e-06) çağıran fonksiyondaki değeri bekliyor |
| R5f | power aralık hatası (X05 için beklenen mesaj) | `005c60d8` | `"Power is outside the admissible range ("` | — | DİZE ✓ · oracle X05 ve XREF bekliyor |

Ek referanslar (aynı Listing ekranından):
- `005c61d8` `" is outside the admissible range ("` → XREF[2]: `FUN_00487b70`, `FUN_00488200` (genel aralık mesajı, birden çok doğrulayıcı kullanıyor)
- `005c61fc` `" is inside the prohibited range ("` → XREF[1]: `FUN_00487a40`
- `005c6250` `"Sample size must be greater than or equal to "` → XREF[1]: `FUN_00488700`

**R5a ayrıntı:** `FUN_004880e0(this, double, double)` iki ondalık alır, `param_2 <= param_3` ise 1 döndürür. Parametre rolleri (param_2 = α, param_3 = power) mesaj metninden çıkarıldı. Eşitlik kabul edildiği için oracle id 28 (power = α → hesaplar, N 1) binary ile tutarlı. `FUN_004880e0`'a **79 çağrı** var (References to FUN_004880e0, hepsi UNCONDITIONAL_CALL; ilki `00497e14`, liste `004c26ea` ötesine uzanıyor). power ≥ α kontrolü testlere özgü değil, bütün test pencerelerinin paylaştığı tek bir doğrulayıcı. `FUN_00437db0(this+0x2b0, mesaj)` ortak hata bildirim fonksiyonu gibi görünüyor ([AJAN]; referans listesiyle sınanacak).

Doğrulama fonksiyonları `0x00487a40`–`0x00488700` aralığında kümeleniyor: ortak bir girdi doğrulama modülü olması muhtemel ([AJAN], decompile ile sınanacak).

**R5e ayrıntı:** `FUN_00487880(this, std::string ad, double değer, double sınır)` bütün testlerin ortak etki büyüklüğü doğrulayıcısı. Mesaj dört parçadan kuruluyor: sabit `"Effect size "` + `ad` (bizde "w") + `" must be greater "` + `sınır` (`operator<<` ile, varsayılan 6 anlamlı basamak → "1e-06") + `"."` (`DAT_005c4ac8` = 0x2E). Ekrandaki "Effect size w must be greater 1e-06." (oracle 21, 22) bununla birebir. "than" kelimesinin eksikliği bu birleştirmeden geliyor. Karşılaştırma `değer < sınır` olduğu için **w = sınır kabul edilir**. SPEC'in eski S3 kararı ("eşik dahil reddedilir") ve klonun davranışı bu noktada yanlıştı (HALLUCINATIONS H8). Sınırın 1e-06 olduğu ekrandaki mesajdan okunuyor; çağıran fonksiyondaki sabit henüz görülmedi.

**Parametre adı tablosu:** `005c55a8` "Effect size w" dizesine kod doğrudan erişmiyor; tek referansı `00609400(*)` adresindeki bir işaretçi. Bu işaretçi, `PTR_s_Number_of_groups_006093f0` ile başlayan bir işaretçi dizisinin 4. elemanı: [0] "Number of groups", [1] "Denominator df", [2] "Numerator df", [3] "M", [4] "Effect size w", [5] "Effect size d", [6] "Effect size f^2". Dizinin başına 14 fonksiyondan referans var (`FUN_0050e460`, `FUN_00512f80`, `FUN_00513720`, `FUN_0051d200`, `FUN_0051d660`, `FUN_0051fbe0`, `FUN_00521280`, `FUN_00521780`, `FUN_00522300`, `FUN_00522990`; bazıları iki kez). Parametre adları testler arasında paylaşılan bir tablodan sıra numarasıyla seçiliyor ([AJAN] yorumu: hata mesajı = `tablo[i]` + `" must be greater "` + sınır; doğrulayıcı fonksiyonla sınanacak).

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
