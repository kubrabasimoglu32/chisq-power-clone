# HALLUCINATIONS — ajanın yanlış çıkarımları

Ajan: Claude Opus 5.5. H1–H4 Oturum 1 (inceleme), H5–H7 Oturum 2 (yazım). Her kayıt: ne dendi, nasıl fark edildi, hangi kontrol yakaladı, ne düzeltildi.

## H1 — "Df her zaman tam sayıdır" varsayımı
- **Ne dendi:** İlk vektör planında (EKSIK_VAKALAR, X08) Df = 1.5 "geçersiz girdi" sınıfına kondu. G*Power'ın bunu reddedeceği örtük olarak varsayıldı. Aynı varsayım sanity betiğine de girdi: Df `int(float(...))` ile tam sayıya çevriliyordu.
- **Nasıl fark edildi:** G*Power, Df = 1.5 ile hata vermedi ve sonuç hesapladı (oracle id 27: N 99, güç 0.8030493).
- **Hangi kontrol yakaladı:** Oracle görseli (X08) + `tests/sanity_chi2.py`. Betik Df'yi 1'e yuvarladığı için bu satırda yanlış karşılaştırma yapacaktı.
- **Düzeltme:** Betik Df'yi ondalık olarak okuyor; scipy kesirli Df ile 7 basamak aynı sonucu verdi. LEDGER A10 eklendi. Sözleşme Df'yi tam sayı istediği için SPEC'te S1 sapması olarak kayda geçti.

## H2 — CLI sözleşmesinin uydurulması
- **Ne dendi:** SPEC'in ilk taslağında CLI girdisi `{"mode":"apriori",...}` biçiminde JSON, çıktı alanları `lambda`, `total_n`, hata çıktısı yalnızca `{"error":...}` olarak tanımlandı. Ders sözleşmesi görülmeden "makul" bir biçim üretildi.
- **Nasıl fark edildi:** Dersin CONTRACT belgesi okununca bayrak tabanlı çağrı (`--test chi2-contingency --mode a-priori --w ...`), `ncp` / `n_total` / `critical_chi2` alanları ve `{"error","code","field"}` + çıkış kodu 2 kuralı ortaya çıktı.
- **Hangi kontrol yakaladı:** Sözleşme ile SPEC'in elle karşılaştırılması.
- **Düzeltme:** SPEC §1 sözleşmeye göre yeniden yazıldı. Diferansiyel test düzeneği sözleşme alan adlarını kullanıyor.

## H3 — Kural sayımında hata
- **Ne dendi:** LEDGER A1 ("kritik χ² yalnızca α ve Df'ye bağlı") için "13/13 satır" yazıldı ve listeye Df = 2 satırları da karıştırıldı.
- **Nasıl fark edildi:** Satırlar tek tek yeniden sayılınca α = 0.05, Df = 1 olan satır sayısının 12 olduğu görüldü.
- **Hangi kontrol yakaladı:** Ajanın kendi yeniden sayımı (öz denetim). Test değil.
- **Düzeltme:** 12/12 olarak düzeltildi; Df = 2 çifti (2, 16) ayrı yazıldı.

## H4 — Determine panelinin düzeni (kısmi)
- **Ne dendi:** Panelin düzeni görülmeden "hücre sayısı + H0/H1 tablosu, muhtemelen 'Calculate and transfer to main window' düğmesi" diye tarif edildi. Belirsiz olduğu açıkça yazıldı.
- **Nasıl fark edildi:** Oracle id 29, 30 tarifin doğru olduğunu gösterdi. Ancak kullanıcı hesap düğmesine basmadan görüntü aldı; talimat yeterince net değildi.
- **Hangi kontrol yakaladı:** Görsel okuma (panelde w = "?").
- **Düzeltme:** EKSIK_VAKALAR'a adım adım D01b/D02b talimatı eklendi.

