# Recommended Improvements

A prioritized list of improvements for the Agriculture Parts Lookup project, organized by impact and effort.

---

## 1. Testing (High Impact)

**Current state:** No test framework, no unit tests, no integration tests.

### Recommendations

- **Add pytest** as the test framework (add `pytest>=7.0` to `requirements.txt`)
- **Unit tests for ROI calculations:** The scoring logic in `tractor_performance_roi_analysis.py:69-128` and `planter_roi_analysis.py:62-113` is the core value of the project. These functions should have deterministic tests that verify score weights, tier assignments, and edge cases (e.g., all-zero gains, single-part input, division-by-zero when `max_payback` is 0).
- **Unit tests for the forum miner's text processing:** The regex matching in `jd1720_forum_miner.py:117-135` (`count_matches`, `count_parts`) can be tested against known input strings without any network access.
- **CSV parsing tests:** Verify that `load_performance_parts()` and `load_upgrades()` handle malformed rows, missing columns, and empty files gracefully rather than crashing with an unhandled `KeyError` or `ValueError`.
- **Integration test for the forum miner:** Use `responses` or `requests-mock` to test `mine_thread()` end-to-end against a saved HTML fixture, confirming that issue/part counts are correct.
- **Add a CI workflow for tests:** Extend `.github/workflows/` with a test job that runs on every push and PR, blocking merges on failure.

### Why it matters

The ROI scoring formulas and regex patterns are the kind of logic that silently produces wrong results when changed. Without tests, there is no way to know if a formula tweak or regex edit breaks existing behavior.

---

## 2. Data Validation (High Impact)

**Current state:** Scripts assume CSV files are well-formed. A missing column or non-numeric price will crash with an unhelpful traceback.

### Recommendations

- **Validate CSV schemas on load.** Check that required columns exist before accessing them. Report which file and which column is missing.
- **Validate numeric fields.** Wrap `float()` conversions in `tractor_performance_roi_analysis.py:48-58` and `planter_roi_analysis.py:45-51` with error handling that identifies the problematic row and value.
- **Guard against division by zero.** `max_payback` and `max_revenue` are used as divisors (`tractor_performance_roi_analysis.py:81`, `planter_roi_analysis.py:77-80`). If all values are 0 (e.g., empty or corrupt CSV), the scripts crash. Add explicit checks.
- **Validate part number formats** in the product CSVs to catch data entry errors early (e.g., a part number that is accidentally a price).

---

## 3. Error Handling & Logging (Medium Impact)

**Current state:** All output uses `print()`. Errors in the forum miner are caught with a bare `except Exception` at `jd1720_forum_miner.py:250` and printed to stdout.

### Recommendations

- **Replace `print()` with Python's `logging` module.** Use `logging.info()` for progress, `logging.warning()` for recoverable issues, and `logging.error()` for failures. This allows users to control verbosity and redirect output to files.
- **Avoid bare `except Exception`.** The forum miner catches all exceptions at line 250, which silently swallows programming bugs (e.g., `TypeError`, `AttributeError`). Catch `requests.RequestException` for network errors and let programming errors propagate.
- **Add exit codes.** Both ROI scripts exit 0 even when they produce warnings (e.g., non-production-fitment parts). Use distinct exit codes for "completed with warnings" vs "completed clean."

---

## 4. Code Duplication (Medium Impact)

**Current state:** `tractor_performance_roi_analysis.py` and `planter_roi_analysis.py` share significant structural patterns — CSV loading, tier assignment, report writing, and summary printing are near-identical.

### Recommendations

- **Extract a shared module** (e.g., `roi_utils.py`) containing:
  - Generic CSV loading with schema validation
  - `assign_tiers()` — identical logic in both scripts (`tractor_performance_roi_analysis.py:131-143`, `planter_roi_analysis.py:116-128`)
  - `write_report_csv()` — structurally identical
  - Summary printing helpers (tier breakdown, category best-of)
- **Keep scoring functions separate** since the weight factors and input fields differ between tractors and planters. The scoring logic is appropriately specialized.

This reduces maintenance burden and ensures tier thresholds stay consistent across analyses.

---

## 5. Forum Miner Robustness (Medium Impact)

**Current state:** The forum miner has hardcoded URLs, compiles regexes on every call, and stores all thread text in memory.

### Recommendations

- **Pre-compile regex patterns.** `ISSUE_PATTERNS` at `jd1720_forum_miner.py:35-49` are compiled inside `count_matches()` on every call. Compile them once at module load time using `re.compile()`.
- **Add retry logic for HTTP requests.** `fetch_html()` at line 87-91 makes a single attempt. Network flakiness is common in CI. Use `requests.adapters.HTTPAdapter` with `urllib3.util.retry.Retry` for automatic retries with backoff.
- **Don't store full thread text in `ThreadResult`.** The `text` field (line 82) stores the entire page text in memory for every thread. This is never written to output. Either drop it after extraction or stream processing.
- **Respect `robots.txt`.** The docstring mentions respecting robots.txt (line 9), but no code checks it. Use `urllib.robotparser` to verify crawl permission before fetching.
- **Make the miner generic.** Currently hardcoded to JD 1720 planter forums. The architecture (fetch, parse, regex match, aggregate) works for any equipment type. Parameterize the issue patterns and part terms so the same miner can scan threads for any tractor or planter model.

