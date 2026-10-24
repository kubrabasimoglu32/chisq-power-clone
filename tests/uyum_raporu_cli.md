# Diferansiyel test raporu (CLI ↔ G*Power oracle)

Komut: `gpower-clone` · tolerans: n_total tam, ondalık ≤ 1e-06 (mutlak ya da göreli)

| id | mod | durum | not |
|---|---|---|---|
| 1 | apriori | GEÇTİ |  |
| 2 | apriori | GEÇTİ |  |
| 3 | apriori | GEÇTİ |  |
| 4 | apriori | GEÇTİ |  |
| 5 | apriori | GEÇTİ |  |
| 6 | apriori | GEÇTİ |  |
| 7 | apriori | GEÇTİ |  |
| 8 | apriori | GEÇTİ |  |
| 9 | apriori | GEÇTİ |  |
| 10 | apriori | GEÇTİ |  |
| 11 | apriori | GEÇTİ |  |
| 12 | apriori | BELİRSİZ (S2) | kod 0 {'ncp': 0.18, 'critical_chi2': 3.8414588206941285, 'n_total': 2, 'actual_power': 0.07086349410120685} |
| 13 | apriori | GEÇTİ | beklenen INCONSISTENT, gelen kod 2 {'error': 'Power must be greater than or equal to alpha.', 'code': 'INCONSISTENT', 'field': 'power'} |
| 14 | apriori | GEÇTİ |  |
| 15 | posthoc | GEÇTİ |  |
| 16 | posthoc | GEÇTİ |  |
| 17 | posthoc | GEÇTİ |  |
| 18 | posthoc | GEÇTİ |  |
| 19 | posthoc | GEÇTİ | beklenen OUT_OF_RANGE, gelen kod 2 {'error': 'Total sample size is outside the admissible range [2, 2147483646].', 'code': 'OUT_OF_RANGE', 'field': 'n_total'} |
| 20 | posthoc | GEÇTİ |  |
| 21 | apriori | GEÇTİ | beklenen OUT_OF_RANGE, gelen kod 2 {'error': 'Effect size w must be greater than or equal to 1e-06.', 'code': 'OUT_OF_RANGE', 'field': 'w'} |
| 22 | apriori | GEÇTİ | beklenen OUT_OF_RANGE, gelen kod 2 {'error': 'Effect size w must be greater than or equal to 1e-06.', 'code': 'OUT_OF_RANGE', 'field': 'w'} |
| 23 | apriori | GEÇTİ | beklenen OUT_OF_RANGE, gelen kod 2 {'error': 'Alpha is outside the admissible range (1e-07, 1).', 'code': 'OUT_OF_RANGE', 'field': 'alpha'} |
| 24 | apriori | GEÇTİ | beklenen OUT_OF_RANGE, gelen kod 2 {'error': 'Alpha is outside the admissible range (1e-07, 1).', 'code': 'OUT_OF_RANGE', 'field': 'alpha'} |
| 25 | apriori | GEÇTİ | beklenen OUT_OF_RANGE, gelen kod 2 {'error': 'Degrees of freedom must be greater or equal one.', 'code': 'OUT_OF_RANGE', 'field': 'df'} |
| 26 | posthoc | GEÇTİ | beklenen OUT_OF_RANGE, gelen kod 2 {'error': 'Total sample size is outside the admissible range [2, 2147483646].', 'code': 'OUT_OF_RANGE', 'field': 'n_total'} |
| 27 | apriori | GEÇTİ | beklenen INVALID_VALUE, gelen kod 2 {'error': "'df' must be an integer, got '1.5'.", 'code': 'INVALID_VALUE', 'field': 'df'} |
| 28 | apriori | BELİRSİZ (S2) | kod 0 {'ncp': 0.18, 'critical_chi2': 3.8414588206941285, 'n_total': 2, 'actual_power': 0.07086349410120685} |
| 31 | apriori | GEÇTİ |  |
| K1 | apriori | GEÇTİ |  |

**Oracle: 28/28 satır geçti.**
**N tam eşleşme (kapı ≥ %90): 14/14 = %100.0**
