# GRUP 1 GÖREVİ — YZM301 Teardown Sprint (χ² testi, Goodness-of-fit / Contingency tables)

Sen **Oturum 1 (inceleme/analiz)** ajanısın. Bu oturumda YALNIZCA oracle verisini düzenler, doğrular ve SPEC.md ile LEDGER.md üretirsin. **Motor/CLI kodu YAZMA** (o, Grup 2'nin ayrı oturumunun işi; temiz oda kuralı).

## Bağlam
- Ödev: G*Power 3.1.9.7 (Windows) hesap motorunu tersine mühendislikle incele, kanıtla, SPEC.md yaz. Test ailesi: **χ² testleri → Goodness-of-fit tests: Contingency tables** (etki büyüklüğü w, serbestlik derecesi Df), a priori (N hesapla) ve post hoc (güç hesapla).
- Kâhin (doğru cevap) = G*Power ekran görüntüleri. Sen değil, G*Power belirler beklenen değeri.
- Puan yalnızca **[REA]** etiketli kanıta verilir. Kılavuzda yazan = [DOK]. Çıkarımın = [AJAN]. **Hiçbir satıra kanıtsız [REA] yazma.**

## Kurallar (ihlal etme)
1. `GPower.exe` ve kurulum dosyaları repoya girmez; `.gitignore`'a ekle.
2. Decompile çıktısı hiçbir dosyaya konmaz. Ledger'da yalnızca kısa alıntı + fonksiyon adresi olabilir.
3. Projeye "G*Power" adı verme (repo/paket adı örn. `chisq-power-clone`). README'de Faul, Erdfelder, Lang ve Buchner (2007, 2009) atfı olsun.
4. Gerçek hasta verisi yok. Dış AI API'sine yalnızca kurgusal senaryolar.
5. Emin olmadığın bir değeri uydurma; "BELİRSİZ" yaz ve bana sor.

## Girdi
- Görseller: `images/` klasörü (G*Power ekran görüntüleri; iki kişinin görselleri karışık).
- Varsa mevcut CSV/not dosyaları. Önce hepsini listele.

## Adımlar

### 1. Envanter
`images/` ve diğer dosyaları listele. Kaç görsel var, adları nasıl, CSV var mı raporla. Test ailesi χ² dışı (ör. F testi/ANOVA) olan görselleri ayrı listele, CSV'ye alma.

### 2. Görselleri oku ve CSV üret
Her ekran görüntüsünü aç ve şunları oku: Effect size w, α err prob, Power (1−β err prob), Total sample size (post hoc'ta girdi), Df (girdiler); Noncentrality parameter λ, Critical χ², Total sample size, Actual power / Power (çıktılar); "Type of power analysis" (a priori / post hoc).
Ekranda **görünen basamak sayısıyla** yaz. Okunamayan alanı boş bırak ve `notlar` sütununa "okunamadı" yaz.

`oracle/chisq_gof.csv` sütunları:
```
id,mod,w,alpha,power,df,total_n,actual_power,critical_chi2,lambda,screenshot,kaynak,notlar
```
- a priori satırda `power` = girilen hedef güç, `actual_power` = çıktı.
- post hoc satırda `total_n` girdi, `power` boş, `actual_power` = hesaplanan güç.
- `kaynak`: `grup1` veya `grup2` (bilmiyorsan "?" yaz ve bana sor).

### 3. Yeniden adlandırma
- Görselleri `oracle/screenshots/` altına `v{id}.png` olarak **kopyala** (orijinalleri silme/taşıma).
- `images/` klasörünü silme; yalnızca `oracle/screenshots/` oluştur.
- id'leri 1'den başlayarak çakışmasız ver. Eşleme tablosunu `oracle/RENAME_MAP.csv` (eski_ad,yeni_ad,id) olarak yaz.

### 4. Bağımsız çapraz kontrol (kâhin DEĞİL, sadece sanity)
`scipy.stats.ncx2` ile:
- λ = w²·N, kritik χ² = chi2.isf(α, df), güç = ncx2.sf(kritik, df, λ).
- **A priori:** güç ≥ hedef olan en küçük tam sayı N'yi ara (ANOVA'daki "grup sayısının katına yuvarlama" kuralı burada YOK; varsa veriden gözle, varsayma).
- **Post hoc:** verilen N ile gücü hesapla; G*Power'ın gösterdiği basamağa yuvarlayıp karşılaştır. λ ve kritik χ²'yi de karşılaştır.
- Sonuçları `tests/uyum_raporu.md` içine tablo olarak yaz: id, mod, G*Power değeri, scipy değeri, fark, durum (EŞLEŞTİ / FARK).
- FARK olan her satırı listele: önce girdi okuma hatası ihtimalini kontrol et (görseli tekrar oku), sonra gerçek uyuşmazlık olarak işaretle. **Uyuşmazlığı "düzeltme", raporla.** G*Power değeri her zaman geçerlidir.

### 5. Eksik vaka analizi
Veri setinde şunlar var mı kontrol et ve eksikleri `EKSIK_VAKALAR.md`'ye listele (G*Power'da girilecek vektörler olarak, girdi değerleriyle):
- Farklı Df değerleri (1, 2, 3, 4, 5, 10, büyük df ör. 50)
- w çok küçük (ör. 0.01) ve çok büyük (ör. 2, w > 1)
- Cohen eşikleri: w = 0.1 / 0.3 / 0.5
- Güç ≈ α veya α'dan küçük (a priori ve post hoc)
- Geçersiz girdiler (w=0, w<0, α=0, α=1, power=1, power≤α, df=0, N=0)
- Post hoc modu (güç hesaplama), çok küçük N (ör. N=1, 2)
- N'nin tam sayıya yuvarlanma kuralını sınayan satırlar (gerçek N tam sayıya çok yakın/uzak)