---

## 6. Security (Medium Impact)

### Recommendations

- **GitHub Actions: pin action versions to SHA hashes** instead of tags. The workflow at `.github/workflows/forum-miner.yml:27-28` uses `actions/checkout@v4` — tag-based references can be retargeted. Use full commit SHAs.
- **GitHub Actions: sanitize the `urls_file` input.** The workflow passes `${{ github.event.inputs.urls_file }}` directly into a shell command at line 42-43 without validation. This is a command injection vector. Validate the input or use an environment variable.
- **Add a `.env.example`** and ensure `.env` is in `.gitignore` if environment variables are ever used for API keys or credentials.
- **Pin dependency versions.** `requirements.txt` uses `>=` minimum versions. For reproducible builds, pin exact versions or use a `requirements.lock` / `pip-compile` workflow.

---

## 7. Code Quality Tooling (Medium Impact)

**Current state:** No linter, formatter, or type checker configured.

### Recommendations

- **Add `ruff`** for linting and formatting (replaces flake8 + black + isort in a single fast tool). Add a `ruff.toml` or `[tool.ruff]` section in `pyproject.toml`.
- **Add `mypy`** for type checking. The codebase already uses some type hints (`jd1720_forum_miner.py:87`, `94`, `117`) but not consistently. Adding `mypy --strict` incrementally will catch type errors.
- **Add `pre-commit`** hooks to enforce formatting and linting before commits.
- **Add a linting CI job** that runs on every PR alongside tests.

---

## 8. Project Configuration (Low Impact)

**Current state:** No `pyproject.toml`. Dependencies are in a bare `requirements.txt`.

### Recommendations

- **Add `pyproject.toml`** as the single project configuration file. Define project metadata, dependencies, tool configs (ruff, mypy, pytest), and entry points.
- **Add a `[project.scripts]` entry point** so users can run `agriculture-parts-roi` instead of `python tractor_performance_roi_analysis.py`.
- **Separate runtime and dev dependencies.** `requests` and `beautifulsoup4` are runtime deps. `pytest`, `ruff`, `mypy`, and `pre-commit` should be dev/optional deps.

---

## 9. CI/CD Expansion (Low Impact)

**Current state:** One workflow for the forum miner only.

### Recommendations

- **Add a test/lint workflow** triggered on all pushes and PRs:
  - Run `pytest`
  - Run `ruff check` and `ruff format --check`
  - Run `mypy`
- **Add a workflow to validate CSV data** — run a lightweight script that checks all 86 CSVs for schema correctness (required columns exist, numeric fields parse, no empty part numbers).
- **Add a workflow for the ROI analysis scripts** — run both tractor and planter ROI analyses on push to verify they complete without errors. Compare output checksums to detect unintended scoring changes.
- **Add branch protection** on `main` requiring CI to pass before merge.

---

## 10. Documentation Gaps (Low Impact)

**Current state:** Good README with data structure docs, but missing developer-facing documentation.

### Recommendations

- **Add a "Development Setup" section** to the README covering: clone, create virtualenv, install deps, run scripts, run tests.
- **Add a "Contributing" section** or `CONTRIBUTING.md` with guidelines for adding new equipment brands (CSV schema to follow, folder naming, required files).
- **Document the ROI scoring methodology** in more detail — the README describes weights but doesn't explain the normalization math or assumptions (e.g., diesel at $3.80/gal, 8 gal/hr burn rate). Users should understand what drives the scores.
- **Add inline comments for the regex patterns.** The issue patterns at `jd1720_forum_miner.py:35-49` are non-trivial. Adding a comment next to each explaining what real-world issue it targets (e.g., `# Seed metering failures: skips or doubles`) would help maintainers.

---

## Summary by Priority

| Priority | Area | Effort | Impact |
|----------|------|--------|--------|
| **P0** | Testing (unit + integration) | Medium | High |
| **P0** | Data validation on CSV load | Low | High |
| **P1** | Error handling & logging | Low | Medium |
| **P1** | Code duplication (shared module) | Medium | Medium |
| **P1** | Forum miner robustness | Medium | Medium |
| **P1** | Security (CI injection, pinning) | Low | Medium |
| **P2** | Code quality tooling (ruff, mypy) | Low | Medium |
| **P2** | pyproject.toml + proper packaging | Low | Low |
| **P2** | CI/CD expansion | Medium | Low |
| **P2** | Documentation gaps | Low | Low |
