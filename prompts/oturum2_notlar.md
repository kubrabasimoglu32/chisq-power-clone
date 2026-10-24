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
- **S3:** (güncellendi, aşağıya bkz.) `w < 1e-06` → `OUT_OF_RANGE`; `w = 1e-06` geçerli.
- **S4:** `power < alpha` → `INCONSISTENT`, field `power`. `power = alpha` kabul (S4b) → S2 nedeniyle N = 2.
- **X05:** `power ≥ 1` ya da `≤ 0` → `OUT_OF_RANGE`.
- **S5:** compromise / criterion / sensitivity → `UNSUPPORTED`, field `mode`. Başka bilinmeyen mod → `INVALID_VALUE`; `--test` ≠ `chi2-contingency` → `UNSUPPORTED`, field `test`.
- **S6:** `alpha ≤ 1e-07` ya da `≥ 1` → `OUT_OF_RANGE`.
- **S7:** (güncellendi, aşağıya bkz.) a priori N için üst sınır yok; 2147483646 yalnızca post-hoc `n_total` girdisinde.
- **SPEC'te tanımsız, benim kararım:** moda ait olmayan bayrak (ör. a-priori'de `--n_total`) → `UNKNOWN_PARAM`; aynı bayrağın iki kez verilmesi → `INVALID_VALUE`; değersiz bayrak → `MISSING_PARAM`; doğrulama sırası bilinmeyen → eksik → test/mod → sözdizimi → aralık → tutarlılık. İç hata JSON'unda `code` = `INTERNAL` (SPEC kod listesinde iç hata kodu yok), çıkış 1.

## SPEC güncellemesi 1 (S3: w alt sınırı)
- **Önceki karar:** `w ≤ 1e-06` → `OUT_OF_RANGE`. Eşitliği de reddediyordum; dayanağım G*Power mesajındaki "greater 1e-06" ifadesi ve eski SPEC'teki `0 < w ≤ 1e-06 → hata` satırıydı.
- **Neden değişti:** SPEC böyle dedi. Güncel §4 S3 ve §3'teki yeni senaryo "w alt sınırına tam eşitse kabul edilir" (`[REA] R5e`): hata yalnızca `w < 1e-06` iken. Kontrol `w >= 1e-06` yapıldı; mesaj "Effect size w must be greater than or equal to 1e-06." oldu, çünkü G*Power'ın "greater" metni artık eşitlik davranışıyla çelişiyor. Test satırı S3: `w = 0.0000009` → `OUT_OF_RANGE`, field `w`.
- **Çözülmemiş SPEC çelişkisi (S3 ↔ S7):** Yeni senaryo `--w 0.000001 --alpha 0.05 --power 0.80 --df 1` için çıkış 0 ve en küçük N istiyor. Bu girdi için gereken ncp ≈ 7.8489, yani N ≈ 7.85 × 10¹², sınırın (2147483646) yaklaşık 3655 katı. Değişmeyen S7, bu durumda `NO_SOLUTION` (çıkış 2) diyor. İki kural aynı anda sağlanamaz. Değer uydurmamak için S7 korundu: CLI `NO_SOLUTION` döner. Yeni senaryonun "çıkış 0" kısmı `tests/test_spec.py`'de `xfail(strict=True)` olarak gerekçesiyle duruyor. w = 1e-06'nın doğrulamadan geçtiği (field `w` hatası yok) ve post-hoc'ta normal hesaplandığı ayrıca test ediliyor. SPEC'in hangisinin geçerli olduğuna karar vermesi gerekiyor (ör. S7 sınırını kaldırmak ya da senaryo girdisini değiştirmek).

## SPEC güncellemesi 2 (w = 1e-06 senaryosu post-hoc'a taşındı)
- S3 ↔ S7 çelişkisi SPEC'te giderildi: senaryo artık post-hoc (`w 0.000001, alpha 0.05, n_total 1000, df 1` → çıkış 0, ncp 1e-09, power ≈ 0.0500000001). Motor değişmedi.
- xfail kaldırıldı. Yerine iki normal test geldi: post-hoc senaryosu ve a-priori w = 1e-06 → `NO_SOLUTION`, field `n_total` (SPEC notu: önce w kontrolü geçer, sonra N üst sınırı devreye girer).

