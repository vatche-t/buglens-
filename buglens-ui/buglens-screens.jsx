// buglens-screens.jsx
// Synthetic "screenshots" — believable buggy product UI rendered in HTML/CSS.
// These stand in for the user-uploaded image so the demo reads as real.
// All classes are prefixed `mk-` and scoped via a single injected <style>.

const MOCK_STYLE = `
.mk{position:absolute;inset:0;background:#f4f5f7;color:#1c2330;
  font-family:'Space Grotesk',system-ui,sans-serif;overflow:hidden;
  display:flex;flex-direction:column}
.mk *{box-sizing:border-box}
.mk-bar{height:34px;flex:0 0 34px;background:#e7e9ee;border-bottom:1px solid #d6d9e0;
  display:flex;align-items:center;gap:6px;padding:0 12px}
.mk-dot{width:9px;height:9px;border-radius:50%;background:#c6cad3}
.mk-url{margin-left:10px;height:18px;flex:1;max-width:260px;border-radius:5px;
  background:#fff;border:1px solid #d6d9e0;font-size:10px;color:#8a909c;
  display:flex;align-items:center;padding:0 8px;font-family:'JetBrains Mono',monospace}

/* ---- Payment ---- */
.mk-pay-wrap{flex:1;display:flex;align-items:center;justify-content:center;padding:22px}
.mk-card{width:300px;background:#fff;border:1px solid #e3e6ec;border-radius:14px;
  box-shadow:0 10px 30px rgba(20,30,60,.08);padding:22px}
.mk-h{font-size:17px;font-weight:600;margin:0 0 4px}
.mk-sub{font-size:11px;color:#8a909c;margin:0 0 18px}
.mk-field{margin-bottom:13px}
.mk-flbl{font-size:10px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;
  color:#9aa0ac;margin-bottom:5px;display:block}
.mk-inp{height:36px;border:1.5px solid #dfe2e8;border-radius:8px;display:flex;align-items:center;
  padding:0 11px;font-size:13px;font-family:'JetBrains Mono',monospace;color:#1c2330;background:#fff}
.mk-inp.err{border-color:#e5484d}
.mk-row2{display:flex;gap:11px}
.mk-row2>div{flex:1}
.mk-erline{font-size:10.5px;color:#e5484d;margin-top:6px;display:flex;align-items:center;gap:5px}
.mk-pay{height:42px;border-radius:9px;background:#c9ccd4;color:#fff;font-weight:600;font-size:14px;
  display:flex;align-items:center;justify-content:center;margin-top:6px;cursor:not-allowed}
.mk-lock{font-size:9px;color:#aeb3bd;text-align:center;margin-top:9px}

/* ---- Dashboard ---- */
.mk-dash{flex:1;display:flex;min-height:0}
.mk-side{width:54px;flex:0 0 54px;background:#1c2330;display:flex;flex-direction:column;
  align-items:center;gap:14px;padding:16px 0}
.mk-sq{width:22px;height:22px;border-radius:6px;background:rgba(255,255,255,.14)}
.mk-sq.on{background:var(--accent)}
.mk-main{flex:1;padding:18px;display:flex;flex-direction:column;gap:14px;min-width:0}
.mk-toprow{display:flex;align-items:center;justify-content:space-between}
.mk-title{font-size:16px;font-weight:600}
.mk-range{height:30px;border:1px solid #d6d9e0;border-radius:7px;background:#fff;font-size:11px;
  display:flex;align-items:center;gap:8px;padding:0 11px;color:#3a4150;font-weight:500}
.mk-range b{color:#1c2330}
.mk-tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:11px}
.mk-tile{background:#fff;border:1px solid #e6e8ee;border-radius:10px;padding:12px}
.mk-tlbl{font-size:9.5px;color:#9aa0ac;font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.mk-tval{font-size:19px;font-weight:600;margin-top:6px}
.mk-tval span{font-size:11px;color:#2f9e6f;font-weight:600;margin-left:5px}
.mk-panel{flex:1;background:#fff;border:1px solid #e6e8ee;border-radius:12px;min-height:0;
  display:flex;flex-direction:column}
.mk-phead{padding:13px 16px;font-size:13px;font-weight:600;border-bottom:1px solid #eef0f4}
.mk-pbody{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:11px}
.mk-spin{width:30px;height:30px;border-radius:50%;border:3px solid #e6e8ee;
  border-top-color:var(--accent);animation:mkspin 1s linear infinite}
@keyframes mkspin{to{transform:rotate(360deg)}}
.mk-ptext{font-size:11px;color:#aeb3bd}

/* ---- Signup (mobile) ---- */
.mk-mobwrap{flex:1;background:#e9ebf0;display:flex;align-items:center;justify-content:center;padding:18px}
.mk-phone{width:208px;height:330px;background:#fff;border-radius:22px;border:1px solid #d6d9e0;
  box-shadow:0 14px 36px rgba(20,30,60,.14);padding:26px 20px;position:relative;overflow:hidden}
.mk-notch{position:absolute;top:9px;left:50%;transform:translateX(-50%);width:54px;height:5px;
  border-radius:3px;background:#dcdfe6}
.mk-mh{font-size:17px;font-weight:600;margin:8px 0 3px}
.mk-msub{font-size:10px;color:#9aa0ac;margin:0 0 20px}
.mk-mfield{margin-bottom:16px;position:relative}
.mk-minp{height:34px;border:1.5px solid #dfe2e8;border-radius:8px;background:#fff;
  display:flex;align-items:center;padding:0 10px;font-size:11px;color:#5a6170}
.mk-minp.err{border-color:#e5484d}
/* The bug: error pulled up over the field instead of below it */
.mk-merr{position:absolute;left:4px;bottom:5px;font-size:10px;color:#e5484d;font-weight:600;
  background:rgba(255,255,255,.86);padding:0 3px}
.mk-mbtn{height:38px;border-radius:9px;background:var(--accent);color:#fff;font-weight:600;
  font-size:12px;display:flex;align-items:center;justify-content:center;margin-top:6px}

/* ---- Settings (broken avatar) ---- */
.mk-setwrap{flex:1;padding:26px 30px}
.mk-crumb{font-size:11px;color:#9aa0ac;font-family:'JetBrains Mono',monospace;margin-bottom:18px}
.mk-prof{display:flex;align-items:flex-start;gap:2px;background:#fff;border:1px solid #e6e8ee;
  border-radius:12px;padding:20px}
.mk-broken{width:30px;height:24px;flex:0 0 auto;border:1.5px dashed #c2c7d0;border-radius:4px;
  display:flex;align-items:center;justify-content:center;color:#b3b8c2;font-size:13px;
  position:relative;margin-top:2px}
/* name/email shifted tight against the broken icon — the layout jump */
.mk-pinfo{margin-left:8px}
.mk-pname{font-size:17px;font-weight:600}
.mk-pmail{font-size:12px;color:#8a909c;font-family:'JetBrains Mono',monospace;margin-top:3px}
.mk-pfields{margin-top:22px;display:flex;flex-direction:column;gap:13px}
.mk-pf{display:flex;flex-direction:column;gap:5px}
.mk-pfl{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;color:#9aa0ac}
.mk-pfv{height:34px;background:#f4f5f7;border:1px solid #e6e8ee;border-radius:8px}
`;

