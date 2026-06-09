// buglens-app.jsx
// Main application: idle → loading → results, with Tweaks for style + layout.

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "#FF8A3D",
  "theme": "dark",
  "cardLayout": "grid",
  "density": "regular",
  "showVision": true
}/*EDITMODE-END*/;

const LOAD_STAGES = [
  { k: "upload", label: "Uploading screenshot", ms: 500 },
  { k: "vision", label: "Reading with MiniCPM-V 4.6", sub: "vision · OCR", ms: 1100 },
  { k: "structure", label: "Structuring report", sub: "small LLM · strict JSON", ms: 1000 },
];

function useToasts() {
  const [toasts, setToasts] = React.useState([]);
  const push = React.useCallback((msg) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, msg }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 2600);
  }, []);
  return [toasts, push];
}

// ── Header ──
function Header({ onReset, view }) {
  return (
    <header className="bl-top">
      <button className="bl-top-brand" onClick={onReset} title="Start over">
        <Wordmark size={24} />
      </button>
      <div className="bl-top-tag">Screenshot → filed bug, in one read</div>
      <div className="bl-top-right">
        <span className="bl-model-chip"><i className="bl-live" />MiniCPM-V 4.6 · 1.3B</span>
      </div>
    </header>
  );
}

// ── Idle / upload + gallery ──
function IdleView({ onPick }) {
  const onDrop = (ev) => { ev.preventDefault(); onPick(EXAMPLES[0].id); };
  return (
    <div className="bl-idle">
      <div className="bl-hero">
        <div className="bl-hero-lens"><Logo size={58} /></div>
        <h1 className="bl-hero-h">Turn a bug screenshot into a filed report.</h1>
        <p className="bl-hero-sub">
          BugLens reads the image, writes a Jira-ready report, lists the regression tests
          and edge cases — and tells you exactly what it <b>can’t</b> see.
        </p>
        <div
          className="bl-drop"
          onDragOver={(e) => e.preventDefault()}
          onDrop={onDrop}
          onClick={() => onPick(EXAMPLES[0].id)}
        >
          <div className="bl-drop-ic">⤢</div>
          <div className="bl-drop-t">Drop a screenshot</div>
          <div className="bl-drop-s">PNG or JPG · or pick an example below</div>
        </div>
      </div>

      <div className="bl-gallery">
        <div className="bl-gallery-h">
          <span>Example screenshots</span>
          <span className="bl-gallery-hint">click to analyze</span>
        </div>
        <div className="bl-gallery-grid">
          {EXAMPLES.map((e) => (
            <button key={e.id} className="bl-ex" onClick={() => onPick(e.id)}>
              <div className="bl-ex-thumb">
                <MockScreen id={e.id} />
                <span className="bl-ex-scrim" />
                <SeverityBadge level={e.severity} />
              </div>
              <div className="bl-ex-meta">
                <div className="bl-ex-app">{e.app}</div>
                <div className="bl-ex-title">{e.title}</div>
                <div className="bl-ex-blurb">{e.blurb}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Loading ──
function LoadingView({ example, stageIdx }) {
  return (
    <div className="bl-loading">
      <div className="bl-loading-shot">
        <MockScreen id={example.id} />
        <div className="bl-scan" />
      </div>
      <div className="bl-loading-side">
        <div className="bl-load-file">{example.captured}</div>
        <ul className="bl-stages">
          {LOAD_STAGES.map((s, i) => {
            const state = i < stageIdx ? "done" : i === stageIdx ? "active" : "todo";
            return (
              <li key={s.k} data-state={state}>
                <span className="bl-stage-dot">
                  {state === "done" ? "✓" : state === "active" ? <span className="bl-mini-spin" /> : ""}
                </span>
                <div>
                  <div className="bl-stage-l">{s.label}</div>
                  {s.sub && <div className="bl-stage-sub">{s.sub}</div>}
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}

// ── Results ──
function ResultsView({ example, layout, showVision, onReset, push }) {
  const cards = [
    <BugReportCard e={example} key="report" />,
    <MissingInfoCard e={example} key="missing" />,
    <RegressionCard e={example} key="tests" />,
    <EdgeCard e={example} key="edges" />,
  ];
  const tabsMeta = [
    { k: "report", label: "Report" },
    { k: "missing", label: "Missing info" },
    { k: "tests", label: "Tests" },
    { k: "edges", label: "Edge cases" },
  ];
  const [tab, setTab] = React.useState(0);

  return (
    <div className="bl-results">
      {/* Left rail: the lens */}
      <aside className="bl-lens">
        <div className="bl-lens-shot">
          <MockScreen id={example.id} />
        </div>
        <div className="bl-lens-file">{example.captured}</div>
        {showVision && (
          <div className="bl-vision">
            <div className="bl-vision-h"><span className="bl-vision-ic">◎</span> What BugLens saw</div>
            <ul>
              {example.visionRead.map((v, i) => <li key={i}>{v}</li>)}
            </ul>
          </div>
        )}
        <Btn kind="ghost" full onClick={onReset} icon="←">Analyze another</Btn>
      </aside>

      {/* Right: structured output */}
      <main className="bl-output">
        {layout === "tabbed" ? (
          <>
            <div className="bl-tabs">
              {tabsMeta.map((t, i) => (
                <button key={t.k} className={i === tab ? "is-on" : ""} onClick={() => setTab(i)}>
                  {t.label}
                </button>
              ))}
            </div>
            <div className="bl-tabpane">{cards[tab]}</div>
          </>
        ) : (
          <div className={`bl-cards bl-cards-${layout}`}>{cards}</div>
        )}

        <div className="bl-export">
          <span className="bl-export-l">Export</span>
          <Btn kind="primary" icon="↗" onClick={() => push("Sent to Jira — JIRA-4821 created (demo)")}>Create Jira issue</Btn>
          <Btn kind="ghost" icon="⌥" onClick={() => push("Opened GitHub issue draft (demo)")}>GitHub issue</Btn>
          <Btn kind="ghost" icon="▤" onClick={() => push("Downloaded buglens-report.csv (demo)")}>CSV</Btn>
        </div>
      </main>
    </div>
  );
}

// ── App ──
function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [view, setView] = React.useState("idle"); // idle | loading | results
  const [activeId, setActiveId] = React.useState(null);
  const [report, setReport] = React.useState(null); // structured result from the backend
  const [stageIdx, setStageIdx] = React.useState(0);
  const [toasts, push] = useToasts();
  const timers = React.useRef([]);

  const clearTimers = () => { timers.current.forEach(clearTimeout); timers.current = []; };

  const pick = (id) => {
    clearTimers();
    setActiveId(id);
    setReport(null);
    setStageIdx(0);
    setView("loading");
    // Ask the backend to analyze (mock mode returns the matching example).
    fetch(`/api/analyze?id=${encodeURIComponent(id)}`)
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setReport)
      .catch(() => push("Analysis failed — backend unavailable"));
    let acc = 0;
    LOAD_STAGES.forEach((s, i) => {
      acc += s.ms;
      timers.current.push(setTimeout(() => setStageIdx(i + 1), acc));
    });
    timers.current.push(setTimeout(() => setView("results"), acc + 250));
  };

  const reset = () => { clearTimers(); setView("idle"); setActiveId(null); setReport(null); };

  React.useEffect(() => () => clearTimers(), []);

  const example = EXAMPLES.find((e) => e.id === activeId);
  const accent = Array.isArray(t.accent) ? t.accent[0] : t.accent;

  return (
    <div className="bl-app" data-theme={t.theme} data-density={t.density}
         style={{ "--accent": accent }}>
      <Header onReset={reset} view={view} />
      <div className="bl-stage-wrap">
        {view === "idle" && <IdleView onPick={pick} />}
        {view === "loading" && example && <LoadingView example={example} stageIdx={stageIdx} />}
        {view === "results" && report && (
          <ResultsView example={report} layout={t.cardLayout} showVision={t.showVision}
                       onReset={reset} push={push} />
        )}
      </div>

      <div className="bl-toasts">
        {toasts.map((x) => <div key={x.id} className="bl-toast">{x.msg}</div>)}
      </div>

      <TweaksPanel title="Tweaks">
        <TweakSection label="Style" />
        <TweakColor label="Accent" value={t.accent}
          options={["#FF8A3D", "#4C8DFF", "#37C99E", "#A878FF"]}
          onChange={(v) => setTweak("accent", v)} />
        <TweakRadio label="Theme" value={t.theme} options={["dark", "light"]}
          onChange={(v) => setTweak("theme", v)} />
        <TweakSection label="Results layout" />
        <TweakRadio label="Cards" value={t.cardLayout}
          options={[{ value: "grid", label: "Grid" }, { value: "column", label: "Column" }, { value: "tabbed", label: "Tabs" }]}
          onChange={(v) => setTweak("cardLayout", v)} />
        <TweakRadio label="Density" value={t.density} options={["compact", "regular", "comfy"]}
          onChange={(v) => setTweak("density", v)} />
        <TweakToggle label="Show “what I saw”" value={t.showVision}
          onChange={(v) => setTweak("showVision", v)} />
        <TweakSection label="Jump to" />
        <div style={{ display: "flex", gap: 6 }}>
          <TweakButton label="Upload" secondary onClick={reset} />
          <TweakButton label="Results" onClick={() => pick(activeId || EXAMPLES[0].id)} />
        </div>
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
