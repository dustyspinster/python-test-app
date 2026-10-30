# python-test-app

[![Tests](https://github.com/dustyspinster/python-test-app/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/dustyspinster/python-test-app/actions/workflows/tests.yml)

**[View the latest test reports](https://dustyspinster.github.io/python-test-app/)** from `main`, published by CI after every push and nightly run.

Automated UI and API tests written in Python with pytest, with user-facing behavior described in Gherkin and run by [pytest-bdd](https://pytest-bdd.readthedocs.io/):

- **UI tests** drive [Swag Labs](https://www.saucedemo.com), Sauce Labs' demo store, with Selenium and Chrome: login, logout, product sorting, product details, cart, checkout, accessibility, response times, and the deliberate bugs of Swag Labs' `problem_user` and `error_user` accounts, all written as Gherkin scenarios.
- **API tests** exercise the [Restful-booker](https://restful-booker.herokuapp.com) API with `requests`: authentication, and creating, reading, searching, updating, partially updating and deleting bookings, with every JSON response validated against a schema. Requests go through a client-side rate limiter.

Tests run on every push and pull request, nightly at 9:00 UTC, and on demand through GitHub Actions.

## What this demonstrates

- **Behavior-driven scenarios:** [feature files](tests/ui/features/) in Gherkin describe login, logout, product sorting, product details, cart, checkout, known bugs and the [booking lifecycle](tests/api/features/bookings.feature) in plain language a product owner can review, using Backgrounds, Scenario Outlines with Examples tables, and step definitions shared across features.
- **Page object model:** step definitions describe user actions, while locators and waits live in [`pages/`](pages/).
- **UI and API testing:** browser tests with Selenium, and REST API tests with `requests` covering authentication, create, read, search, update, partial update and delete, plus negative cases such as missing records, bad credentials, unauthorized changes, malformed requests and invalid booking data.
- **API contract checks:** strict [JSON schemas](tests/api/schemas.py) for every response shape, checking required fields, exact types, real dates and no unexpected fields, with offline tests proving the schemas reject bad data.
- **Reliable tests:** explicit waits instead of sleeps, and every click or keystroke is checked for its effect rather than assumed to work.
- **Accessibility testing:** every page is scanned with [axe-core](https://github.com/dequelabs/axe-core) against the WCAG 2.0–2.2 Level A and AA rules, the standard behind Section 508. Keyboard access is checked separately, because automated scans miss it: the scan reports Swag Labs clean, yet two WCAG failures were found by checking focus directly (see Known issues).
- **Rate limiting:** every API request passes through a [token-bucket rate limiter](tests/api/rate_limiter.py) (10 requests per second, bursts up to 20) that makes requests wait rather than fail. Its [Gherkin scenarios](tests/api/features/rate_limiter.feature) run against a fake clock, so the timings are exact and the tests take milliseconds.
- **Performance checks:** response-time scenarios with limits in plain language ("within 3 seconds"), timed with the browser's own clock from when the page receives each action, comparing a normal account with Swag Labs' deliberately slow one.
- **Parallel execution:** [pytest-xdist](https://pytest-xdist.readthedocs.io/) spreads each suite across one worker per CPU core, each UI worker with its own Chrome. Every test sets up its own browser session and data, so tests can run in any order on any worker. On a 4-core machine the UI suite drops from about 65 seconds to 19.
- **Continuous integration:** GitHub Actions runs linting, API tests and headless UI tests as separate parallel jobs on every push, pull request and night, uploads an HTML report for each test job, and publishes the reports from `main` to GitHub Pages.
- **Code quality:** type-hinted page objects, with linting and formatting enforced by [ruff](https://docs.astral.sh/ruff/) in CI.
- **Debuggable failures:** each failed UI test saves a screenshot, the URL, the browser console log and the page source.
- **Root cause analysis:** a CI-only failure was traced, experiment by experiment, to headless Chrome dropping real input, then worked around and [reported to Chromium](https://issues.chromium.org/issues/571158512). Read the [case study](docs/chrome-dropped-input.md).

## Project layout

```
pages/                 Page objects for the Swag Labs UI
  interactions.py      Click and type helpers that confirm each action took effect (see Known issues)
  timing.py            Response-time measurement with the browser's own clock
tests/ui/              UI tests: login, logout, sorting, product details, cart, checkout, accessibility,
                       performance, problem_user and error_user bugs
  features/            Gherkin feature files, one per area
  conftest.py          Step definitions shared by more than one feature
  test_*.py            Each module runs one feature file and holds its own step definitions
tests/api/             API tests for Restful-booker, with their own fixtures
  features/            Gherkin scenarios for the booking lifecycle and its permissions
  test_bookings.py     Plain pytest checks for listing, search, authentication and token retry
  test_validation.py   How the API handles bad input and missing records, including its known bugs
  rate_limiter.py      Keeps API requests within 10 per second, with bursts up to 20
  test_rate_limiter.py The rate limiter's scenarios, run against a fake clock
  schemas.py           JSON schemas for each response shape, and the validation helper
conftest.py            Chrome setup, a logged-in driver fixture, and failure capture
pyproject.toml         ruff lint and format settings
.github/workflows/     CI workflow: lint, API tests, UI tests, and report publishing
.github/scripts/       Builds the index page for the published reports
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

Run in parallel, one worker per CPU core, as CI does:

```
pytest -n auto
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

Each Gherkin scenario runs as an ordinary pytest test, named after the scenario, so the commands above run them too. To run one feature, run its module:

```
pytest tests/ui/test_checkout.py
```

### Writing scenarios

Feature files describe what the user does and sees, not how the page is built: no locators, URLs or waits. Those belong in the step definitions and page objects. Each `test_*.py` module calls `scenarios()` on its feature file and defines the steps only that feature uses; steps used by several features, such as `Given I am logged in`, live in `conftest.py`. The API scenarios cover what a product owner cares about, who can create, change and cancel a booking, while plain pytest tests in `test_bookings.py` cover contract details such as search results and the authentication endpoint.

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

In CI, download these from the run's **failure-screenshots** artifact. The **ui-test-report** and **api-test-report** artifacts have the full HTML report for each test job. For `main`, the same reports are also [published to GitHub Pages](https://dustyspinster.github.io/python-test-app/).

## Known issues

### Headless Chrome intermittently drops clicks and typing

**Symptom.** A UI test fails because a click or keystroke had no effect: Checkout never opens the checkout page, or typed text never appears in a form field. Selenium reports no error, and retrying in the same browser session doesn't help. It mostly showed up in GitHub Actions, but it also happens locally, in bursts: some CI runs lost input in every session, others in none.

**Cause.** We traced this to Chrome itself. When it happens, the page is healthy and ready for input: the element is visible and uncovered, the tab has focus, and the app's click handlers are attached. But no input event reaches the page at all. A click sent directly through Chrome's DevTools protocol, bypassing ChromeDriver, is lost the same way. A JavaScript `element.click()` on the same element works. We reproduced it on Chrome 153 and 154, on Linux in CI and on Windows. We reported it as [Chromium issue 571158512](https://issues.chromium.org/issues/571158512) in October 2026; it's not yet confirmed.

**Workaround.** The page objects never call Selenium's `click()`, `send_keys()` or `Select` directly. They go through `click()`, `type_text()` and `choose_option()` in [`pages/interactions.py`](pages/interactions.py), which:

1. use real input first, as a user would
2. confirm the action took effect: the page navigated, a button changed, the field kept its text, the dropdown kept its choice, or an error appeared
3. only if nothing happened, perform the same action with JavaScript and log a warning

Real input is always tried first, so the tests still catch genuine problems such as hidden or covered elements. When adding a page object, use these helpers instead of calling `click()`, `send_keys()` or `Select` directly.

**How to tell when it fires.** The fallback logs a warning like this:

```
WARNING  pages.interactions:interactions.py:76 Clicking ('id', 'checkout') had no effect (Chrome may have dropped it); clicking via JavaScript
```

pytest only prints logs for failing tests by default. To see the warnings for passing tests too, check each test's captured log in the UI test report, or run with live logging:

```
pytest -v -o log_cli=true --log-cli-level=WARNING
```

Live logging doesn't work with parallel workers (`-n`). For a parallel run, add `-rP` instead, which prints each passing test's captured log after the run.

A passing test with these warnings means the fallback handled a dropped input. If the JavaScript attempt has no effect either, the test fails with an error ending in "even via JavaScript": the app itself ignored the action, which is a real bug rather than Chrome's. If Chrome fixes the bug and the warnings stop appearing, the fallback can be removed.

For the full investigation, see the [case study](docs/chrome-dropped-input.md).

### Swag Labs shows some item totals unrounded

**Symptom.** The checkout scenario *Checkout totals the cart with tax* buys the Backpack, Bike Light, Bolt T-Shirt and Fleece Jacket. The order overview shows `Item total: $105.96000000000001` instead of `$105.96`. Tax ($8.48) and the order total ($114.44) are correct.

**Cause.** Swag Labs adds prices as floating-point numbers, which can't store most cents exactly: in JavaScript, `29.99 + 9.99 + 15.99 + 49.99` is `105.96000000000001`. The site rounds the tax and total before displaying them but not the item total. Many carts happen to add up cleanly, which is why the two-item checks didn't catch it; this four-item cart doesn't.

**How the suite handles it.** The scenario is tagged `@known-bug`, which [`tests/ui/conftest.py`](tests/ui/conftest.py) turns into a strict expected failure. It still runs on every build and appears in the report as expected to fail, without failing CI. Only a failed assertion counts as the known bug, so a timeout or crash still fails the test. If Swag Labs fixes the bug, the scenario passes unexpectedly, which fails the build as a reminder to remove the tag. The expected amounts are worked out by hand in the feature file rather than calculated by the test, so the test doesn't repeat the site's mistake.

### Two keyboard accessibility failures the automated scan misses

[`accessibility.feature`](tests/ui/features/accessibility.feature) scans every page with axe-core using the WCAG 2.2 Level A and AA rules. All seven pages pass, but checking keyboard support directly finds two failures, both tagged `@known-bug`:

| Problem | WCAG criterion |
|---|---|
| The shopping cart link can't receive keyboard focus: it's an `<a>` with no `href`, so Tab skips it, even though it's announced to screen readers as a "Cart" button | [2.1.1 Keyboard](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html) (Level A) |
| The Login button looks identical with and without keyboard focus: the site removes the browser's focus outline and adds nothing in its place | [2.4.7 Focus Visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html) (Level AA) |

**Why keyboard support is checked without pressing keys.** Headless Chrome drops simulated key presses the same way it drops clicks (see the first Known issue), so a test that presses Tab and Enter fails at random. Instead, [`pages/accessibility.py`](pages/accessibility.py) checks what keyboard use depends on: whether an element can receive focus, the order Tab moves in, whether the login fields sit in a form that Enter submits, and whether focusing an element changes how it looks. The focus-appearance check only covers the login page, where the browser reliably enters its keyboard-focus state; after a mouse-driven login it often doesn't, which would make the result meaningless.

**What the scan leaves for a person.** axe reports some items it can't decide, such as color contrast on the menu and cart buttons, as needing review. The tests log these as warnings in the report rather than failing. The username and password fields show only the blinking text cursor when focused; W3C's guidance counts that as a focus indicator, so they aren't treated as failures, though a stronger indicator would help.

### Reset App State leaves products marked as in the cart

**Symptom.** After adding a product and choosing **Reset App State** from the menu, the cart badge clears, but the product's button still says **Remove** instead of **Add to cart**, so the page shows the product as in a cart that is now empty.

**How the suite handles it.** The scenario *The app state is reset and fully empties the cart* in [`cart.feature`](tests/ui/features/cart.feature) is tagged `@known-bug`. It checks the badge first, which passes, and then the button, which fails, so the report shows the reset working for the cart but not for the products page.

### `problem_user` has six deliberate bugs

Swag Labs' `problem_user` test account is built to misbehave. [`problem_user.feature`](tests/ui/features/problem_user.feature) describes the correct behavior for each bug, and each scenario is tagged `@known-bug`, so it runs on every build as a strict expected failure, handled the same way as the unrounded item total above. Each bug was confirmed by comparing `problem_user` with `standard_user`:

| Bug | What `problem_user` sees |
|---|---|
| Product images | All six products show the same "404" placeholder image |
| Sorting | Choosing a sort option does nothing; the menu snaps back to Name (A to Z) |
| Add to cart | Does nothing for the Bolt T-Shirt, Fleece Jacket and Red T-Shirt |
| Remove | Does nothing for any product in the cart |
| Product links | Every link opens the next product's page (Backpack opens the Fleece Jacket); the Fleece Jacket, which has the highest product ID, opens "ITEM NOT FOUND" |
| Checkout | Typing a last name overwrites the first name, so checkout fails with "Last Name is required" |

The product-link and "ITEM NOT FOUND" symptoms are one bug: each link points to product ID + 1, and no product has ID 6.

### `error_user` fails on some buttons and fields

Swag Labs' `error_user` account fails in different places from `problem_user`. [`error_user.feature`](tests/ui/features/error_user.feature) describes the correct behavior, with the affected cases tagged `@known-bug`:

| Bug | What `error_user` sees |
|---|---|
| Add to cart on a product's details page | Does nothing for the Bolt T-Shirt, Fleece Jacket and Red T-Shirt; works for the other three |
| Last name at checkout | The field won't take any input, and Continue still moves on with it blank |
| Finish | Does nothing, so the order is never completed |

The Add to cart scenario runs every product, with the three broken ones in their own `Examples:` table tagged `@known-bug`, so the report shows the bug is limited to those products. The Finish scenario opens the order overview directly, so the last name bug can't stop it before it reaches Finish.

### `performance_glitch_user` is slow to show products

**Symptom.** For Swag Labs' `performance_glitch_user` account, logging in takes about 5 seconds to show the products, against well under a second for `standard_user` and `visual_user`. Sorting and returning to the product list are just as slow; adding to the cart is not.

**How the suite handles it.** [`performance.feature`](tests/ui/features/performance.feature) runs each timing scenario for several users, with `performance_glitch_user` in its own `Examples:` table tagged `@known-bug`. The time limit is 3 seconds, far from both the normal times and the glitch, so a slow CI runner doesn't make the result flaky. [`pages/timing.py`](pages/timing.py) times each action with the browser's own clock, from when the page receives the click, so the input fallback described above can't count against the site.

### Restful-booker mishandles some bad input

[`test_validation.py`](tests/api/test_validation.py) checks that the booking API rejects a client's mistakes with a 4xx status. It handles malformed JSON, unsupported response formats and unknown booking IDs correctly, but not these, which run as strict expected failures with the bug as the reason:

| Request | Restful-booker returns | Expected |
|---|---|---|
| A required field missing, or an empty body | 500 Internal Server Error | 400 |
| `totalprice` that isn't a number | 200, saved as `null` | 400 |
| Checkout date before the checkin date | 200, saved | 400 |
| `checkin` that isn't a date | 200, saved | 400 |
| Updating or deleting a booking that doesn't exist | 405 Method Not Allowed | 404 |

The tests expect only what any REST API should do, since Restful-booker publishes no validation rules; negative prices and empty names aren't treated as bugs for the same reason. Any booking the API wrongly saves is deleted when the test ends.

### Restful-booker resets every 10 minutes

The public Restful-booker API [resets itself every 10 minutes](https://restful-booker.herokuapp.com/), which also invalidates login tokens. A test whose token was issued just before a reset gets `403 Forbidden` afterwards. Authorized requests in the API tests go through `AuthedClient` in [`tests/api/conftest.py`](tests/api/conftest.py), which logs in again and retries once on a 403, logging a warning:

```
PATCH https://restful-booker.herokuapp.com/booking/12 returned 403; logging in again and retrying once
```

A real permissions bug fails again on the retry, so it still fails the test. The tests that check unauthorized requests send no token and still expect 403.

## License

[MIT](LICENSE)
