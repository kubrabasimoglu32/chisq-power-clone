# chisq-power-clone

χ² olumsallık tablosu (goodness-of-fit: contingency tables) güç analizinin temiz oda yeniden yazımı. YZM301 Teardown Sprint, test ailesi 4: **χ² testi, olumsallık tablosu (yanıt oranları)**.

## Yapılan katmanlar

| katman | durum |
|---|---|
| Temel: motor + CLI | ✅ tamam (`src/chisq_power/`), temiz oda Oturum 2'de yazıldı |
| Bonus: MCP sunucusu | ❌ yapılmadı |
| Bonus: AI ajanı | ❌ yapılmadı |

## Durum özeti

| öğe | değer |
|---|---|
| G*Power oracle vektörü | 30 satır, her biri ekran görüntüsüyle (`oracle/`) |
| └ sayısal sonuç | 21 (15 a priori, 6 post hoc) |
| └ geçersiz girdi | 7 (G*Power hata mesajlarıyla) |
| └ Determine paneli | 2 (yalnızca girdi; w henüz görülmedi) |
| scipy sanity uyumu | 21/21, 7 basamak (`tests/uyum_raporu.md`) |
| Ölçek vektörü (statsmodels) | 1050 (`oracle/scale_statsmodels.csv`); 4'ünde statsmodels çözüm bulamadı |
| [REA] kanıtı | 6 hata dizesi binary'de bulundu (R5a–f, adresli); fonksiyon referansları bekleniyor (`LEDGER.md`) |
| CLI diferansiyel testi | oracle 27/27 geçti; **N tam eşleşme 13/13 = %100** (kapı ≥ %90) (`tests/uyum_raporu_cli.md`) |
| CLI ölçek testi | 1050/1050 = %100 |
| SPEC birim testleri | 44/44 (`tests/test_spec.py`) |
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
python -m pytest -q                          # SPEC senaryoları (44 test)
python tests/test_differential.py            # CLI ↔ G*Power oracle (kapı: N ≥ %90 tam eşleşme)
python tests/test_differential.py --scale    # + 1050 ölçek vektörü
python tests/sanity_chi2.py                  # oracle CSV ↔ scipy (kâhin değil)
python tests/gen_scale_statsmodels.py        # ölçek vektörlerini yeniden üretir
```

### Sözleşmeden G*Power'a göre bilinçli sapmalar
G*Power'ın kesirli df'yi kabul etmesi, N = 1'e izin vermesi gibi farklar `SPEC.md` §4'te (S1–S7) listelenmiştir. CLI sözleşmeye uyar.

## Temiz oda süreci
- **Oturum 1 (inceleme):** G*Power ekranlarından oracle, SPEC.md ve LEDGER.md üretti. Motor kodu yazmadı. İlk prompt: `prompts/oturum1_inceleme.md`.
- **Oturum 2 (yazım):** Ayrı bir ajan, yalıtılmış bir klasörde yalnızca SPEC.md, oracle CSV'leri ve CLI'ı çağıran test düzeneğiyle çalıştı. LEDGER'ı ve inceleme betiklerini görmedi. İlk prompt: `prompts/oturum2_yazim.md`, notları: `prompts/oturum2_notlar.md`.
- Yalıtım dosya sistemi izniyle değil talimatla sağlandı; ajan klasör dışına bakmadığını raporladı.

## REA ve Ghidra kontrolü

Ajana "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?" sorusunun cevabı:

![REA kontrolü](docs/rea_kontrol.png) _(ekran görüntüsü eklenecek)_

## Sürüm bilgisi
- Referans: G*Power 3.1.9.7 (Windows), yalnızca resmi sayfadan (psychologie.hhu.de)
- GPower.exe SHA-256: _(doldurulacak — PowerShell: `Get-FileHash .\GPower.exe -Algorithm SHA256`)_
- Bu repo: v0.2 (Oturum 1: inceleme · Oturum 2: motor + CLI)

## Demo video
_(60 saniyelik CLI videosu — eklenecek)_

## Repo yapısı
```
SPEC.md            kabul kriterleri (Gherkin) + CLI sözleşmesi
LEDGER.md          kanıt defteri: [DOK] [AJAN] [REA]
HALLUCINATIONS.md  ajanın yanlış çıkarımları
AGENT_COST.md      ajan maliyet ve süreç günlüğü
EKSIK_VAKALAR.md   G*Power'da alınacak kalan vektörler
prompts/           iki oturumun ilk prompt'ları
oracle/            G*Power vektörleri (CSV) + ekran görüntüleri + ölçek vektörleri
src/chisq_power/   engine.py (tek hesap motoru) + cli.py (ince katman) — Oturum 2
tests/             diferansiyel test, sanity kontrolü, uyum raporları
```

## Atıf
Bu proje G*Power'ın davranışını referans alır; G*Power ile bağlantılı değildir. G*Power'ı bilim dünyasına ücretsiz sunan yazarlara teşekkür ederiz:

Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods, 39*, 175–191.

Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses. *Behavior Research Methods, 41*, 1149–1160.
