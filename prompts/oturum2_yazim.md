# OTURUM 2 — YAZIM (temiz oda) · ilk prompt

Sen **Oturum 2 (yazım)** ajanısın. χ² olumsallık tablosu güç analizi için bir hesap motoru ve CLI yazacaksın.

## Temiz oda kuralı (ihlal etme)
- Başlangıç girdin **yalnızca `SPEC.md`**. Davranışı oradan öğren.
- `LEDGER.md`'yi, `prompts/oturum1_*.md` dosyalarını, Ghidra/REA çıktılarını ve G*Power'ın kendisini **açma**. Bunları görmen temiz oda kuralını bozar.
- `tests/test_differential.py` dosyasını **çalıştırabilir** ve ürettiği raporu okuyabilirsin. Beklenen değeri sen değil G*Power belirler; fark varsa hata sendedir ya da SPEC'te açıklanmış bir kuraldır.
- Emin olmadığın bir davranışı uydurma. SPEC'te yoksa ya da "BELİRSİZ" yazıyorsa bana sor.

## Yapılacaklar
1. **Motor (`src/…/engine`)**: Tüm hesap mantığı yalnızca burada olsun. CLI (ve ileride MCP/ajan) bu motoru çağıran ince katmanlardır.
   - Dağılım fonksiyonları için scipy serbest. Puan; N arama (çözücü), yuvarlama ve df kurallarından gelir.
2. **CLI**: `gpower-clone` komutu, SPEC §1'deki sözleşmeye birebir uysun:
   - bayraklar, tek satır JSON çıktı, alan adları, yuvarlanmamış tam hassasiyet;
   - hata kodları ve çıkış kodları (2 geçersiz girdi, 1 iç hata);
   - günlükler yalnızca stderr'e; çağrı ≤ 2 sn.
3. **Paketleme**: `pip install -e .` ile `gpower-clone` komutu kurulabilsin (`pyproject.toml`).
4. **Test**: SPEC'teki her Gherkin senaryosunu birim testi olarak yaz (`tests/`), sonra `python tests/test_differential.py` ve `--scale` ile çalıştır. Hedef: oracle'da N tam eşleşme ≥ %90 (hedefimiz %100).
5. **README**: Kurulum ve Çalıştırma bölümlerini doldur.
6. **Kayıt**: Yanlış çıkarımlarını `HALLUCINATIONS.md`'ye, maliyet ve iterasyonları `AGENT_COST.md`'ye ("Oturum 2" bölümü) yaz.

## Kurallar
- Projeye "G*Power" adını verme. Komut adı `gpower-clone` sözleşme gereğidir.
- Kodda decompile çıktısı ya da G*Power'dan kopyalanmış parça olmayacak.
- SPEC §3'teki sapmalarda (S1–S6) SPEC'in kararına uy; "BELİRSİZ" olanlar için bana sor.
