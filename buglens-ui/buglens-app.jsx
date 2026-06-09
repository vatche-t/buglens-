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

// Read a File into a bare base64 string (no data: prefix) for the JSON body.
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1] || "");
    reader.onerror = () => reject(new Error("Could not read the file"));
    reader.readAsDataURL(file);
  });
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
const NOTE_INPUT_STYLE = {
  width: "100%", marginTop: 12, padding: "10px 12px",
  background: "var(--surface-2)", border: "1px solid var(--border)",
  borderRadius: 10, color: "var(--text)", font: "inherit", outline: "none",
};

function IdleView({ onPick, onUpload, note, onNoteChange }) {
  const inputRef = React.useRef(null);
  const handleFiles = (files) => { if (files && files[0]) onUpload(files[0]); };
  const onDrop = (ev) => { ev.preventDefault(); handleFiles(ev.dataTransfer.files); };
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
          onClick={() => inputRef.current && inputRef.current.click()}
        >
          <div className="bl-drop-ic">⤢</div>
          <div className="bl-drop-t">Drop a screenshot</div>
          <div className="bl-drop-s">PNG or JPG · or pick an example below</div>
          <input
            ref={inputRef}
            type="file"
            accept="image/png,image/jpeg"
            style={{ display: "none" }}
            onChange={(e) => { handleFiles(e.target.files); e.target.value = ""; }}
          />
        </div>
        <input
          type="text"
          value={note}
          onChange={(e) => onNoteChange(e.target.value)}
          placeholder="Optional: one-line tester note (e.g. “Pay button does nothing”)"
          style={NOTE_INPUT_STYLE}
          aria-label="Tester note"
        />
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

const SHOT_IMG_STYLE = { width: "100%", height: "100%", objectFit: "contain", display: "block" };

// ── Export helpers (client-side, so they work for examples and live uploads
// alike — the report payload is already in the browser) ──
function severityLabel(s) {
  return (window.SEVERITY && SEVERITY[s] && SEVERITY[s].label) || (s ? s[0].toUpperCase() + s.slice(1) : s);
}

function toJira(e) {
  const L = [
    `h2. ${e.title}`, "",
    `*Severity:* ${severityLabel(e.severity)} — ${e.severityWhy}`,
    `*Component:* ${e.app}`, "",
    "h3. Summary", e.summary, "",
    "h3. Steps to Reproduce",
  ];
  e.steps.forEach((s) => L.push(`# ${s}`));
  L.push("", "h3. Expected", e.expected, "", "h3. Actual", e.actual, "", "h3. Environment");
  e.env.forEach((r) => L.push(`* ${r.k}: ${r.v}${r.known ? "" : " _(unconfirmed)_"}`));
  L.push("", "h3. Missing Info (confirm before filing)");
  e.missing.forEach((m) => L.push(`* ${m.q} — ${m.why}`));
  L.push("", "h3. Regression Tests");
  e.tests.forEach((t) => L.push(`* ${t.id} ${t.title}: given ${t.given}, when ${t.when}, then ${t.then}`));
  L.push("", "h3. Edge Cases");
  e.edges.forEach((c) => L.push(`* ${c.t}: ${c.d}`));
  return L.join("\n");
}

function toGithub(e) {
  const L = [
    `# ${e.title}`, "",
    `**Severity:** ${severityLabel(e.severity)} — ${e.severityWhy}  `,
    `**Component:** ${e.app}`, "",
    "## Summary", e.summary, "",
    "## Steps to Reproduce",
  ];
  e.steps.forEach((s, i) => L.push(`${i + 1}. ${s}`));
  L.push("", "## Expected", e.expected, "", "## Actual", e.actual, "",
    "## Environment", "", "| Field | Value | Confirmed |", "| --- | --- | --- |");
  e.env.forEach((r) => L.push(`| ${r.k} | ${r.v} | ${r.known ? "yes" : "no"} |`));
  L.push("", "## Missing Info (confirm before filing)");
  e.missing.forEach((m) => L.push(`- [ ] **${m.q}** — ${m.why}`));
  L.push("", "## Regression Tests");
  e.tests.forEach((t) => {
    L.push(`- **${t.id} ${t.title}**`, `  - _Given_ ${t.given}`, `  - _When_ ${t.when}`, `  - _Then_ ${t.then}`);
  });
  L.push("", "## Edge Cases");
  e.edges.forEach((c) => L.push(`- **${c.t}** — ${c.d}`));
  return L.join("\n");
}

function csvCell(v) {
  const s = String(v);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function toCsv(e) {
  const rows = [["id", "title", "given", "when", "then"]];
  e.tests.forEach((t) => rows.push([t.id, t.title, t.given, t.when, t.then]));
  return rows.map((r) => r.map(csvCell).join(",")).join("\n") + "\n";
}

function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
  return Promise.reject(new Error("clipboard unavailable"));
}

function downloadText(name, text, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url; a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ── Loading ──
function LoadingView({ shotUrl, mockId, fileName, stageIdx }) {
  return (
    <div className="bl-loading">
      <div className="bl-loading-shot">
        {shotUrl
          ? <img style={SHOT_IMG_STYLE} src={shotUrl} alt="Uploaded screenshot" />
          : <MockScreen id={mockId} />}
        <div className="bl-scan" />
      </div>
      <div className="bl-loading-side">
        <div className="bl-load-file">{fileName}</div>
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
function ResultsView({ example, shotUrl, fileName, layout, showVision, onReset, push }) {
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
          {shotUrl
            ? <img style={SHOT_IMG_STYLE} src={shotUrl} alt="Screenshot" />
            : <MockScreen id={example.id} />}
        </div>
        <div className="bl-lens-file">{fileName}</div>
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
          <Btn kind="primary" icon="↗"
            onClick={() => copyText(toJira(example))
              .then(() => push("Copied Jira markdown to clipboard"))
              .catch(() => push("Couldn’t access the clipboard"))}>Copy Jira</Btn>
          <Btn kind="ghost" icon="⌥"
            onClick={() => copyText(toGithub(example))
              .then(() => push("Copied GitHub issue to clipboard"))
              .catch(() => push("Couldn’t access the clipboard"))}>Copy GitHub issue</Btn>
          <Btn kind="ghost" icon="▤"
            onClick={() => { downloadText("buglens-tests.csv", toCsv(example), "text/csv"); push("Downloaded buglens-tests.csv"); }}>Download CSV</Btn>
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
  const [shotUrl, setShotUrl] = React.useState(null); // object URL of an uploaded screenshot
  const [uploadName, setUploadName] = React.useState("");
  const [note, setNote] = React.useState(""); // optional tester note sent with uploads
  const [stageIdx, setStageIdx] = React.useState(0);
  const [toasts, push] = useToasts();
  const timers = React.useRef([]);
  const reqRef = React.useRef(0); // monotonic token so only the latest request wins
  const shotUrlRef = React.useRef(null);

  const clearTimers = () => { timers.current.forEach(clearTimeout); timers.current = []; };
  const clearShot = () => {
    if (shotUrlRef.current) URL.revokeObjectURL(shotUrlRef.current);
    shotUrlRef.current = null;
    setShotUrl(null);
  };

  // Gallery example: fetched from the mock backend by id.
  const pick = (id) => {
    clearTimers();
    clearShot();
    setUploadName("");
    setActiveId(id);
    setReport(null);
    setStageIdx(0);
    setView("loading");
    // Tag this request; a slower earlier response can't overwrite a newer pick.
    const token = ++reqRef.current;
    fetch(`/api/analyze?id=${encodeURIComponent(id)}`)
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then((data) => { if (token === reqRef.current) setReport(data); })
      .catch(() => {
        if (token !== reqRef.current) return;
        push("Analysis failed — backend unavailable");
        reset(); // keep view + data in sync instead of an empty results screen
      });
    let acc = 0;
    LOAD_STAGES.forEach((s, i) => {
      acc += s.ms;
      timers.current.push(setTimeout(() => setStageIdx(i + 1), acc));
    });
    timers.current.push(setTimeout(() => setView("results"), acc + 250));
  };

  // Uploaded screenshot: POSTed to the real backend; results show when it lands.
  const analyzeUpload = (file) => {
    if (!file || !file.type || !file.type.startsWith("image/")) {
      push("Please choose a PNG or JPG screenshot");
      return;
    }
    clearTimers();
    clearShot();
    const nextShotUrl = URL.createObjectURL(file);
    shotUrlRef.current = nextShotUrl;
    setShotUrl(nextShotUrl);
    setUploadName(file.name);
    setActiveId(null);
    setReport(null);
    setStageIdx(0);
    setView("loading");
    const token = ++reqRef.current;
    const testerNote = note.trim();
    // Advance the visual stages but keep the last one active until the result lands.
    let acc = 0;
    LOAD_STAGES.forEach((s, i) => {
      if (i >= LOAD_STAGES.length - 1) return;
      acc += s.ms;
      timers.current.push(setTimeout(() => setStageIdx(i + 1), acc));
    });
    fileToBase64(file)
      .then((image_b64) => fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_b64, note: testerNote }),
      }))
      .then(async (r) => {
        if (!r.ok) {
          const body = await r.json().catch(() => ({}));
          const msg = typeof body.detail === "string" ? body.detail : `Analysis failed (HTTP ${r.status})`;
          throw new Error(msg);
        }
        return r.json();
      })
      .then((data) => {
        if (token !== reqRef.current) return;
        setStageIdx(LOAD_STAGES.length);
        setReport(data);
        setView("results");
      })
      .catch((err) => {
        if (token !== reqRef.current) return;
        push(err.message || "Analysis failed");
        reset();
      });
  };

  const reset = () => {
    clearTimers();
    reqRef.current++; // invalidate any in-flight request
    clearShot();
    setUploadName("");
    setNote("");
    setView("idle");
    setActiveId(null);
    setReport(null);
  };

  React.useEffect(() => () => clearTimers(), []);

  const example = EXAMPLES.find((e) => e.id === activeId);
  const accent = Array.isArray(t.accent) ? t.accent[0] : t.accent;

  return (
    <div className="bl-app" data-theme={t.theme} data-density={t.density}
         style={{ "--accent": accent }}>
      <Header onReset={reset} view={view} />
      <div className="bl-stage-wrap">
        {view === "idle" && (
          <IdleView onPick={pick} onUpload={analyzeUpload} note={note} onNoteChange={setNote} />
        )}
        {view === "loading" && (shotUrl || example) && (
          <LoadingView shotUrl={shotUrl} mockId={activeId}
                       fileName={shotUrl ? uploadName : example && example.captured}
                       stageIdx={stageIdx} />
        )}
        {view === "results" && report && (
          <ResultsView example={report} shotUrl={shotUrl}
                       fileName={shotUrl ? uploadName : report.captured}
                       layout={t.cardLayout} showVision={t.showVision}
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
