// buglens-cards.jsx
// The four structured-output cards. Each is self-contained and copy-able.

// ── plaintext builders for the copy actions ──
function reportToMarkdown(e) {
  return [
    `# ${e.title}`,
    ``,
    `**Severity:** ${SEVERITY[e.severity].label} — ${e.severityWhy}`,
    ``,
    `## Summary`,
    e.summary,
    ``,
    `## Steps to reproduce`,
    ...e.steps.map((s, i) => `${i + 1}. ${s}`),
    ``,
    `## Expected`,
    e.expected,
    ``,
    `## Actual`,
    e.actual,
    ``,
    `## Environment`,
    ...e.env.map((r) => `- ${r.k}: ${r.v}`),
  ].join("\n");
}
function testsToText(e) {
  return e.tests
    .map((t) => `${t.id} — ${t.title}\n  Given ${t.given}\n  When ${t.when}\n  Then ${t.then}`)
    .join("\n\n");
}

function CardShell({ kind, glyph, kicker, title, action, children, accent }) {
  return (
    <section className="bl-card" data-kind={kind} style={accent ? { "--card-accent": accent } : undefined}>
      <header className="bl-card-h">
        <span className="bl-card-ic">{glyph}</span>
        <div className="bl-card-ht">
          <div className="bl-kicker">{kicker}</div>
          <h3>{title}</h3>
        </div>
        {action}
      </header>
      <div className="bl-card-b">{children}</div>
    </section>
  );
}

// ── 1. Bug report ──
function BugReportCard({ e }) {
  return (
    <CardShell
      kind="report"
      glyph="❏"
      kicker="Bug report · paste into Jira"
      title="Structured report"
      action={<CopyBtn getText={() => reportToMarkdown(e)} label="Copy" />}
    >
      <div className="bl-rep-top">
        <SeverityBadge level={e.severity} />
        <span className="bl-rep-why">{e.severityWhy}</span>
      </div>
      <p className="bl-summary">{e.summary}</p>

      <div className="bl-sublabel">Steps to reproduce</div>
      <ol className="bl-steps">
        {e.steps.map((s, i) => <li key={i}>{s}</li>)}
      </ol>

      <div className="bl-ea">
        <div className="bl-ea-col bl-ea-exp">
          <div className="bl-ea-lbl">Expected</div>
          <p>{e.expected}</p>
        </div>
        <div className="bl-ea-col bl-ea-act">
          <div className="bl-ea-lbl">Actual</div>
          <p>{e.actual}</p>
        </div>
      </div>

      <div className="bl-sublabel">Environment</div>
      <div className="bl-env">
        {e.env.map((r, i) => (
          <div className="bl-env-row" key={i} data-known={r.known ? "1" : "0"}>
            <span className="bl-env-k">{r.k}</span>
            <span className="bl-env-v">{r.v}</span>
          </div>
        ))}
      </div>
    </CardShell>
  );
}

// ── 2. Missing information — THE DIFFERENTIATOR ──
function MissingInfoCard({ e }) {
  const [confirmed, setConfirmed] = React.useState({});
  const total = e.missing.length;
  const done = Object.values(confirmed).filter(Boolean).length;
  return (
    <CardShell
      kind="missing"
      glyph="◎"
      kicker="What I can’t see — confirm before filing"
      title="Missing information"
      accent="var(--accent)"
      action={<span className="bl-progress">{done}/{total} confirmed</span>}
    >
      <p className="bl-honest">
        A screenshot only shows the surface. BugLens flags what it <b>cannot</b> determine
        rather than guessing — verify these to complete the report.
      </p>
      <ul className="bl-missing">
        {e.missing.map((m, i) => {
          const on = !!confirmed[i];
          return (
            <li key={i} className={on ? "is-on" : ""}>
              <button
                className="bl-check"
                aria-pressed={on}
                onClick={() => setConfirmed((c) => ({ ...c, [i]: !c[i] }))}
              >
                {on ? "✓" : ""}
              </button>
              <div className="bl-missing-t">
                <div className="bl-missing-q">{m.q}</div>
                <div className="bl-missing-w">{m.why}</div>
              </div>
            </li>
          );
        })}
      </ul>
    </CardShell>
  );
}

// ── 3. Regression tests ──
function RegressionCard({ e }) {
  return (
    <CardShell
      kind="tests"
      glyph="⊞"
      kicker="Regression tests · QA-runnable"
      title="Suggested test cases"
      action={<CopyBtn getText={() => testsToText(e)} label="Copy" />}
    >
      <ul className="bl-tests">
        {e.tests.map((t) => (
          <li key={t.id} className="bl-test">
            <div className="bl-test-h">
              <span className="bl-test-id">{t.id}</span>
              <span className="bl-test-title">{t.title}</span>
            </div>
            <dl className="bl-gwt">
              <div><dt>Given</dt><dd>{t.given}</dd></div>
              <div><dt>When</dt><dd>{t.when}</dd></div>
              <div><dt>Then</dt><dd>{t.then}</dd></div>
            </dl>
          </li>
        ))}
      </ul>
    </CardShell>
  );
}

// ── 4. Edge cases ──
function EdgeCard({ e }) {
  return (
    <CardShell
      kind="edges"
      glyph="⬡"
      kicker="Edge cases · worth checking"
      title="Edge cases"
    >
      <ul className="bl-edges">
        {e.edges.map((c, i) => (
          <li key={i}>
            <span className="bl-edge-marker" />
            <div>
              <div className="bl-edge-t">{c.t}</div>
              <div className="bl-edge-d">{c.d}</div>
            </div>
          </li>
        ))}
      </ul>
    </CardShell>
  );
}

Object.assign(window, { BugReportCard, MissingInfoCard, RegressionCard, EdgeCard });
