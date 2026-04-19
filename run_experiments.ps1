param(
    [string]$OutDir = "outputs_full",
    [switch]$Smoke,
    [switch]$PublicationPackage
)

if (-not (Test-Path .venv)) {
    python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

if ($Smoke) {
    if ($PublicationPackage) {
        python main.py --smoke --output-dir $OutDir --publication-package
    } else {
        python main.py --smoke --output-dir $OutDir
    }
} else {
    if ($PublicationPackage) {
        python main.py --output-dir $OutDir --publication-package
    } else {
        python main.py --output-dir $OutDir
    }
}
