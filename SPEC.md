# SPEC — χ² olumsallık tablosu güç analizi (`chi2-contingency`)

Kaynaklar: `oracle/chisq_gof.csv` (G*Power 3.1.9.7 ekran görüntülerinden 30 satır), LEDGER.md ([DOK] ve [AJAN] maddeleri) ve dersin CLI sözleşmesi (CONTRACT). Bu belge yalnızca davranışı tanımlar; kod, decompile çıktısı veya algoritma adımı içermez.

Kapsam: **a-priori** (N hesapla) ve **post-hoc** (güç hesapla). Sözleşmede adı geçen compromise / criterion / sensitivity modları bu sürümün kapsamı dışında (bkz. S5).

## 1. CLI sözleşmesi

### Çağrı
```
gpower-clone --test chi2-contingency --mode a-priori --w <w> --alpha <α> --power <1−β> --df <df>
gpower-clone --test chi2-contingency --mode post-hoc --w <w> --alpha <α> --n_total <N> --df <df>
```
- Her gerekli bayrak açıkça verilmelidir; varsayılan değer yoktur.
- Ondalık ayırıcı her zaman noktadır.

### Başarılı çıktı
stdout'a **tek satır JSON**, çıkış kodu **0**.

| mod | alanlar |
|---|---|
| a-priori | `ncp`, `critical_chi2`, `n_total` (tam sayı), `actual_power` |
| post-hoc | `ncp`, `critical_chi2`, `power` |

- `ncp`, G*Power ekranındaki "Noncentrality parameter λ"; `critical_chi2`, "Critical χ²".
- Ondalık alanlar tam double hassasiyetle yazılır, **yuvarlanmaz**.
- Aynı girdi her zaman aynı çıktıyı verir. Günlük ve ilerleme bilgisi yalnızca stderr'e gider.
- Her çağrı ağ erişimi olmadan 2 saniye içinde biter.

### Hatalı girdi
stdout'a tek satır JSON: `{"error": "<insan okuyabilir açıklama>", "code": "<KOD>", "field": "<alan>"}`.
- Geçersiz girdi → çıkış kodu **2**; iç hata → **1**.
- Kodlar: `MISSING_PARAM`, `UNKNOWN_PARAM`, `INVALID_VALUE`, `OUT_OF_RANGE`, `INCONSISTENT`, `UNSUPPORTED`, `NO_SOLUTION`.

### Tolerans
- `n_total` **tam** eşleşmeli.
- Ondalık alanlar: referansla mutlak **ya da** göreli fark ≤ 1e-6.

## 2. Davranış

