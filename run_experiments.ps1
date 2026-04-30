param(
    [string]$OutDir = "outputs_reference",
    [switch]$Smoke,
    [switch]$PublicationPackage
)

if (-not (Test-Path .venv)) {
    python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .

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
