# 60 saniyelik CLI demosu — PowerShell
# Kullanım (repo klasöründe):  powershell -ExecutionPolicy Bypass -File demo\demo.ps1

function Show($cmd, $note) {
    Write-Host ""
    Write-Host "# $note" -ForegroundColor DarkGray
    Write-Host "> $cmd" -ForegroundColor Cyan
    Start-Sleep -Milliseconds 900
    Invoke-Expression $cmd
    Write-Host "(çıkış kodu: $LASTEXITCODE)" -ForegroundColor DarkGray
    Start-Sleep -Seconds 4
}

Clear-Host
Write-Host "chisq-power-clone — χ² olumsallık tablosu güç analizi (temiz oda yeniden yazımı)" -ForegroundColor Yellow
Write-Host "Referans: G*Power 3.1.9.7 · Faul, Erdfelder, Lang & Buchner (2007, 2009)" -ForegroundColor DarkGray
Start-Sleep -Seconds 3

Show 'gpower-clone --test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.80 --df 1' `
     'A priori: kaç denek gerekir? (G*Power: N = 88, güç 0.8035275)'

Show 'gpower-clone --test chi2-contingency --mode post-hoc --w 0.3 --alpha 0.05 --n_total 88 --df 1' `
     'Post hoc: 88 denekle güç kaç? (G*Power: 0.8035275)'

Show 'gpower-clone --test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.95 --df 5' `
     'Sözleşme örneği (beklenen N = 220)'

Show 'gpower-clone --test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.04 --df 1' `
     'Geçersiz girdi: güç < α → hata JSON, çıkış kodu 2'

Show 'python tests/test_differential.py | Select-Object -Last 2' `
     'Diferansiyel test: G*Power ekran görüntülerine karşı'

Write-Host ""
Write-Host "Bitti." -ForegroundColor Yellow