### 6. Desenleri çıkar (kanıtlı)
CSV'den gözlenen kuralları çıkar (örn. λ = w²·N mi, kritik χ² yalnızca α ve df'ye mi bağlı, a priori N en küçük tam sayı mı, actual power ≥ hedef güç mü). Her kural için kaç satırda tuttuğunu say. LEDGER.md'ye yaz:
- Kılavuzda geçen = `[DOK]`
- Veriden gözlenen ama binary kanıtı yok = `[AJAN]` (açıkça "diferansiyel testle sınanmalı" yaz)
- `[REA]` satırlarını **boş şablon** bırak: `| id | iddia | fonksiyon adresi / dize ref | alıntı | durum: TODO |`. REA/Ghidra incelemesini ben (veya REA kurulu oturum) yapacak; sen kanıt uydurma.

### 7. Repo iskeleti
```
SPEC.md  LEDGER.md  HALLUCINATIONS.md  AGENT_COST.md  README.md  .gitignore
prompts/  oracle/  oracle/screenshots/  src/  tests/
```
- `.gitignore`: `GPower.exe`, `*.exe`, `GPower*/`, `__pycache__/`, `.venv/`, `images/`, `*.rep/` (Ghidra projesi).
- README iskeleti: bonus katmanlar bölümü, kurulum, çalıştırma, sürüm bilgisi, GPower.exe SHA-256 (bana sor, boş bırak), demo video linki (boş), atıf.
- `prompts/oturum1_inceleme.md`: bu dosyanın içeriğini (ilk prompt olarak) kaydet.
- `HALLUCINATIONS.md` ve `AGENT_COST.md`: şablon başlıklarıyla oluştur. Yanlış çıkarımların olursa dürüstçe kayda geçir (ne dedin, nasıl fark edildi, hangi kontrol yakaladı).

### 8. SPEC.md taslağı
Yalnızca oracle verisi ve [DOK] bilgilerden, **Gherkin** formatında kabul kriterleri yaz:
- Girdi/çıktı alanları (w, alpha, power, df, n / lambda, critical_chi2, total_n, actual_power) ve CLI sözleşmesi (tek satır JSON, geçersiz girdide `{"error":"..."}` + sıfırdan farklı çıkış kodu).
- Her desen için en az bir `Scenario` ve gerçek oracle satırlarından örnek (id referanslı).
- Sınır değer senaryoları.
- Belirsiz/test edilmemiş kurallara "TODO: REA ile doğrulanacak" notu ekle.
- SPEC.md içinde **kod, decompile çıktısı veya algoritmanın adım adım kodu olmasın**; yalnızca davranış.

## Bitirince
Kısa rapor: kaç görsel/satır işlendi, kaç satır EŞLEŞTİ / FARK, hangi satırlar okunamadı, eksik vakaların listesi, REA için bekleyen sorular. Uydurduğun hiçbir şey olmadığını doğrula.
