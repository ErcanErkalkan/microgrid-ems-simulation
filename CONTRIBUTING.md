# Contributing

Contributions are welcome through GitHub issues and pull requests.

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[test]
```

## Verification

Run the unit tests before submitting changes:

```powershell
python -m unittest discover -s tests
```

For pipeline changes, also run a smoke benchmark:

```powershell
python main.py --smoke --output-dir outputs_smoke
```

## Pull Request Expectations

- Keep changes focused.
- Document new controller parameters or metrics in `README.md`.
- Add or update tests for behavioral changes.
- Avoid committing large regenerated output directories unless they are the
  designated reproducibility artifact for a release.

## Reporting Issues

Please include:

- operating system and Python version,
- command used,
- complete error message,
- whether the failure occurs in the smoke run or the full benchmark.
