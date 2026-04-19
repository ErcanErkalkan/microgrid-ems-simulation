# Manuscript Scaffold

## Title

Stress-Aware Heuristic Energy Management for Microgrids Under Ramp and Power-Cap Constraints

## Abstract

Bu çalışma, mikroşebeke enerji yönetimi için PLC/SCADA-uyumlu sezgisel bir controller sunar. Yöntem, PCC ramp davranışını ve grid import/export cap ihlallerini azaltmayı hedeflerken batarya throughput, cycle-depth ve switching yükünü birlikte dikkate alır. Deney paketi sentetik fakat tekrar üretilebilir senaryo ailesi üzerinde Proposed controller'ı `NC`, `GR`, `RS`, `FBRL`, MPC referansları ve Oracle referansları ile karşılaştırır. Sonuçlar, yöntemin özellikle ramp ve switching tarafında güçlü bir trade-off sunduğunu; ancak bazı senaryolarda cap-violation açısından `GR`'ye karşı taviz verebildiğini göstermektedir. Bu nedenle yöntem tam baskın optimal çözüm olarak değil, hesaplama dostu ve stres-farkındalıklı pratik bir controller olarak konumlandırılmalıdır.

## 1. Introduction

- Microgrid EMS problemi neden önemlidir?
- Saha uygulamalarında neden basit, hızlı ve açıklanabilir controller'lar gerekir?
- Sadece ramp azaltmak veya sadece cap-violation azaltmak neden yeterli değildir?
- Bu çalışmanın katkıları:
  1. Stress-aware heuristic controller
  2. Reproducible synthetic benchmark suite
  3. Battery stress proxy metrics + paired stats + ablation pipeline

## 2. Related Work

- Rule-based microgrid EMS
- MPC-based microgrid EMS
- Battery degradation-aware dispatch
- Rainflow / cycle-depth tabanlı degradation proxy kullanımı

Not:
- Bu bölüm insan tarafından gerçek literatürle doldurulmalıdır.
- İddiaları yazarken Proposed method'i “optimal” değil “pragmatic heuristic” olarak konumlandırmak daha güvenlidir.

## 3. Problem Setup

- Microgrid bileşenleri
- Net demand tanımı
- PCC ramp ve cap kısıtları
- Battery SOC ve güç sınırları
- Zaman çözünürlüğü ve senaryolar

## 4. Proposed Method

- Current cap-fix priority
- Forecast-based lookahead
- Reserve correction / prep behavior
- Hysteresis / dwell / action-hold
- PLC/SCADA compatibility ve düşük hesaplama karmaşıklığı

## 5. Experimental Protocol

- Synthetic scenario generation
- Seeds, scenario families, horizon
- Compared controllers
- Main metrics
- Stress proxy metrics
- Paired statistics and Holm correction
- Ablation design
- Oracle / MPC referanslarının rolü

## 6. Results

Önerilen alt başlıklar:

- Main comparison
- Stress proxy comparison
- Pairwise stats vs all baselines
- Ablation results
- MPC / Oracle reference discussion
- Sensitivity analysis

## 7. Discussion

- Proposed controller hangi trade-off'u sunuyor?
- `GR` ile kıyaslandığında güçlü taraflar:
  - lower ramp
  - lower flip/day
  - often lower or comparable IDOD
- Zayıf taraflar:
  - bazı senaryolarda higher cap-violation
  - tam baskın değil
- Bu nedenle iddia dili:
  - “balanced stress-aware heuristic”
  - “practical low-complexity controller”
  - “promising trade-off, not universal dominance”

## 8. Threats to Validity

- Synthetic data assumption
- No hardware-in-the-loop validation
- Tariff / market / forecast uncertainty simplifications
- Metric proxy limitations
- Hyperparameter selection bias risk

## 9. Conclusion

Bu çalışma, mikroşebeke EMS için hızlı ve açıklanabilir bir stress-aware heuristic controller paketi sunmaktadır. Deneyler yöntemin özellikle ramp ve switching tarafında rekabetçi bir trade-off sağlayabildiğini göstermektedir. Gelecek iş olarak gerçek saha verisi, HIL doğrulama ve degradation-aware cost calibration önerilmektedir.

## Artifact Note

Makale artifact referansı olarak aşağıdaki dosyalar öne çıkarılabilir:

- `README.md`
- `PUBLICATION_GUIDE.md`
- `outputs_full/claims_summary_table.csv`
- `outputs_full/paired_stats_all_baselines.csv`
- `outputs_full/publication/publication_audit.md`
- `outputs_full/run_manifest.json`