function BrowserBar({ url }) {
  return (
    <div className="mk-bar">
      <div className="mk-dot" /><div className="mk-dot" /><div className="mk-dot" />
      <div className="mk-url">{url}</div>
    </div>
  );
}

function MockScreen({ id }) {
  if (id === "payment") {
    return (
      <div className="mk">
        <BrowserBar url="shop.acme.io/checkout" />
        <div className="mk-pay-wrap">
          <div className="mk-card">
            <h3 className="mk-h">Payment</h3>
            <p className="mk-sub">Order total · $49.00</p>
            <div className="mk-field">
              <span className="mk-flbl">Card number</span>
              <div className="mk-inp err">4242 4242 4242 4242</div>
              <div className="mk-erline">⚠ Card number looks incomplete</div>
            </div>
            <div className="mk-row2">
              <div className="mk-field">
                <span className="mk-flbl">Expiry</span>
                <div className="mk-inp">12 / 27</div>
              </div>
              <div className="mk-field">
                <span className="mk-flbl">CVC</span>
                <div className="mk-inp">123</div>
              </div>
            </div>
            <div className="mk-pay">Pay $49.00</div>
            <div className="mk-lock">🔒 Secured by AcmePay</div>
          </div>
        </div>
      </div>
    );
  }

  if (id === "dashboard") {
    return (
      <div className="mk">
        <BrowserBar url="app.acme.io/analytics" />
        <div className="mk-dash">
          <div className="mk-side">
            <div className="mk-sq on" /><div className="mk-sq" />
            <div className="mk-sq" /><div className="mk-sq" />
          </div>
          <div className="mk-main">
            <div className="mk-toprow">
              <div className="mk-title">Analytics</div>
              <div className="mk-range">Range · <b>Last 90 days</b> ▾</div>
            </div>
            <div className="mk-tiles">
              <div className="mk-tile"><div className="mk-tlbl">Revenue</div><div className="mk-tval">$84.2k</div></div>
              <div className="mk-tile"><div className="mk-tlbl">Orders</div><div className="mk-tval">1,904</div></div>
              <div className="mk-tile"><div className="mk-tlbl">AOV</div><div className="mk-tval">$44</div></div>
              <div className="mk-tile"><div className="mk-tlbl">Refunds</div><div className="mk-tval">31</div></div>
            </div>
            <div className="mk-panel">
              <div className="mk-phead">Revenue over time</div>
              <div className="mk-pbody">
                <div className="mk-spin" />
                <div className="mk-ptext">Loading…</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (id === "signup") {
    return (
      <div className="mk">
        <BrowserBar url="acme.io/signup" />
        <div className="mk-mobwrap">
          <div className="mk-phone">
            <div className="mk-notch" />
            <h3 className="mk-mh">Create account</h3>
            <p className="mk-msub">Start your 14-day trial</p>
            <div className="mk-mfield">
              <div className="mk-minp">you@company.com</div>
            </div>
            <div className="mk-mfield">
              <div className="mk-minp err">•••••</div>
              <div className="mk-merr">Use at least 8 characters</div>
            </div>
            <div className="mk-mbtn">Create account</div>
          </div>
        </div>
      </div>
    );
  }

  if (id === "settings") {
    return (
      <div className="mk">
        <BrowserBar url="app.acme.io/settings/profile" />
        <div className="mk-setwrap">
          <div className="mk-crumb">Settings / Profile</div>
          <div className="mk-prof">
            <div className="mk-broken">🖼</div>
            <div className="mk-pinfo">
              <div className="mk-pname">Jordan Reyes</div>
              <div className="mk-pmail">jordan@acme.io</div>
            </div>
          </div>
          <div className="mk-pfields">
            <div className="mk-pf"><span className="mk-pfl">Display name</span><div className="mk-pfv" /></div>
            <div className="mk-pf"><span className="mk-pfl">Time zone</span><div className="mk-pfv" /></div>
          </div>
        </div>
      </div>
    );
  }
  return null;
}

Object.assign(window, { MockScreen, MOCK_STYLE });
