"""Built-in BugLens examples as validated reports.

These are the same hand-written examples the `buglens-ui` prototype ships, now
expressed through the canonical `BugReport` contract. In mock backend mode the
app serves these directly; once the model pipeline lands they become the
golden fixtures the structuring output is compared against.
"""

from __future__ import annotations

from buglens.schema import BugReport

EXAMPLES: dict[str, BugReport] = {
    "payment": BugReport(
        id="payment",
        app="Checkout",
        title="Pay button stays disabled with a valid card",
        blurb="Card fields filled, but “Pay $49.00” won’t enable.",
        severity="high",
        severity_why="Blocks revenue on the final checkout step; no client-side workaround for the user.",
        captured="checkout-pay-disabled.png",
        vision_read=[
            "A checkout panel titled “Payment”. Card number, expiry (12 / 27) and CVC (123) fields all appear filled.",
            "A primary button labelled “Pay $49.00” is rendered in a low-contrast grey, consistent with a disabled state.",
            "A red helper line under the card field reads “Card number looks incomplete”.",
            "No network panel, console, or browser chrome is visible in the image.",
        ],
        summary=(
            "On the checkout payment step, the card number, expiry and CVC fields appear complete, but the "
            "primary “Pay $49.00” button remains in a disabled/greyed state. An inline validation message "
            "“Card number looks incomplete” is shown beneath the card field, suggesting the card-number "
            "validator is rejecting input the user believes is valid."
        ),
        steps=[
            "Open the checkout flow and proceed to the Payment step.",
            "Enter card number 4242 4242 4242 4242, expiry 12 / 27, CVC 123.",
            "Observe the inline message “Card number looks incomplete”.",
            "Observe that “Pay $49.00” stays disabled.",
        ],
        expected="With a valid 16-digit card number, the validation message clears and “Pay $49.00” becomes enabled.",
        actual="Validation message persists and the Pay button never enables, blocking completion of the purchase.",
        env=[
            {"key": "Visible in screenshot", "value": "Payment step, $49.00 total", "known": True},
            {"key": "Browser / OS", "value": "not visible — please confirm", "known": False},
            {"key": "Card type used", "value": "not visible — please confirm", "known": False},
        ],
        missing_info=[
            {
                "question": "Does the field strip spaces before validation?",
                "why": "If the validator counts the spaces in “4242 4242 …” as part of the length, a 16-digit card reads as 19 chars and fails. Can’t confirm from a static image — needs the input handler.",
            },
            {
                "question": "What browser & version is this?",
                "why": "Autofill formatting differs across Chrome/Safari and can inject non-breaking spaces. Not visible in the screenshot.",
            },
            {
                "question": "Is the Pay button gated on a separate form-valid flag?",
                "why": "The button could be disabled by overall form state, not the card field alone. Needs the component’s enable condition.",
            },
        ],
        regression_tests=[
            {
                "id": "REG-001",
                "title": "Spaced card number enables Pay",
                "given": "I am on the Payment step",
                "when": "I enter “4242 4242 4242 4242”, a valid expiry and CVC",
                "then": "no validation error shows and the Pay button is enabled",
            },
            {
                "id": "REG-002",
                "title": "Validator strips formatting",
                "given": "a card number with spaces or dashes",
                "when": "the field loses focus",
                "then": "the stored value contains digits only and length checks pass",
            },
            {
                "id": "REG-003",
                "title": "Pay disabled while genuinely incomplete",
                "given": "a 12-digit partial card number",
                "when": "I review the form",
                "then": "the Pay button stays disabled and the incomplete message shows",
            },
        ],
        edge_cases=[
            {"title": "Amex 15-digit cards", "detail": "A 16-digit length rule will wrongly reject valid Amex numbers."},
            {"title": "Browser autofill", "detail": "Autofilled values may not fire the same input events as typing."},
            {"title": "Trailing whitespace", "detail": "A pasted number with a trailing space can pass length but fail Luhn."},
            {"title": "Paste vs type", "detail": "Pasting may bypass per-keystroke formatting that strips spaces."},
        ],
    ),
    "dashboard": BugReport(
        id="dashboard",
        app="Analytics",
        title="Revenue chart spins forever after date change",
        blurb="Switching the range to “Last 90 days” never resolves.",
        severity="medium",
        severity_why="Core dashboard widget unusable for a common range; other widgets still load.",
        captured="analytics-chart-spinner.png",
        vision_read=[
            "An analytics dashboard with a sidebar and four metric tiles across the top (Revenue, Orders, AOV, Refunds).",
            "The large “Revenue over time” panel shows a centered loading spinner and no chart.",
            "A date-range control in the top right reads “Last 90 days”.",
            "The surrounding tiles show numbers, so the page itself has loaded.",
        ],
        summary=(
            "On the Analytics dashboard, selecting the “Last 90 days” range leaves the main “Revenue over time” "
            "chart stuck on its loading spinner indefinitely, while the summary tiles around it populate normally. "
            "This points to a failure isolated to the time-series request for the longer range rather than a full "
            "page-load failure."
        ),
        steps=[
            "Open the Analytics dashboard (default range loads fine).",
            "Open the date-range control in the top right.",
            "Select “Last 90 days”.",
            "Observe the Revenue chart spinner never resolves.",
        ],
        expected="The chart fetches the 90-day series and renders within a few seconds, or shows an error state if the request fails.",
        actual="The spinner persists with no chart and no error message; the widget is stuck.",
        env=[
            {"key": "Visible in screenshot", "value": "“Last 90 days” selected, spinner shown", "known": True},
            {"key": "Network response", "value": "not visible — please confirm", "known": False},
            {"key": "Console errors", "value": "not visible — please confirm", "known": False},
        ],
        missing_info=[
            {
                "question": "Did the 90-day request return, error, or hang?",
                "why": "A spinner with no error usually means the promise never settled (timeout/aborted) — but the network tab isn’t in the image, so this is unconfirmed.",
            },
            {
                "question": "Is there a row-count or payload limit?",
                "why": "90 days of hourly points may exceed a server cap that silently truncates or 500s. Can’t tell from the screenshot.",
            },
            {
                "question": "Does a shorter custom range (e.g. 60 days) also hang?",
                "why": "Needed to tell whether it’s the 90-day preset specifically or any range past a threshold.",
            },
        ],
        regression_tests=[
            {
                "id": "REG-011",
                "title": "90-day range renders",
                "given": "I am on the Analytics dashboard",
                "when": "I select “Last 90 days”",
                "then": "the Revenue chart renders a series within the timeout window",
            },
            {
                "id": "REG-012",
                "title": "Failed fetch shows an error, not a spinner",
                "given": "the time-series request errors or times out",
                "when": "I wait past the timeout",
                "then": "the chart shows a retryable error state instead of an endless spinner",
            },
            {
                "id": "REG-013",
                "title": "Range switching cancels stale requests",
                "given": "a 90-day request is in flight",
                "when": "I switch to “Last 7 days”",
                "then": "the in-flight request is aborted and the 7-day series renders",
            },
        ],
        edge_cases=[
            {"title": "Empty range", "detail": "A new account with no 90-day history should show an empty state, not a spinner."},
            {"title": "DST boundary", "detail": "Spanning a clock change can produce a duplicate or missing hour bucket."},
            {"title": "Slow network", "detail": "On 3G the request may legitimately take long — distinguish slow from hung."},
            {"title": "Rapid switching", "detail": "Toggling ranges fast can race responses and render stale data."},
        ],
    ),
    "signup": BugReport(
        id="signup",
        app="Sign up",
        title="Password error overlaps the input on mobile",
        blurb="Error text renders on top of the field, unreadable.",
        severity="low",
        severity_why="Cosmetic but hurts conversion on the signup form; field is still usable.",
        captured="signup-error-overlap.png",
        vision_read=[
            "A mobile signup form with Email and Password fields and a “Create account” button.",
            "Red error text “Use at least 8 characters” appears to overlap the lower edge of the Password input rather than sitting below it.",
            "The layout looks like a narrow mobile viewport.",
            "Device model and exact viewport width are not indicated in the image.",
        ],
        summary=(
            "On the mobile signup form, the password validation message “Use at least 8 characters” renders "
            "overlapping the bottom edge of the Password input instead of in the space beneath it. The field remains "
            "functional, but the collision makes both the error and the field value hard to read — a layout/spacing "
            "issue at narrow widths."
        ),
        steps=[
            "Open the signup form on a narrow mobile viewport.",
            "Enter a password shorter than 8 characters.",
            "Trigger validation (blur or submit).",
            "Observe the error text overlapping the input.",
        ],
        expected="The error message appears in a reserved space directly below the field without overlapping it.",
        actual="The error text is absolutely positioned over the input’s lower edge, colliding with the field.",
        env=[
            {"key": "Visible in screenshot", "value": "Mobile signup, password error", "known": True},
            {"key": "Device / viewport width", "value": "not visible — please confirm", "known": False},
            {"key": "Browser", "value": "not visible — please confirm", "known": False},
        ],
        missing_info=[
            {
                "question": "Is the error absolutely positioned?",
                "why": "Overlap usually means the message is taken out of flow with no reserved height. Confirming needs the CSS, not the picture.",
            },
            {
                "question": "At what width does it start overlapping?",
                "why": "Could be every mobile width or only below a breakpoint. The exact viewport isn’t shown.",
            },
            {
                "question": "Does a two-line error wrap into the field?",
                "why": "A longer message may make the collision worse; can’t tell from a single short string.",
            },
        ],
        regression_tests=[
            {
                "id": "REG-021",
                "title": "Error sits below the field",
                "given": "a mobile viewport of 360px",
                "when": "a validation error shows",
                "then": "the message renders below the input with no overlap",
            },
            {
                "id": "REG-022",
                "title": "Field reserves error space",
                "given": "any input with validation",
                "when": "no error is present",
                "then": "space is reserved so showing an error does not shift surrounding layout",
            },
            {
                "id": "REG-023",
                "title": "Two-line errors don’t collide",
                "given": "a long validation message",
                "when": "it wraps to two lines",
                "then": "the field and message remain fully readable",
            },
        ],
        edge_cases=[
            {"title": "320px screens", "detail": "The smallest common phones are most likely to collide."},
            {"title": "Large text setting", "detail": "OS-level font scaling grows the error and worsens overlap."},
            {"title": "RTL languages", "detail": "Translated errors are often longer and wrap differently."},
            {"title": "Landscape", "detail": "Short viewport height can push the error under the keyboard."},
        ],
    ),
    "settings": BugReport(
        id="settings",
        app="Settings",
        title="Broken avatar collapses the profile header",
        blurb="Image fails to load and the layout jumps.",
        severity="medium",
        severity_why="Visible on every visit to Settings for affected users; degrades trust in the page.",
        captured="settings-broken-avatar.png",
        vision_read=[
            "A Settings → Profile page with a header area for an avatar, name and email.",
            "Where the avatar should be, a broken-image placeholder icon is shown.",
            "The name and email text appear shifted up/left, as if the avatar’s box has no reserved size.",
            "No URL or network detail for the image is visible in the screenshot.",
        ],
        summary=(
            "On the Settings profile header, the user avatar fails to load and falls back to the browser’s "
            "broken-image icon. Because the avatar container doesn’t appear to reserve a fixed size, the adjacent "
            "name and email shift position, causing a visible layout jump. The result is a degraded header that "
            "looks broken on every visit for affected users."
        ),
        steps=[
            "Open Settings → Profile for a user whose avatar URL is unreachable.",
            "Observe the broken-image icon in place of the avatar.",
            "Observe the name/email shifting to fill the empty space.",
        ],
        expected="A failed avatar shows a graceful fallback (initials or default) at the same fixed size, with no layout shift.",
        actual="The broken-image icon shows and the surrounding text reflows, jumping the layout.",
        env=[
            {"key": "Visible in screenshot", "value": "Profile header, broken avatar", "known": True},
            {"key": "Image URL / status code", "value": "not visible — please confirm", "known": False},
            {"key": "Affected users", "value": "not visible — please confirm", "known": False},
        ],
        missing_info=[
            {
                "question": "Why did the image fail — 404, CORS, or expired URL?",
                "why": "The fix differs for each, and the status code isn’t in the screenshot.",
            },
            {
                "question": "Does the avatar have an onError fallback?",
                "why": "A broken-image icon suggests no error handler; confirming needs the component code.",
            },
            {
                "question": "Is the container sized independently of the image?",
                "why": "The layout jump implies the box collapses when the image is missing — needs the CSS.",
            },
        ],
        regression_tests=[
            {
                "id": "REG-031",
                "title": "Failed avatar falls back gracefully",
                "given": "an avatar URL that returns an error",
                "when": "the profile header renders",
                "then": "a default/initials avatar shows at the correct size",
            },
            {
                "id": "REG-032",
                "title": "No layout shift on image failure",
                "given": "the avatar fails to load",
                "when": "the header renders",
                "then": "the name and email stay in the same position (reserved box)",
            },
            {
                "id": "REG-033",
                "title": "Broken-image icon never shown",
                "given": "any avatar load failure",
                "when": "the page renders",
                "then": "the native broken-image icon is never visible to the user",
            },
        ],
        edge_cases=[
            {"title": "Slow image load", "detail": "A reserved box should hold space while the image is still loading."},
            {"title": "Expired signed URL", "detail": "Time-limited URLs can 403 after a while and need refresh logic."},
            {"title": "No avatar set", "detail": "Brand-new users have no image at all and need the same fallback."},
            {"title": "Transparent PNG", "detail": "A valid but empty image can look broken — distinct from a load failure."},
        ],
    ),
}


def list_examples() -> list[dict]:
    """Gallery metadata for every example, in display order."""

    return [
        {
            "id": report.id,
            "app": report.app,
            "title": report.title,
            "blurb": report.blurb,
            "severity": report.severity.value,
            "captured": report.captured,
        }
        for report in EXAMPLES.values()
    ]


def get_example(example_id: str) -> BugReport | None:
    """Return the report for an example id, or None if unknown."""

    return EXAMPLES.get(example_id)
