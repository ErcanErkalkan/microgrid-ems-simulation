# Publication Guide

Bu repo, makale gönderimine yakın bir deney/artifact paketi üretecek şekilde hazırlanmıştır. Kabul garantisi vermez; ama teknik tekrar üretilebilirlik, controller seçimi ve claim-audit tarafını otomatikleştirir.

## Recommended Commands

Tam deney koşusu:

```powershell
python main.py --output-dir outputs_full
```

Tam deney + publication audit paketi:

```powershell
python main.py --output-dir outputs_full --publication-package
```

Hızlı doğrulama:

```powershell
python main.py --smoke --output-dir outputs_smoke
```

Not:
- `--smoke` koşusu dosya üretimini doğrular; repeated-split candidate stabilitesi ve hold-out seçimi ancak çoklu seed içeren tam koşuda anlamlıdır.

## Main Artifacts

- `main_comparison_table.csv` / `.tex`: ana controller karşılaştırması
- `stress_proxy_table.csv` / `.tex`: batarya-stres proxy tablosu
- `paired_stats_table.csv` / `.tex`: legacy paired stats
- `paired_stats_all_baselines.csv` / `.tex`: Proposed vs tüm ana baseline'lar
- `claims_summary_table.csv` / `.tex`: claim audit özeti
- `claims_by_scenario.csv` / `.tex`: claim audit'in senaryo bazlı kırılımı
- `runtime_summary.csv` / `.tex`: controller başına hesaplama maliyeti özeti
- `run_manifest.json`: tüm ana deney ayarları + Proposed controller parametreleri
- `publication/`: train/hold-out seçim ve audit paketi

## Publication Folder

`--publication-package` kullanıldığında aşağıdakiler üretilir:

- `candidate_search_train.csv`: GR referansına göre train split aday sıralaması
- `candidate_search_holdout.csv`: aynı adayların hold-out split sıralaması
- `candidate_search_repeated.csv`: deterministic repeated-split candidate sonuçları
- `candidate_stability_summary.csv`: repeated-split stabilite özeti
- `holdout_main_comparison_table.csv` / `.tex`
- `holdout_claims_summary.csv` / `.tex`
- `holdout_claims_by_scenario.csv` / `.tex`
- `holdout_pairwise_stats.csv` / `.tex`
- `publication_audit.md`
- `publication_selection.json`

## What This Package Covers

- Controller varsayılanlarının seçimini belgeleme
- Hold-out split ile aşırı uyumu azaltma
- Repeated-split stabilite kontrolü ile aday seçimini daha savunulabilir hale getirme
- Çoklu baseline karşılaştırması
- Senaryo bazlı claim kırılımı
- Runtime/complexity kanıtı
- Etki büyüklüğü, p-değeri ve Holm düzeltmesi
- LaTeX tablo çıktıları
- Figür ve manifest üretimi

## What Still Needs Human Authorship

- Literatür taraması ve related work konumlandırması
- Yenilik iddiasının dikkatli cümlelerle yazılması
- Hedef dergi/konferans kurallarına göre formatlama
- Limitations / threat-to-validity bölümü
- Gerçek saha verisi, HIL veya hardware validation gerekiyorsa onun eklenmesi

## Recommended Claim Discipline

- `GR` karşısında tam üstünlük iddia etmeyin.
- Daha güvenli ifade: Proposed controller daha düşük ramp, daha düşük veya benzer IDOD ve daha düşük switching ile çalışırken, cap-violation tarafında bazı senaryolarda taviz verebilir.
- Oracle ve MPC sonuçlarını “referans” olarak, Proposed controller’ı ise “pragmatic heuristic” olarak çerçevelemek daha savunulabilir olacaktır.