## SPEC güncellemesi 3 (S7: a priori N üst sınırı kaldırıldı, oracle 31)
- **Önceki karar:** a priori N > 2147483646 → `NO_SOLUTION`. **Yeni:** sınır yok, normal sonuç (SPEC ve oracle 31 böyle diyor). 2147483646 yalnızca post-hoc `n_total` girdisinde geçerli (`OUT_OF_RANGE`).
- `--w 0.000001 --alpha 0.05 --power 0.80 --df 1` → `n_total` 7848860509327 (JSON tam sayı; %.5g = 7.8489e+12, oracle notundaki scipy değeriyle aynı), ncp 7.8488605…, actual_power 0.80000000000004. Süre ~0.4 sn: üstel arama + ikili arama, yaklaşık 85 değerlendirme.
- **BELİRSİZ (N > 2⁵³) için kararım:** arama 2⁵³'te durur → `NO_SOLUTION`, field `n_total`, çıkış 2. Bu sınırın üstünde double her tam sayıyı tutamadığı için ncp = w²N ve "en küçük N" kesin olmaktan çıkar. Gerçekte w ≥ 1e-06 ve power < 1 ile buraya ancak çok büyük df ile ulaşılıyor (ör. df 1e8).
- **Bu sırada bulunan hata (önceden vardı, halüsinasyon sayılır):** `scipy.special.chndtr` df ≳ 1e11'de NaN döndürüyor. NaN aramada fark edilmiyordu ve CLI `json.dumps` hatasıyla traceback verip stdout'u boş bırakıyordu (çıkış 1, JSON yok). df = 1e12 ile elle denerken yakalandı. Artık sonlu olmayan her ara değer `NumericalError` → çıkış 1, `{"error","code":"INTERNAL","field":null}`. SPEC df için üst sınır tanımlamadığından bunu girdi hatası değil iç hata saydım.
- Testler: eski "a-priori w=1e-06 → NO_SOLUTION" ve "S7 → NO_SOLUTION" testleri yeni senaryoya göre değişti. Eklenenler: post-hoc n_total sınırı, 2⁵³ kararı, NaN → iç hata JSON'u. Ölçek vektörleri yeni aramayla motordan tekrar kontrol edildi: 1050/1050.

## SPEC güncellemesi 4 (MCP, §6)
- **Ortak giriş noktası:** `src/chisq_power/service.py` → `execute(params) -> Outcome(status, payload)` ve `to_json`. CLI'daki "sonuç/hata nesnesi üret + JSON'a çevir" kısmı buraya taşındı; CLI ve MCP ikisi de yalnızca bunu çağırıyor. scipy yalnızca `engine.py`'de.
- **`mcp_server.py`:** resmî SDK (mcp 2.3.0, düşük seviye `Server`, stdio). Tek araç `chi2_contingency_power`. Başarıda `content[0].text` = CLI stdout satırı, `structuredContent` = aynı nesne. Hatada aynı hata nesnesi ve `isError: true`.
- **Karar:** girdi şeması `tools/list`'te yayınlanıyor ama SDK'ya doğrulatılmıyor (`get_tool_input_schema` verilmedi). Aksi hâlde `df: 1.5` gibi girdiler motora ulaşmadan SDK hatasıyla dönerdi ve CLI ile eşdeğerlik bozulurdu.
- **Karar:** JSON `null` → alan yok sayılır. Şemada olmayan alan motora iletilir → `UNKNOWN_PARAM` (CLI ile aynı). `test` araç adından çıkarılır.
- **Halüsinasyon / takılma:** mcp 2.x'te `FastMCP` kaldırılmış (`MCPServer` olmuş) ve alan adları snake_case (`structured_content`, `is_error`). v1 alışkanlığıyla yazmadan önce SDK kaynağına bakarak doğrulandı. İlk stdio testinde `anyio.fail_after` olay döngüsü dışında çağrıldığı için `NoEventLoopError` aldım; pytest yakaladı, döngünün içine taşındı.
- `requires-python` ≥ 3.10'a çekildi (mcp SDK gereği).
- `oracle/chisq_gof.csv` çalışma kopyasında commit'lenmemiş bir değişiklik var: yalnızca `kaynak` sütunu (`?` → `grup1`), değerler aynı (csv ile alan alan karşılaştırıldı). Dosya 11:51'de, benim bu adımımdan önce değişmiş; ben yazmadım. Koordinatöre ait sayıp commit'lerime katmadım. `git diff HEAD~1` çalışma kopyasıyla karşılaştırdığı için ilk bakışta "güncelleme 4"ün parçası sanmıştım.
- Testler: `tests/test_mcp.py`:
  - 38 eşdeğerlik vakası: 29 oracle satırının tamamı, §6'nın 4 örneği ve 5 sözleşme vakası (eksik, bilinmeyen, bozuk, UNSUPPORTED, INTERNAL);
  - gerçek stdio istemcisi;
  - mimari testleri.
  
  Toplam pytest: 95 geçti.
