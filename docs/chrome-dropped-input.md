# Case study: tracking a CI-only test failure down to a Chrome bug

The checkout tests in this repo passed on my machine and failed in GitHub Actions. This is how Claude and I narrowed that down, step by step, to a bug in headless Chrome: real clicks and keystrokes sometimes never reach the page. It covers the leads that turned out wrong, the evidence that settled it, the workaround, and the upstream bug report.

**Outcome:** the root cause was isolated to Chrome, below both the test code and ChromeDriver. The tests got a targeted workaround that still uses real input first, and the bug was reported as [Chromium issue 571158512](https://issues.chromium.org/issues/571158512).

## The symptom

Every checkout test failed in CI, with two kinds of error:

```
AssertionError: Clicking Checkout never opened checkout-step-one
```

```
AssertionError: Checkout fields did not keep typed values.
Wanted ('', 'User', '97201'), saw ('', '', ''), URL https://www.saucedemo.com/checkout-step-one.html
```

The page objects already waited for each element to be clickable, checked that each action took effect, and retried. The Checkout click was retried three times; typing was retried once a second for 15 seconds. Nothing helped. Locally, the same tests passed!

## Hypotheses that were ruled out

Each of these was a reasonable explanation. Each was tested, not assumed.

| Hypothesis | Test | Result |
|---|---|---|
| CI runs headless; local runs don't | Ran the checkout tests headless locally | 4 passed. Not headless mode. |
| A race with the 404 redirect: Swag Labs is hosted on GitHub Pages, so opening `checkout-step-one.html` directly returns a 404 page that redirects into the app | Recorded the page's URL, navigation entries and DOM every 250 ms after `driver.get` | The redirect finished before `driver.get` returned, and the page stayed put. Not a race. |
| Typing doesn't work at all on the CI runner | A diagnostic test typed into the checkout form four ways in CI: `send_keys`, click then `send_keys`, ActionChains, and a JavaScript setter | All four worked. Typing works on the runner. |
| The site detects automation or headless Chrome | Read the site's JavaScript bundle | It only reads the user agent for its error reporting. The checkout form is a plain React form. |
| Selenium's `clear()` breaks the React form | Bisected locally and caught a failure after `clear()` | Then the same steps passed 12 of 12, and 40 more passed. A coincidence: the failure is intermittent. |
| A regression in Chrome 154 | Ran a probe 10 times each on Chrome 153 and 154, side by side in one CI run | Input was lost in 6 of 10 sessions on 153 and 10 of 10 on 154. Both versions are affected. |
| The site swallows the events | Searched the bundle and CSS for capture-phase listeners on `window`, `stopImmediatePropagation`, `pointer-events` and `inert` | None. |

Two things became clear along the way. **The failure was not CI-only:** it reproduced on Windows too, just less often. **It came in bursts:** some CI runs lost input in every session, others in none. Local runs had simply fallen in quiet periods.

## The evidence

To see what the page actually received, I had Claude write a probe test. It performs the same actions as the failing tests, and before each one installs capture-phase event listeners on `window`, the first place an event arrives. When an action has no effect, it records the page's state, then retries the same action two other ways:

- **Through the DevTools protocol** (`Input.dispatchMouseEvent`), which sends the click straight to Chrome and bypasses ChromeDriver's click handling
- **Through JavaScript** (`element.click()`), which triggers the click from inside the page with no real input involved

One captured failure in CI, Chrome 154. The previous click in the same session, on the cart link, had been delivered normally. The next one, on Checkout, was not:

| Check | Result | Meaning |
|---|---|---|
| Element at the button's center | The Checkout button itself | Nothing was covering it |
| React handlers on the button | `onClick` attached | The app was ready to handle the click |
| `document.hasFocus()` / `visibilityState` | `true` / `visible` | The tab was focused and visible |
| Browser targets | One page, plus Chrome's own UI | No stray tab or popup took the input |
| Events after Selenium's click | **None** | Selenium reported success, but nothing reached the page |
| Events after the DevTools click | **None**, and no effect | Lost below ChromeDriver too |
| JavaScript `element.click()` | Worked, and went to checkout | The page and its handlers were healthy |

That pinned it down. The page was healthy and would respond to anything triggered from inside it, but Chrome was not delivering real input to it, whether it came from ChromeDriver or straight from the DevTools protocol. Once a page got into this state it stayed that way, which is why the retries never recovered.

## The fix

Retrying the same input can't help when the browser is dropping it, so the page objects now go through two helpers in [`pages/interactions.py`](../pages/interactions.py):

1. Use real input first, as a user would.
2. Confirm the action took effect: the page navigated, a button changed, a field kept its text, or an error appeared.
3. Only if nothing happened, perform the same action with JavaScript: `element.click()`, or for text fields the native value setter plus an `input` event, which React accepts. Then log a warning.

Real input is always tried first, so the tests still catch genuine problems such as hidden or covered elements. The fallback replaced the retry loops in the page objects.

**Verification:**

- **Simulated failure:** Claude made Selenium's native `click()`, `send_keys()` and `clear()` no-ops through a pytest plugin, so every action had to go through the fallback. All 13 UI tests passed.
- **Normal runs:** the full suite passed locally, and the checkout and cart tests passed 30 of 30 times in CI. Chrome didn't drop input during those runs, so the fallback wasn't needed there; its log warning shows up in the test report when it fires.

## Reporting it upstream

I searched the Chromium tracker for an existing report. I found a couple and had Claude compare them to our current issue. The closest match, [issue 499572770](https://issues.chromium.org/issues/499572770), is about WebDriver input commands being slow but succeeding, so it's a different bug. I filed [issue 571158512](https://issues.chromium.org/issues/571158512) with the evidence and a standalone reproduction script. The script starts fresh headless sessions against the public demo site, and when input is lost it prints the evidence and confirms the DevTools and JavaScript results.

## Lessons

- **Measure what the page receives, not what the test sent.** Selenium reported every click as successful. Event listeners on the page showed nothing arrived.
- **Retries only help when the failure is transient within a session.** Here it lasted the whole page, so retrying the same input could never work. Choosing a different path did.
- **"Fails only in CI" can be a sampling artifact.** The bug also happened locally, in bursts. The extra probe runs exposed that.
- **Change one variable at a time.** Comparing scenarios and Chrome versions side by side in the same CI run ruled out explanations quickly.
- **Keep workarounds narrow and visible.** The fallback runs only after real input demonstrably failed, and logs every time it does.
- **Push past the quick fix.** After the first attempt to resolve the issue failed, Claude suggested removing the tests from CI to make the build green. I wanted to know why they failed, and pressing for explanations at each step led to the probe experiments and real cause. Skipping the tests would have hidden a bug that also affected local runs. 
