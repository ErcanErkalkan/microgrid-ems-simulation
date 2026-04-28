# run_q1_tests.ps1

Write-Host "Starting Q1 SCI Pragmatic Test Suite..."
Write-Host "======================================="

if (-not (Test-Path .venv)) {
    python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Write-Host "`n[1/3] Running Core Benchmark & Publication Package (outputs_q1_eval)..."
python main.py --output-dir outputs_q1_eval --publication-package
if ($LASTEXITCODE -ne 0) { Write-Error "Phase 1 failed."; exit $LASTEXITCODE }

Write-Host "`n[2/3] Running FGCS Robustness Extensions (outputs_fgcs_q1)..."
python -m jer_microgrid.fgcs_extensions --output-dir outputs_fgcs_q1
if ($LASTEXITCODE -ne 0) { Write-Error "Phase 2 failed."; exit $LASTEXITCODE }

Write-Host "`n[3/3] Running Evidence Upgrade (outputs_evidence_q1)..."
python -m jer_microgrid.evidence_upgrade --output-root outputs_evidence_q1 --synthetic-seeds 5
if ($LASTEXITCODE -ne 0) { Write-Error "Phase 3 failed."; exit $LASTEXITCODE }

Write-Host "`n======================================="
Write-Host "All tests completed successfully!"
