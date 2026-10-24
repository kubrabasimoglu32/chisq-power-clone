# chisq-power-clone

χ² olumsallık tablosu (goodness-of-fit: contingency tables) güç analizinin temiz oda yeniden yazımı. YZM301 Teardown Sprint, test ailesi 4: **χ² testi, olumsallık tablosu (yanıt oranları)**.

## Yapılan katmanlar

| katman | durum |
|---|---|
| Temel: motor + CLI | ✅ tamam (`src/chisq_power/`), temiz oda Oturum 2'de yazıldı |
| Bonus: MCP sunucusu | ✅ tamam: `gpower-clone-mcp`, tek araç `chi2_contingency_power` (şema: `MCP.md`) |
| Bonus: AI ajanı | ❌ yapılmadı |

## Durum özeti

| öğe | değer |
|---|---|
| G*Power oracle vektörü | 31 satır, her biri ekran görüntüsüyle (`oracle/`) |
| └ sayısal sonuç | 22 (16 a priori, 6 post hoc) |
| └ geçersiz girdi | 7 (G*Power hata mesajlarıyla) |
| └ Determine paneli | 2 (yalnızca girdi; w henüz görülmedi) |
| scipy sanity uyumu | 22/22, 7 basamak (`tests/uyum_raporu.md`) |
| Ölçek vektörü (statsmodels) | 1050 (`oracle/scale_statsmodels.csv`); 4'ünde statsmodels çözüm bulamadı |
| [REA] kanıtı | **2 kanıtlandı:** R5a (`FUN_004880e0`: power ≥ α, eşitlik kabul), R5e (`FUN_00487880`: w < sınır → hata, **eşitlik kabul**, kılavuzda yok). 4 hata dizesi daha adresli; ortak doğrulayıcı (79 çağrı) ve parametre adı tablosu (`LEDGER.md`) |
| CLI diferansiyel testi | oracle 28/28 geçti; **N tam eşleşme 14/14 = %100** (kapı ≥ %90) (`tests/uyum_raporu_cli.md`) |
| CLI ölçek testi | 1050/1050 = %100 |
| SPEC + MCP testleri | 95/95 (`tests/test_spec.py`, `tests/test_mcp.py`) |
| CLI ↔ MCP eşdeğerliği | 38/38 vaka birebir aynı JSON (oracle'ın tüm sayısal ve hata satırları dahil); gerçek stdio istemcisiyle de sınandı |
| Bilinen sapma | id 12 ve 28: G*Power N = 1, CLI N = 2 (sözleşme alt sınırı 2; SPEC §4 S2) |

## Kurulum

Python ≥ 3.10.
```
pip install -e .                 # gpower-clone komutunu kurar (bağımlılık: scipy)
pip install pytest statsmodels   # testler ve ölçek vektörleri için
```

## Çalıştırma

CLI dersin sözleşmesine uyar (ayrıntı: `SPEC.md` §1):
```
gpower-clone --test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.80 --df 1
gpower-clone --test chi2-contingency --mode post-hoc --w 0.3 --alpha 0.05 --n_total 88 --df 1
```
Komut adı `gpower-clone` sözleşme gereğidir; bu proje G*Power değildir ve onun yerine sunulmaz.

Testler:
```
python -m pytest -q                          # SPEC + MCP testleri (95 test)
python tests/test_differential.py            # CLI ↔ G*Power oracle (kapı: N ≥ %90 tam eşleşme)
python tests/test_differential.py --scale    # + 1050 ölçek vektörü
python tests/sanity_chi2.py                  # oracle CSV ↔ scipy (kâhin değil)
python tests/gen_scale_statsmodels.py        # ölçek vektörlerini yeniden üretir
```

### MCP sunucusu
```
gpower-clone-mcp        # stdio MCP sunucusu; Claude Desktop yapılandırması MCP.md'de
```
Araç `chi2_contingency_power` girdi olarak `mode, w, alpha, power | n_total, df` alır ve CLI'ın aynı girdide yazdığı JSON'u birebir döndürür. Hata durumunda aynı hata nesnesini `isError: true` ile döndürür. Mimari: `engine.py` (tek hesap motoru) ← `service.py` (ortak giriş) ← `cli.py` ve `mcp_server.py` (ince katmanlar). scipy yalnızca motorda; bunu mimari testleri denetliyor.

### Sözleşmeden G*Power'a göre bilinçli sapmalar
G*Power'ın kesirli df'yi kabul etmesi, N = 1'e izin vermesi gibi farklar `SPEC.md` §4'te (S1–S7) listelenmiştir. CLI sözleşmeye uyar.

## Temiz oda süreci
- **Oturum 1 (inceleme):** G*Power ekranlarından oracle, SPEC.md ve LEDGER.md üretti. Motor kodu yazmadı. İlk prompt: `prompts/oturum1_inceleme.md`.
- **Oturum 2 (yazım):** Ayrı bir ajan, yalıtılmış bir klasörde yalnızca SPEC.md, oracle CSV'leri ve CLI'ı çağıran test düzeneğiyle çalıştı. LEDGER'ı ve inceleme betiklerini görmedi. İlk prompt: `prompts/oturum2_yazim.md`, notları: `prompts/oturum2_notlar.md`.
- Yalıtım dosya sistemi izniyle değil talimatla sağlandı; ajan klasör dışına bakmadığını raporladı.
- **REA geri besleme döngüsü:** Ghidra bulguları (R5e) ve yeni oracle (31) SPEC'i üç kez değiştirdi. Oturum 2'ye her seferinde yalnızca SPEC farkı iletildi, Ghidra çıktısı iletilmedi. Oturum 2 bu süreçte SPEC'teki bir çelişkiyi yakaladı (HALLUCINATIONS H9). Geçmiş: `klon-oturum2` deposunun 10 commit'i, `prompts/oturum2_notlar.md`.

## REA ve Ghidra kontrolü

REA (`npx rea-agents setup`) Gemini ajanına kayıtlı olarak kuruldu. Ajana "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?" diye soruldu. Cevap (2026-10-24):

> REA (Reverse‑Engineer‑Anything) araçları bu oturumda mevcuttur. reverse‑engineer‑anything skill'inin tanım dosyası (`C:\Users\kubra\.gemini\config\skills\reverse-engineer-anything\SKILL.md`) bulunuyor; bu sayede REA'nın sunduğu statik analiz, dekompilasyon ve karşılaştırma işlevlerini doğrudan çağırabilirsiniz.

Ghidra sağlayıcısı ayrıca sorulduğunda gelen cevap:

> Ghidra sağlayıcısı ise şu anda yüklü ya da kaydedilmiş bir MCP aracı olarak listede yer almıyor. Ghidra‑özel komutları ya da doğrudan Ghidra entegrasyonu bu oturumda kullanılamaz; ancak aynı anda kullanılabilecek diğer native analiz araçları (rizin, radare2‑tabanlı araçlar, inspect_binary_layout, inspect_native_* gibi) mevcuttur.

**Sonuç:** REA kurulu ve native analiz araçları (rizin/radare2) çalışıyor; REA'nın Ghidra sağlayıcısı bağlı değil. LEDGER'daki [REA] satırları REA ajanı üzerinden değil, Ghidra CodeBrowser'da (proje `gpower`, binary `GPowerNT.exe`) elle bulundu: String Search, XREF listeleri ve Decompile paneli. Her satırda adres ve kısa alıntı var; aynı adımlarla tekrar üretilebilir.

## Sürüm bilgisi
- Referans: G*Power 3.1.9.7 (Windows), yalnızca resmi sayfadan (psychologie.hhu.de)
- İncelenen binary: `GPowerNT.exe` (G*Power 3.1.9.7 paketindeki asıl çalıştırılabilir dosya)
- SHA-256: `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812` (PowerShell `Get-FileHash .\GPowerNT.exe -Algorithm SHA256`, 2026-10-24)
- Bu repo: v0.3 (Oturum 1: inceleme · Oturum 2: motor + CLI + MCP)

## Demo video
https://youtu.be/tbmPOeM1CI8 (60 saniyelik CLI demosu: a priori, post hoc, sözleşme örneği, geçersiz girdi ve G*Power oracle'ına karşı diferansiyel test; betik `demo/demo.ps1`)

## Repo yapısı
```
SPEC.md            kabul kriterleri (Gherkin) + CLI sözleşmesi
LEDGER.md          kanıt defteri: [DOK] [AJAN] [REA]
HALLUCINATIONS.md  ajanın yanlış çıkarımları
AGENT_COST.md      ajan maliyet ve süreç günlüğü
EKSIK_VAKALAR.md   G*Power'da alınacak kalan vektörler
prompts/           iki oturumun ilk prompt'ları
oracle/            G*Power vektörleri (CSV) + ekran görüntüleri + ölçek vektörleri
src/chisq_power/   engine.py (tek hesap motoru) ← service.py ← cli.py, mcp_server.py — Oturum 2
MCP.md             MCP araç şeması ve yapılandırma
demo/demo.ps1      60 saniyelik CLI demosu
tests/             diferansiyel test, sanity kontrolü, uyum raporları
```

## Atıf
Bu proje G*Power'ın davranışını referans alır; G*Power ile bağlantılı değildir. G*Power'ı bilim dünyasına ücretsiz sunan yazarlara teşekkür ederiz:

Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods, 39*, 175–191.

Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses. *Behavior Research Methods, 41*, 1149–1160.