```gherkin
Feature: χ² olumsallık tablosu güç analizi (chi2-contingency)

  Background:
    Given CLI "gpower-clone --test chi2-contingency" olarak çağrılır

  # [DOK] D3, D4 · [AJAN] A2, A3, A4, A4b
  Scenario Outline: A priori örneklem büyüklüğü
    When "--mode a-priori --w <w> --alpha <alpha> --power <power> --df <df>" çalıştırılır
    Then çıkış kodu 0'dır ve stdout tek satır JSON'dur
    And n_total = <n_total>
    And actual_power ≈ <actual_power>
    And critical_chi2 ≈ <critical_chi2>
    And ncp ≈ <ncp>
    Examples:
      | id | w    | alpha | power | df | n_total | actual_power | critical_chi2 | ncp        |
      | 1  | 0.3  | 0.05  | 0.80  | 1  | 88      | 0.8035275    | 3.8414588     | 7.9200000  |
      | 2  | 0.3  | 0.05  | 0.80  | 2  | 108     | 0.8036939    | 5.9914645     | 9.7200000  |
      | 3  | 0.3  | 0.05  | 0.80  | 4  | 133     | 0.8013043    | 9.4877290     | 11.9700000 |
      | 4  | 0.1  | 0.05  | 0.80  | 1  | 785     | 0.8000569    | 3.8414588     | 7.8500000  |
      | 5  | 0.5  | 0.05  | 0.80  | 1  | 32      | 0.8074304    | 3.8414588     | 8.0000000  |
      | 6  | 0.3  | 0.05  | 0.95  | 3  | 191     | 0.9502399    | 7.8147279     | 17.1900000 |
      | 7  | 0.3  | 0.01  | 0.90  | 5  | 245     | 0.9003979    | 15.0862725    | 22.0500000 |
      | 8  | 0.3  | 0.05  | 0.80  | 10 | 181     | 0.8014702    | 18.3070381    | 16.2900000 |
      | 9  | 0.3  | 0.05  | 0.80  | 50 | 336     | 0.8006734    | 67.5048065    | 30.2400000 |
      | 10 | 0.01 | 0.05  | 0.80  | 1  | 78489   | 0.8000020    | 3.8414588     | 7.8489000  |
      | 11 | 2    | 0.05  | 0.80  | 1  | 2       | 0.8074304    | 3.8414588     | 8.0000000  |

  # [DOK] D3 · [AJAN] A4b, A5
  Scenario Outline: Post hoc güç
    When "--mode post-hoc --w <w> --alpha <alpha> --n_total <n_total> --df <df>" çalıştırılır
    Then çıkış kodu 0'dır
    And power ≈ <power>
    And critical_chi2 ≈ <critical_chi2>
    And ncp ≈ <ncp>
    Examples:
      | id | w   | alpha | n_total | df | power     | critical_chi2 | ncp        |
      | 15 | 0.3 | 0.05  | 88      | 1  | 0.8035275 | 3.8414588     | 7.9200000  |
      | 16 | 0.3 | 0.05  | 50      | 2  | 0.4604212 | 5.9914645     | 4.5000000  |
      | 17 | 0.5 | 0.05  | 10      | 1  | 0.3526081 | 3.8414588     | 2.5000000  |
      | 18 | 0.1 | 0.05  | 100     | 1  | 0.1700750 | 3.8414588     | 1.0000000  |
      | 20 | 0.3 | 0.01  | 200     | 3  | 0.8732131 | 11.3448667    | 18.0000000 |

  # [DOK] D3 · [AJAN] A2 — TODO: REA ile doğrulanacak (R1)
  Scenario: Noncentrality parametresi w² × N'dir
    Given geçerli bir girdi
    Then ncp, w'nin karesi ile n_total'ın çarpımına eşittir
    # örnek: id 4 → 0.1² × 785 = 7.85; id 20 → 0.3² × 200 = 18

  # [AJAN] A1, A1b — TODO: REA ile doğrulanacak (R2)
  Scenario: Kritik değer yalnızca α ve df'ye bağlıdır
    Given alpha 0.05 ve df 1, farklı w, power ve n_total değerleri
    Then critical_chi2 her durumda 3.8414588'dir (merkezi χ²(df) dağılımının üst α noktası)
    # örnek: id 1, 4, 5, 10, 11, 15, 17, 18

  # [AJAN] A3, A3b — TODO: REA ile doğrulanacak (R4)
  Scenario: A priori N, hedef gücü sağlayan en küçük tam sayıdır; kat kuralı yoktur
    Given geçerli bir a priori girdi
    Then n_total ile hesaplanan güç hedefe eşit ya da büyüktür
    And n_total − 1 ile hesaplanan güç hedefin altındadır
    And n_total herhangi bir pozitif tam sayı olabilir (grup sayısının katına yuvarlanmaz)
    # örnek: id 3 (133), id 6 (191), id 10 (78489)

  # [AJAN] A5
  Scenario: A priori ve post hoc tutarlıdır
    Given id 1: a-priori w 0.3, alpha 0.05, power 0.80, df 1 → n_total 88, actual_power 0.8035275
    When post-hoc w 0.3, alpha 0.05, n_total 88, df 1 çalıştırılır
    Then power 0.8035275'tir (id 15)

  # [AJAN] A7
  Scenario: w > 1 kabul edilir
    When "--mode a-priori --w 2 --alpha 0.05 --power 0.80 --df 1" çalıştırılır
    Then n_total = 2 (id 11)

  # [AJAN] A8
  Scenario: Deterministik çıktı
    Given aynı girdi iki kez verilir
    Then iki çıktı birebir aynıdır (id 4 ↔ id 14)

  # [AJAN] A6c–A6f + sözleşme aralıkları — TODO: REA ile doğrulanacak (R5)
  Scenario Outline: Geçersiz girdi reddedilir
    When <mod> modunda <alan> = <değer> verilir, diğer alanlar geçerlidir
    Then çıkış kodu 2'dir
    And stdout {"error": ..., "code": "<code>", "field": "<alan>"} biçimindedir
    Examples:
      | oracle id | mod      | alan    | değer | code         | G*Power tepkisi                                     |
      | 21        | a-priori | w       | 0     | OUT_OF_RANGE | "Effect size w must be greater 1e-06."              |
      | 22        | a-priori | w       | -0.3  | OUT_OF_RANGE | aynı                                                |
      | 23        | a-priori | alpha   | 0     | OUT_OF_RANGE | "Alpha is outside the admissible range (1e-07, 1)." |
      | 24        | a-priori | alpha   | 1     | OUT_OF_RANGE | aynı                                                |
      | 25        | a-priori | df      | 0     | OUT_OF_RANGE | "Degrees of Freedom must be greater or equal one."  |
      | 26        | post-hoc | n_total | 0     | OUT_OF_RANGE | "Total sample size is outside the admissible range" |
      | — (X05)   | a-priori | power   | 1     | OUT_OF_RANGE | oracle bekleniyor                                   |

  # [AJAN] A6 — kod seçimi bizim kararımız (S4)
  Scenario: Hedef güç α'dan küçük
    When "--mode a-priori --w 0.3 --alpha 0.05 --power 0.04 --df 1" çalıştırılır
    Then çıkış kodu 2'dir
    And code "INCONSISTENT", field "power"
    # G*Power: "Power must be greater than or equal to alpha." (id 13)

  # Sözleşme kuralları (oracle gerekmez)
  Scenario Outline: Eksik, bilinmeyen ya da bozuk bayrak
    When <durum>
    Then çıkış kodu 2'dir ve code "<code>"
    Examples:
      | durum                                  | code          |
      | --df verilmez                          | MISSING_PARAM |
      | --ratio 1 gibi tanımsız bayrak verilir | UNKNOWN_PARAM |
      | --w abc verilir                        | INVALID_VALUE |
```

