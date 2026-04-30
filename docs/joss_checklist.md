# JOSS Readiness Checklist

This checklist maps the repository to the JOSS review expectations.

## Complete in Repository

- OSI-approved license: `LICENSE` uses MIT.
- Research-software paper: `paper/paper.md`.
- Bibliography: `paper/paper.bib`.
- Citation metadata: `CITATION.cff`.
- Zenodo metadata: `.zenodo.json`.
- README with statement of need, installation, example usage, tests, and
  reproducibility notes.
- Core API overview: `docs/api.md`.
- Contribution guidelines: `CONTRIBUTING.md`.
- Code of conduct: `CODE_OF_CONDUCT.md`.
- Package metadata and console script: `pyproject.toml`.
- Automated local tests: `tests/test_core.py`.
- GitHub Actions test workflow: `.github/workflows/tests.yml`.
- GitHub Actions JOSS draft workflow: `.github/workflows/draft-pdf.yml`.
- Smoke benchmark command documented in `README.md`.
- Current reproducibility artifact: `outputs_reference/`.
- Paper includes the currently required JOSS sections: Statement of Need,
  State of the Field, Software Design, Research Impact, Availability and
  Reproducibility, and AI Usage Disclosure.

## External Submission Actions

These cannot be completed from the local workspace alone:

- Make the GitHub repository public before submission.
- Enable GitHub Issues for reviewer interaction.
- Tag a release, for example `v0.1.0`.
- Archive the tagged release on Zenodo and obtain a DOI.
- Add the Zenodo DOI to `paper/paper.bib`, `paper/paper.md`, `CITATION.cff`,
  and `.zenodo.json`.
- Add the author's ORCID to `paper/paper.md` if one is available.
- Confirm whether the public repository shows at least six months of open
  development history; JOSS may desk-reject repositories that appear newly
  public without sufficient development history.
- If six months of public development history is not visible in this
  repository, provide verifiable evidence of earlier public availability,
  external use, releases, issue/PR discussion, or related publications before
  submission.