## H5 — "2 saniye sınırı rahat sağlanır" varsayımı (Oturum 2)
- **Ne dendi:** Motor `scipy.stats` ile yazıldı. Çağrı süresinin sorun olmayacağı varsayıldı.
- **Nasıl fark edildi:** Tek çağrı ~0.97 sn sürdü; bunun ~0.96 sn'si yalnızca `import scipy.stats`.
- **Hangi kontrol yakaladı:** Elle yapılan süre ölçümü. Hiçbir test yakalamadı, çünkü süre sınırın altındaydı.
- **Düzeltme:** `scipy.special` kullanıldı (~0.4 sn). İki yol arasındaki sayısal fark en fazla 6e-16 ölçüldü.

## H6 — Anlamsız test koşulu (Oturum 2)
- **Ne dendi:** "Kat kuralı yok" senaryosunun testine, örnek N'ler tek sayı olduğu için her durumda geçecek bir koşul yazıldı. Test hiçbir şeyi sınamıyordu.
- **Nasıl fark edildi:** Ajan testi yazarken koşulun her zaman doğru döneceğini fark etti.
- **Hangi kontrol yakaladı:** Öz denetim. Böyle bir testi mutasyon testi yakalardı (yapılmadı).
- **Düzeltme:** Koşul, N'nin (df+1)'in katı olmadığını sınayacak biçimde düzeltildi.

## H7 — "`pytest` komutu doğru ortamı görür" varsayımı (Oturum 2)
- **Ne dendi:** Testlerin `pytest -q` ile çalışacağı varsayıldı.
- **Nasıl fark edildi:** `ModuleNotFoundError: chisq_power`. PATH'teki pytest ayrı bir yorumlayıcıya bağlı bir araçtı.
- **Hangi kontrol yakaladı:** Testin ilk çalıştırılması.
- **Düzeltme:** README'de komut `python -m pytest -q` olarak yazıldı.

## H8 — "Mesaj 'greater' diyorsa eşitlik reddedilir" çıkarımı (Oturum 1 → Oturum 2'ye taşındı)
- **Ne dendi:** G*Power'ın "Effect size w must be greater 1e-06." mesajından w = 1e-06'nın da reddedildiği çıkarıldı. SPEC S3'e "0 < w ≤ 1e-06 → hata" yazıldı. Klon (Oturum 2) bunu uyguladı: "eşik dahil reddedilir, 'greater 1e-06' ifadesine göre".
- **Nasıl fark edildi:** Ghidra'da mesajı kuran `FUN_00487880` açıldı. Hata koşulu `değer < sınır`, yani eşitlik kabul ediliyor.
- **Hangi kontrol yakaladı:** REA/Ghidra incelemesi (LEDGER R5e). Diferansiyel test yakalayamazdı, çünkü oracle'da w = 1e-06 vektörü yoktu. Mesaj metnine güvenmek, kodun davranışına güvenmekle aynı şey değil.
- **Düzeltme:** SPEC S3 ve yeni senaryo güncellendi. Klonun düzeltilmesi Oturum 2'ye yalnızca SPEC değişikliği olarak iletilecek. X10 oracle'ı (w = 0.000001) çapraz doğrulama için istendi.

## H9 — Kendi içinde çelişkili SPEC senaryosu (Oturum 1)
- **Ne dendi:** H8 düzeltmesi yapılırken SPEC'e "a priori, w = 1e-06 → çıkış 0, normal N" senaryosu eklendi. Kullanıcıya da "N yaklaşık 7.8 milyar çıkar" denildi.
- **Nasıl fark edildi:** Oturum 2 ajanı senaryoyu uygularken gereken N'nin yaklaşık 7.85 × 10¹² olduğunu (7.8 milyar değil, 7.8 trilyon) ve bunun S7'deki N üst sınırını aştığını gösterdi. Senaryo, S7'nin istediği NO_SOLUTION ile çelişiyordu. Ajan değer uydurmadı; testi strict xfail olarak işaretleyip kararı geri sordu.
- **Hangi kontrol yakaladı:** Temiz oda oturumu. SPEC'i yalnızca metin olarak okuyan bağımsız ajan, iki kuralın birlikte sağlanamayacağını fark etti.
- **Düzeltme:** Senaryo post hoc moduna taşındı (w = 1e-06, N = 1000 → w hatası yok). X10 oracle vektörü de post hoc olarak değiştirildi.
