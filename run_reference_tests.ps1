# run_reference_tests.ps1

Write-Host "Starting reference benchmark verification..."
Write-Host "==========================================="

if (-not (Test-Path .venv)) {
    python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Write-Host "`n[1/2] Running unit tests..."
python -m unittest discover -s tests
if ($LASTEXITCODE -ne 0) { Write-Error "Unit tests failed."; exit $LASTEXITCODE }

Write-Host "`n[2/2] Running reference benchmark and publication package (outputs_reference)..."
python main.py --output-dir outputs_reference --publication-package
if ($LASTEXITCODE -ne 0) { Write-Error "Reference benchmark failed."; exit $LASTEXITCODE }

Write-Host "`n======================================="
Write-Host "Reference verification completed successfully!"