## 3. Sözleşme ile G*Power'ın ayrıştığı yerler

Gizli vektörler sözleşmeye göre çalıştırıldığı için CLI **sözleşmeye** uyar. G*Power'ın farklı davrandığı yerler aşağıda; her biri hocaya sorulacak ve README'de belirtilecek.

| # | durum | G*Power (oracle) | sözleşme | SPEC kararı |
|---|---|---|---|---|
| S1 | kesirli df (1.5) | hesaplar: N 99, güç 0.8030493 (id 27) | df tam sayı ≥ 1 | `INVALID_VALUE`, field `df` |
| S2 | N = 1 | post hoc'ta kabul eder (id 19); a priori N = 1 döndürebilir (id 12, 28) | n_total tam sayı ≥ 2 | post-hoc `n_total 1` → `OUT_OF_RANGE`. A priori sonucun 1 çıktığı durum **BELİRSİZ** (G*Power 1 diyor, sözleşme alt sınırı 2) |
| S3 | 0 < w ≤ 1e-06 | hata | w > 0 | G*Power'a uyulur: `OUT_OF_RANGE` (TODO: X10 ile eşik doğrulanacak) |
| S4 | power < α | Input error (id 13) | aralık (0, 1), özel kural yok | `INCONSISTENT`, field `power` |
| S4b | power = α | kabul, N 1 (id 28) | — | S2'ye bağlı |
| S5 | compromise / criterion / sensitivity | oracle yok | sözleşmede tanımlı | bu sürümde `UNSUPPORTED`; ödev a priori + post hoc istiyor |
| S6 | 0 < α ≤ 1e-07 | hata (aralık 1e-07'den başlıyor) | α ∈ (0, 1) | G*Power'a uyulur: `OUT_OF_RANGE` (TODO: X11 ile doğrulanacak) |

## 4. Açık TODO'lar
- R1–R9 (LEDGER.md): REA ile binary kanıtı.
- Determine paneli (oranlardan w): oracle id 29, 30 yalnızca girdiyi gösteriyor; panelin hesapladığı w görülmedi (D01b, D02b bekleniyor). CLI w'yi doğrudan aldığı için motorun kapsamında değil; ajan katmanında kullanılabilir.
