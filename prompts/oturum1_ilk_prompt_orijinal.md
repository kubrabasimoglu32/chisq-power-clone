# OTURUM 1 — İNCELEME · ilk prompt (orijinal)

Oturum, aşağıdaki görev dosyası (ANOVA için yazılmıştı) ve şu kullanıcı mesajıyla başladı:

> "bunun x^2 testi olacak şekilde değiştirip uygular mısın"

Ajanın χ² için uyarladığı sürüm: `oturum1_inceleme.md`.

---

# GRUP 1 GÖREVİ — YZM301 Teardown Sprint (Tek yönlü ANOVA, F testi)

Sen **Oturum 1 (inceleme/analiz)** ajanısın. Bu oturumda YALNIZCA oracle verisini düzenler, doğrular ve SPEC.md ile LEDGER.md üretirsin. **Motor/CLI kodu YAZMA** (o, Grup 2'nin ayrı oturumunun işi; temiz oda kuralı).

## Bağlam
- Ödev: G*Power 3.1.9.7 (Windows) hesap motorunu tersine mühendislikle incele, kanıtla, SPEC.md yaz. Test ailesi: **F testi, tek yönlü ANOVA (fixed effects, omnibus, one-way)**, a priori (N hesapla) ve post hoc (güç hesapla).
- Kâhin (doğru cevap) = G*Power ekran görüntüleri. Sen değil, G*Power belirler beklenen değeri.
- Puan yalnızca **[REA]** etiketli kanıta verilir. Kılavuzda yazan = [DOK]. Çıkarımın = [AJAN]. **Hiçbir satıra kanıtsız [REA] yazma.**

## Kurallar (ihlal etme)
1. `GPower.exe` ve kurulum dosyaları repoya girmez; `.gitignore`'a ekle.
2. Decompile çıktısı hiçbir dosyaya konmaz. Ledger'da yalnızca kısa alıntı + fonksiyon adresi olabilir.
3. Projeye "G*Power" adı verme (repo/paket adı örn. `anova-power-clone`). README'de Faul, Erdfelder, Lang ve Buchner (2007, 2009) atfı olsun.
4. Gerçek hasta verisi yok. Dış AI API'sine yalnızca kurgusal senaryolar.
5. Emin olmadığın bir değeri uydurma; "BELİRSİZ" yaz ve bana sor.

## Girdi
- Görseller: `images/` klasörü (G*Power ekran görüntüleri; iki kişinin görselleri karışık).
- Varsa mevcut CSV/not dosyaları. Önce hepsini listele.

## Adımlar

### 1. Envanter
`images/` ve diğer dosyaları listele. Kaç görsel var, adları nasıl, CSV var mı raporla.

### 2. Görselleri oku ve CSV üret
Her ekran görüntüsünü aç ve şunları oku: Effect size f, α err prob, Power, Number of groups (girdiler); Noncentrality λ, Critical F, Numerator df, Denominator df, Total sample size, Actual power (çıktılar); varsa "Type of power analysis" (a priori / post hoc).
Ekranda **görünen basamak sayısıyla** yaz. Okunamayan alanı boş bırak ve `notlar` sütununa "okunamadı" yaz.

`oracle/anova_oneway.csv` sütunları:
```
id,mod,f,alpha,power,groups,total_n,n_per_group,actual_power,critical_f,df1,df2,lambda,screenshot,kaynak,notlar
```
`kaynak`: `grup1` veya `grup2` (hangisinin görseli olduğunu bilmiyorsan "?" yaz ve bana sor).

### 3. Yeniden adlandırma
- Görselleri `oracle/screenshots/` altına `v{id}.png` olarak **kopyala** (orijinalleri silme/taşıma yerine kopyala).
- `images/` klasörünü silme; yalnızca `oracle/screenshots/` oluştur.
- id'leri 1'den başlayarak çakışmasız ver. Eşleme tablosunu `oracle/RENAME_MAP.csv` (eski_ad,yeni_ad,id) olarak yaz.

### 4. Bağımsız çapraz kontrol (kâhin DEĞİL, sadece sanity)
`scipy.stats.ncf` ile her a priori satırı için tahmini N hesapla:
- λ = f²·N, df1 = k−1, df2 = N−k, kritik F = F.isf(α, df1, df2), güç = ncf.sf(kritik, df1, df2, λ).
- En küçük N'yi ara; **toplam N'yi grup sayısının katına yukarı yuvarla** (bilinen G*Power davranışı: f=0.25, α=0.05, güç=0.80, 3 grup → 159; 4 grup güç 0.95 → 280).
- Sonuçları `tests/uyum_raporu.md` içine tablo olarak yaz: id, G*Power N, scipy N, fark, durum (EŞLEŞTİ / FARK).
- FARK olan her satırı listele: önce girdi okuma hatası ihtimalini kontrol et (görseli tekrar oku), sonra gerçek uyuşmazlık olarak işaretle. **Uyuşmazlığı "düzeltme", raporla.** G*Power değeri her zaman geçerlidir.

### 5. Eksik vaka analizi
Veri setinde şunlar var mı kontrol et ve eksikleri `EKSIK_VAKALAR.md`'ye listele (benim için G*Power'da girilecek vektörler olarak, girdi değerleriyle):
- Farklı grup sayıları (2, 3, 4, 5, 10)
- d/f çok küçük ve çok büyük
- Güç ≈ α veya α'dan küçük
- Geçersiz girdiler (f=0, α=0, α=1, power=1, groups=1)
- Post hoc modu (güç hesaplama)
- Toplam N için grup sayısının katı kuralını sınayan satırlar

