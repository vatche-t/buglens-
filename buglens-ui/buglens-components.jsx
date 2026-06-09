// buglens-components.jsx
// Shared primitives: logo, severity badge, buttons, copy action, tag.

function Logo({ size = 26 }) {
  // Aperture / lens mark — the "lens" that inspects the bug.
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <circle cx="16" cy="16" r="13" stroke="var(--accent)" strokeWidth="2" />
      <path d="M16 3.5 L23 16 M16 3.5 L9 16" stroke="var(--accent)" strokeWidth="1.4" opacity=".55" />
      <path d="M28.5 16 L16 16 M28.5 16 L22 27" stroke="var(--accent)" strokeWidth="1.4" opacity=".55" />
      <path d="M3.5 16 L16 16 M3.5 16 L10 27" stroke="var(--accent)" strokeWidth="1.4" opacity=".55" />
      <circle cx="16" cy="16" r="4.4" fill="var(--accent)" />
    </svg>
  );
}

function Wordmark({ size = 26 }) {
  return (
    <div className="bl-word">
      <Logo size={size} />
      <span>Bug<b>Lens</b></span>
    </div>
  );
}

function SeverityBadge({ level }) {
  const s = SEVERITY[level] || SEVERITY.medium;
  return (
    <span className="bl-sev" style={{ "--sc": s.c }}>
      <i /> {s.label}
    </span>
  );
}

function Btn({ children, kind = "ghost", onClick, icon, full, ...rest }) {
  return (
    <button className={`bl-btn bl-btn-${kind}${full ? " bl-btn-full" : ""}`} onClick={onClick} {...rest}>
      {icon && <span className="bl-btn-ic">{icon}</span>}
      {children}
    </button>
  );
}

function Tag({ children, tone = "neutral" }) {
  return <span className={`bl-tag bl-tag-${tone}`}>{children}</span>;
}

// Copy-to-clipboard with a transient "Copied" state.
function CopyBtn({ getText, label = "Copy" }) {
  const [done, setDone] = React.useState(false);
  const onCopy = () => {
    try {
      const txt = typeof getText === "function" ? getText() : String(getText || "");
      if (navigator.clipboard) navigator.clipboard.writeText(txt).catch(() => {});
    } catch (e) {}
    setDone(true);
    setTimeout(() => setDone(false), 1400);
  };
  return (
    <button className={`bl-copy${done ? " is-done" : ""}`} onClick={onCopy}>
      {done ? "✓ Copied" : `⧉ ${label}`}
    </button>
  );
}

Object.assign(window, { Logo, Wordmark, SeverityBadge, Btn, Tag, CopyBtn });
