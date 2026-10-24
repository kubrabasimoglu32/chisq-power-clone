# AGENT_COST — ajan maliyet ve süreç günlüğü

## Oturum 1 — inceleme (oracle, SPEC, LEDGER)

| alan | değer |
|---|---|
| Ajan | Claude Opus 5.5 (claude.ai, dosya + kabuk araçları, bilgisayara köprü) |
| Tarih | 2026-10-23 |
| Süre | ~1 saat (20:14–21:10, kullanıcının G*Power'da görüntü aldığı süre dahil) |
| İterasyon | 5 kullanıcı turu: görev uyarlaması → 14 a priori görsel → vektör talimatı → 16 görsel → sözleşmeye uyarlama |
| Okunan görsel | 30 G*Power ekran görüntüsü |
| Token | **Tahmini**, ölçülmedi: görsel başına ~1–1.5 bin token × 30 ≈ 40 bin; metin ve araç çağrılarıyla toplam yaklaşık 200–300 bin. Kesin değer kullanım ekranından doldurulacak. |
| Maliyet | BELİRSİZ, kullanım ekranından doldurulacak |
| REA / Ghidra | REA, Gemini ajanına kuruldu (kontrol cevabı README'de). Kanıtlar Ghidra CodeBrowser'da elle toplandı; ajan, kullanıcının gönderdiği ekran görüntülerini okuyup LEDGER'a işledi (2026-10-24, ~30 dk, ~15 ekran görüntüsü). |

### Ne işe yaradı
- Vektörleri önceden kodlu dosya adlarıyla (C01, P01, X01) planlamak: görseller ile CSV satırlarının eşleştirilmesi kolaylaştı.
- Bağımsız scipy kontrolü: 21/21 satır 7 basamak tuttu. Okuma hatası olsaydı hemen görünecekti.

### Neyi farklı yapardık
- Ders sözleşmesini (CONTRACT) en başta okumak. SPEC'in CLI bölümü bir kez boşuna yazıldı (H2).
- Kullanıcıya her vektörü G*Power alan adlarıyla, tam tablo halinde ilk seferde vermek. İlk talimat ("N", "Determine") anlaşılmadı, bir tur kaybedildi.
- Hata diyaloğunun girdi alanlarını örttüğünü baştan söylemek (id 13'te w okunamadı).
- İkinci tur görseller adlandırılmadan geldi; içerikten eşleştirildi. Dosya adı kuralını daha görünür vermek gerekirdi.

## Oturum 2 — yazım (temiz oda)

| alan | değer |
|---|---|
| Ajan | Claude Opus 5.5, Oturum 1'den ayrı başlatılmış bağımsız ajan; yalıtılmış klasör |
| Tarih | 2026-10-23 |
| Süre | ~21 dakika (ölçek koşusu ~8 dk dahil) |
| Token | ~105 bin (ajan araç sayacı) |
| Araç çağrısı | 35 |
| Commit | 3 (motor+CLI+paket, testler, notlar+rapor) |
| Sonuç | ilk denemede oracle 27/27, N 13/13, ölçek 1050/1050 |
| SPEC güncellemesi turları | 3 tur (S3, senaryo düzeltmesi, S7), toplam ~8 dk, ~30 bin token; son durum oracle 28/28, N 14/14, 50 test |

### Takıldığı yerler
- `scipy.stats` içe aktarması tek başına ~1 sn sürüyordu (2 sn sınırının yarısı). `scipy.special`'a geçilince süre ~0.4 sn'ye düştü.
- PATH'teki `pytest` ayrı bir ortamda kurulu olduğu için paketi göremedi; testler `python -m pytest` ile çalıştırıldı.

### Neyi farklı yapardık
- Sınır vektörlerini her iki modda (a priori ve post hoc) baştan almak. S7 hatası (H10) tesadüfen yakalandı.
- Çağrı süresi sınırını SPEC'e bir senaryo olarak eklemek. Sorunu test değil, elle yapılan ölçüm yakaladı.
