# python-test-app

[![Tests](https://github.com/dustyspinster/python-test-app/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/dustyspinster/python-test-app/actions/workflows/tests.yml)

Automated UI and API tests written in Python with pytest:

- **UI tests** drive [Swag Labs](https://www.saucedemo.com), Sauce Labs' demo store, with Selenium and Chrome: login, cart, and checkout.
- **API tests** exercise the [Restful-booker](https://restful-booker.herokuapp.com) API with `requests`: authentication and booking create, read, update, and delete.

Tests run on every push and pull request, nightly at 9:00 UTC, and on demand through GitHub Actions.

## What this demonstrates

- **Page object model:** UI tests describe user actions, while locators and waits live in [`pages/`](pages/).
- **UI and API testing:** browser tests with Selenium, and REST API tests with `requests` covering authentication, create, read, update and delete, plus negative cases such as missing records, bad credentials and unauthorized changes.
- **Reliable tests:** explicit waits instead of sleeps, and every click or keystroke is checked for its effect rather than assumed to work.
- **Continuous integration:** GitHub Actions runs linting, API tests and headless UI tests as separate parallel jobs on every push, pull request and night, and uploads an HTML report for each test job.
- **Code quality:** type-hinted page objects, with linting and formatting enforced by [ruff](https://docs.astral.sh/ruff/) in CI.
- **Debuggable failures:** each failed UI test saves a screenshot, the URL, the browser console log and the page source.
- **Root cause analysis:** a CI-only failure was traced, experiment by experiment, to headless Chrome dropping real input, then worked around and [reported to Chromium](https://issues.chromium.org/issues/571158512). Read the [case study](docs/chrome-dropped-input.md).

## Project layout

```
pages/                 Page objects for the Swag Labs UI
  interactions.py      Click and type helpers that confirm each action took effect (see Known issues)
tests/ui/              UI tests: login, cart, checkout
tests/api/             API tests for Restful-booker, with their own fixtures
conftest.py            Chrome setup, a logged-in driver fixture, and failure capture
pyproject.toml         ruff lint and format settings
.github/workflows/     CI workflow: lint, API tests and UI tests as separate jobs
```

## Running the tests

Requires Python 3.12 and Google Chrome. Selenium downloads a matching ChromeDriver automatically.

```
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

Run everything:

```
pytest -v
```

Run one part:

```
pytest tests/ui
pytest tests/api
```

Chrome opens a visible window by default. Set `HEADLESS` to any value to run headless, as CI does:

```
HEADLESS=1 pytest -v            # macOS / Linux
$env:HEADLESS = "1"; pytest -v  # Windows PowerShell
```

Dependency versions are pinned in `requirements.txt` so CI doesn't pick up new releases unannounced. To upgrade a package, change its version there and let CI confirm the suite still passes.

## Linting and formatting

CI runs [ruff](https://docs.astral.sh/ruff/) in a separate lint job alongside the tests, with the settings in `pyproject.toml`. To run the same checks locally:

```
ruff check .
ruff format --check .
```

`ruff check --fix .` fixes what it can automatically, and `ruff format .` reformats the code.

## When a UI test fails

`conftest.py` saves four files per failed UI test to `screenshots/`, named after the test:

| File | Contents |
|---|---|
| `.png` | Screenshot of the browser at the moment of failure |
| `.txt` | Current URL and page title |
| `.log` | Browser console messages |
| `.html` | Page source |

In CI, download these from the run's **failure-screenshots** artifact. The **ui-test-report** and **api-test-report** artifacts have the full HTML report for each test job.

## Known issues

### Headless Chrome intermittently drops clicks and typing

**Symptom.** A UI test fails because a click or keystroke had no effect: Checkout never opens the checkout page, or typed text never appears in a form field. Selenium reports no error, and retrying in the same browser session doesn't help. It mostly showed up in GitHub Actions, but it also happens locally, in bursts: some CI runs lost input in every session, others in none.

**Cause.** We traced this to Chrome itself. When it happens, the page is healthy and ready for input: the element is visible and uncovered, the tab has focus, and the app's click handlers are attached. But no input event reaches the page at all. A click sent directly through Chrome's DevTools protocol, bypassing ChromeDriver, is lost the same way. A JavaScript `element.click()` on the same element works. We reproduced it on Chrome 153 and 154, on Linux in CI and on Windows. We reported it as [Chromium issue 571158512](https://issues.chromium.org/issues/571158512) in October 2026; it's not yet confirmed.

**Workaround.** The page objects never call Selenium's `click()` or `send_keys()` directly. They go through `click()` and `type_text()` in [`pages/interactions.py`](pages/interactions.py), which:

1. use real input first, as a user would
2. confirm the action took effect: the page navigated, a button changed, the field kept its text, or an error appeared
3. only if nothing happened, perform the same action with JavaScript and log a warning

Real input is always tried first, so the tests still catch genuine problems such as hidden or covered elements. When adding a page object, use these helpers instead of calling `click()` or `send_keys()` directly.

**How to tell when it fires.** The fallback logs a warning like this:

```
WARNING  pages.interactions:interactions.py:49 Chrome dropped the click on ('id', 'checkout'); clicking via JavaScript
```

pytest only prints logs for failing tests by default. To see the warnings for passing tests too, check each test's captured log in the UI test report, or run with live logging:

```
pytest -v -o log_cli=true --log-cli-level=WARNING
```

A passing test with these warnings means the fallback handled a dropped input. If Chrome fixes the bug and the warnings stop appearing, the fallback can be removed.

For the full investigation, see the [case study](docs/chrome-dropped-input.md).
