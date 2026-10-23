# OTURUM 2 — YAZIM (temiz oda) · ilk prompt

Sen **Oturum 2 (yazım)** ajanısın. χ² olumsallık tablosu güç analizi için bir hesap motoru ve CLI yazacaksın.

Çalışma klasörün: `/home/claude/klon-oturum2` (bir git deposu). İçinde yalnızca şunlar var:
- `SPEC.md`: tek davranış kaynağın.
- `oracle/chisq_gof.csv`: G*Power değerleri. `oracle/scale_statsmodels.csv`: statsmodels ölçek vektörleri (kâhin değil).
- `tests/test_differential.py`: CLI'ını oracle'a karşı çalıştıran düzenek.

## Temiz oda kuralı (ihlal etme)
- Davranışı **yalnızca `SPEC.md`**'den öğren.
- Bu klasörün **dışındaki hiçbir dosyayı okuma** (özellikle `/home/claude/chisq-power-clone/`, `/mnt/`, LEDGER, Ghidra/REA çıktıları). Orası inceleme oturumunun alanı.
- `tests/test_differential.py`'yi değiştirme; çalıştır ve raporunu oku. Beklenen değeri sen değil G*Power belirler. Fark varsa hata sendedir.
- Değer uydurma. SPEC'te "BELİRSİZ" yazan yerde SPEC'in verdiği geçici karara uy ve bunu rapora yaz.

## Yapılacaklar
1. **Motor** (`src/chisq_power/engine.py`): Tüm hesap mantığı yalnızca burada. CLI ince bir katman olsun (ileride MCP de aynı motoru çağıracak). Dağılım fonksiyonları için scipy serbest.
2. **CLI** (`src/chisq_power/cli.py`): `gpower-clone` komutu, SPEC §1'e birebir uysun:
   - bayraklar, tek satır JSON, alan adları; yuvarlanmamış tam hassasiyet;
   - hata JSON'u `{"error","code","field"}`, çıkış kodu 2 (geçersiz girdi) / 1 (iç hata);
   - günlükler yalnızca stderr; her çağrı ≤ 2 sn; ağ erişimi yok.
3. **Paketleme**: `pyproject.toml`; `pip install --break-system-packages -e .` ile `gpower-clone` komutu kurulsun.
4. **Testler**: SPEC'teki her Gherkin senaryosunu `tests/test_spec.py` içinde pytest testi olarak yaz. Sonra:
   - `pytest -q`
   - `python tests/test_differential.py` ve `python tests/test_differential.py --scale`
   Hedef: oracle'da N tam eşleşme %100, kapı ≥ %90.
5. **Notlar** (`OTURUM2_NOTLAR.md`):
   - **Halüsinasyonlar:** yanlış çıkardığın her şey; nasıl fark edildi, hangi test yakaladı.
   - **Maliyet:** yaklaşık iterasyon sayısı, takıldığın yerler.
   - **SPEC'teki belirsizlikler:** hangi kararı uyguladın.
6. **Commit**: İşi mantıklı adımlarla git'e commit et. Mesaj sonuna şunu ekle:
   ```
   Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
   ```

## Kurallar
- Paket adı `chisq_power`; "G*Power" adını kullanma. Komut adı `gpower-clone` sözleşme gereğidir.
- Kodda decompile çıktısı ya da G*Power'dan kopyalanmış parça olmayacak.

## Bitince raporla
- `pytest` sonucu.
- Diferansiyel test sonucu: oracle geçen/toplam, N eşleşme oranı, ölçek eşleşme oranı.
- Kalan uyuşmazlıklar ve uyguladığın BELİRSİZ kararlar.

---

## Ajanı başlatan mesaj

> Önce /home/claude/klon-oturum2/OTURUM2_PROMPT.md dosyasını oku; o senin görev tanımın ve ilk prompt'un. Oradaki talimatları eksiksiz uygula.
>
> Kesin kural: /home/claude/klon-oturum2 klasörünün DIŞINDAKİ hiçbir dosyayı okuma, listeleme ya da arama (temiz oda kuralı). Python paketlerini pip ile kurabilirsin. Ağ yalnızca paket kurulumu için var.
>
> Bitince OTURUM2_PROMPT.md'nin "Bitince raporla" bölümündeki maddeleri kısa ve sayısal olarak raporla.

Oturum 2, inceleme oturumundan ayrı bir ajan olarak, yalıtılmış bir klasörde (yalnızca SPEC.md, oracle/ ve tests/test_differential.py) koşuldu. Kendi git geçmişi `klon-oturum2` deposunda: 4 commit.
