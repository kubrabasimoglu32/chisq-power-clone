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
| REA / Ghidra | Bu oturumda kullanılmadı. [REA] satırları boş şablon. |

### Ne işe yaradı
- Vektörleri önceden kodlu dosya adlarıyla (C01, P01, X01) planlamak: görseller ile CSV satırlarının eşleştirilmesi kolaylaştı.
- Bağımsız scipy kontrolü: 21/21 satır 7 basamak tuttu. Okuma hatası olsaydı hemen görünecekti.

### Neyi farklı yapardık
- Ders sözleşmesini (CONTRACT) en başta okumak. SPEC'in CLI bölümü bir kez boşuna yazıldı (H2).
- Kullanıcıya her vektörü G*Power alan adlarıyla, tam tablo halinde ilk seferde vermek. İlk talimat ("N", "Determine") anlaşılmadı, bir tur kaybedildi.
- Hata diyaloğunun girdi alanlarını örttüğünü baştan söylemek (id 13'te w okunamadı).
- İkinci tur görseller adlandırılmadan geldi; içerikten eşleştirildi. Dosya adı kuralını daha görünür vermek gerekirdi.

## Oturum 2 — yazım
_(doldurulacak)_