### 6. Desenleri çıkar (kanıtlı)
CSV'den gözlenen kuralları çıkar (örn. N her zaman k'nın katı mı, df2 = N−k mı, λ = f²·N mi). Her kural için kaç satırda tuttuğunu say. Bunları LEDGER.md'ye yaz:
- Kılavuzda geçen = `[DOK]`
- Veriden gözlenen ama binary kanıtı yok = `[AJAN]` (açıkça "diferansiyel testle sınanmalı" yaz)
- `[REA]` satırlarını **boş şablon** olarak bırak: `| id | iddia | fonksiyon adresi / dize ref | alıntı | durum: TODO |`. REA/Ghidra incelemesini ben (veya REA kurulu oturum) yapacak; sen kanıt uydurma.

### 7. Repo iskeleti
```
SPEC.md  LEDGER.md  HALLUCINATIONS.md  AGENT_COST.md  README.md  .gitignore
prompts/  oracle/  oracle/screenshots/  src/  tests/
```
- `.gitignore`: `GPower.exe`, `*.exe`, `GPower*/`, `__pycache__/`, `.venv/`, `images/` (orijinal ham klasör istersem kaldırırım).
- README iskeleti: bonus katmanlar bölümü, kurulum, çalıştırma, sürüm bilgisi, GPower.exe SHA-256 (bana sor, boş bırak), demo video linki (boş), atıf.
- `prompts/oturum1_inceleme.md`: bu dosyanın içeriğini (ilk prompt olarak) kaydet.
- `HALLUCINATIONS.md` ve `AGENT_COST.md`: şablon başlıklarıyla oluştur. Bu oturumda senin yanlış çıkarımların olursa dürüstçe kayda geçir (ne dedin, nasıl fark edildi, hangi kontrol yakaladı).

### 8. SPEC.md taslağı
Yalnızca oracle verisi ve [DOK] bilgilerden, **Gherkin** formatında kabul kriterleri yaz:
- Girdi/çıktı alanları ve CLI sözleşmesi (tek satır JSON, geçersiz girdide `{"error":"..."}` + sıfırdan farklı çıkış kodu).
- Her desen için en az bir `Scenario` ve gerçek oracle satırlarından örnek (id referanslı).
- Sınır değer senaryoları.
- Belirsiz/test edilmemiş kurallara "TODO: REA ile doğrulanacak" notu ekle.
- SPEC.md içinde **kod, decompile çıktısı veya algoritmanın adım adım kodu olmasın**; yalnızca davranış.

## Bitirince
Bana şunu raporla (kısa): kaç görsel/satır işlendi, kaç satır EŞLEŞTİ / FARK, hangi satırlar okunamadı, eksik vakaların listesi, REA için bekleyen sorular. Uydurduğun hiçbir şey olmadığını doğrula.
