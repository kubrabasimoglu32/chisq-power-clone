# Oturum 2 notları (yazım, temiz oda)

Davranış yalnızca `SPEC.md`'den öğrenildi; klasör dışına bakılmadı.

## Halüsinasyonlar / yanlış çıkarımlar
1. **"Her çağrı ≤ 2 sn" rahat sağlanır varsayımı.** İlk sürüm `scipy.stats` (`chi2`, `ncx2`) kullanıyordu; tek çağrı ~0.97 sn sürdü. Bunun ~0.96 sn'si yalnızca `import scipy.stats`. Elle `time gpower-clone ...` ölçümüyle fark edildi (test yakalamadı, sınırın altındaydı ama yarısını yiyordu). `scipy.special` (`chdtri`, `chndtr`) ile değiştirildi: ~0.44 sn; iki yol arasındaki fark 6e-16 ile ölçüldü.
2. **`pytest` komutu ortamı görür varsayımı.** PATH'teki `pytest` izole bir uv aracı (kendi yorumlayıcısı); `ModuleNotFoundError: chisq_power` verdi. Kod hatası değil, ortam meselesi; testler `python -m pytest -q` ile çalıştırıldı.
3. **Test içindeki "kat kuralı yok" iddiası.** İlk taslakta `n % (df+1) != 0 or n % 2 == 1` gibi anlamsız bir koşul yazdım (191 ve 78489 tek olduğu için her şeyi geçirirdi). Yazarken fark edip `n % (df+1) != 0` olarak düzelttim.
4. Oracle sayısal değerlerinde halüsinasyon çıkmadı: ilk çalıştırmada 27/27 geçti, N eşleşmesi 13/13, ölçek 1050/1050.

## Maliyet
- Yaklaşık 12–15 araç iterasyonu; motor ilk denemede oracle'ı tutturdu.
- Takılınan yerler: scipy.stats içe aktarma süresi (2 sn bütçesi), uv-izole pytest, ölçek koşusunun uzunluğu (~1050 CLI çağrısı × ~0.45 sn ≈ 8 dk).

## SPEC belirsizlikleri ve uygulanan kararlar
- **S2 (a priori sonucun 1 çıktığı durum, BELİRSİZ):** Arama alt sınırı sözleşmedeki 2'dir; N = 1 asla döndürülmez. id 12 ve id 28 için CLI `n_total: 2` verir (G*Power 1 diyor). Diferansiyel test bu satırları BELİRSİZ sayıyor, oran dışında. Ölçek vektörlerinde gerçek minimumu 1 olan satır yok (scipy ile kontrol edildi).
- **S2 post-hoc:** `n_total 1` → `OUT_OF_RANGE`, field `n_total`.
- **S1:** kesirli df → `INVALID_VALUE`, field `df`. `n_total` için de aynı tam sayı kuralı (`50.5` → `INVALID_VALUE`). `1.0` gibi tam değerli ondalıklar kabul edilir.
- **S3:** `w ≤ 1e-06` → `OUT_OF_RANGE` (eşik dahil reddedilir, "greater 1e-06" ifadesine göre).
- **S4:** `power < alpha` → `INCONSISTENT`, field `power`. `power = alpha` kabul (S4b) → S2 nedeniyle N = 2.
- **X05:** `power ≥ 1` ya da `≤ 0` → `OUT_OF_RANGE`.
- **S5:** compromise / criterion / sensitivity → `UNSUPPORTED`, field `mode`. Başka bilinmeyen mod → `INVALID_VALUE`; `--test` ≠ `chi2-contingency` → `UNSUPPORTED`, field `test`.
- **S6:** `alpha ≤ 1e-07` ya da `≥ 1` → `OUT_OF_RANGE`.
- **S7 (BELİRSİZ):** 2147483646'yı aşan a priori N → `NO_SOLUTION`, field `n_total`, çıkış kodu 2.
- **SPEC'te tanımsız, benim kararım:** moda ait olmayan bayrak (ör. a-priori'de `--n_total`) → `UNKNOWN_PARAM`; aynı bayrağın iki kez verilmesi → `INVALID_VALUE`; değersiz bayrak → `MISSING_PARAM`; doğrulama sırası bilinmeyen → eksik → test/mod → sözdizimi → aralık → tutarlılık. İç hata JSON'unda `code` = `INTERNAL` (SPEC kod listesinde iç hata kodu yok), çıkış 1.
