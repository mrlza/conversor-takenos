import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRATCH = str(HERE / "assets")
OUT_DIR = HERE

# URL del Web App de Apps Script que hace de proxy CORS hacia la cotización
# USDT/Takenos de la API de Dolarito (ver conversor/apps-script/live-rate-proxy.gs).
# Si queda vacío, el HTML generado usa únicamente el snapshot estático de CURRENCIES.
LIVE_RATE_URL = "https://script.google.com/macros/s/AKfycbzpmnfHUwHx41tOTs4fo6AeJuIgSXfCa0fK3mZzmCQ7b4lKW4kCY9vk5D9KRJYm6VmNqA/exec"

sg = open(f"{SCRATCH}/space-grotesk.woff2.b64").read().strip()
logo_svg = open(f"{SCRATCH}/logo-white-clean.svg").read().strip()
logo_black_svg = open(f"{SCRATCH}/logo-brand-violet.svg").read().strip()
flag_stack_b64 = open(f"{SCRATCH}/flag-stack-cropped.png.b64").read().strip()
footer_pattern_b64 = open(f"{SCRATCH}/footer-pattern-fade.png.b64").read().strip()

CURRENCIES = {
    "ARS": {"buy": 1586.6, "sell": 1555.12, "name": "Peso argentino", "decimals": 2},
    "BOB": {"buy": 11.7606, "sell": 11.3949, "name": "Boliviano", "decimals": 2},
    "MXN": {"buy": 17.064846416382252, "sell": 16.95, "name": "Peso mexicano", "decimals": 2},
    "BRL": {"buy": 5.3214142051846, "sell": 5.109518659, "name": "Real brasileño", "decimals": 2},
    "EUR": {"buy": 0.8816491940711292, "sell": 0.8470747158722614, "name": "Euro", "decimals": 2},
    "CLP": {"buy": 937.14234, "sell": 891.43152, "name": "Peso chileno", "decimals": 0},
    "GBP": {"buy": 0.7632, "sell": 0.7631, "name": "Libra esterlina", "decimals": 2},
    "PYG": {"buy": 6223.1985, "sell": 5750.44596, "name": "Guaraní paraguayo", "decimals": 0},
    "COP": {"buy": 3262.9885338231, "sell": 3005.754706416, "name": "Peso colombiano", "decimals": 0},
    "PEN": {"buy": 3.41, "sell": 3.31, "name": "Sol peruano", "decimals": 2},
}

FLAG_CODES = ["ARS", "BOB", "BRL", "CLP", "COP", "EUR", "GBP", "MXN", "PEN", "PYG", "USD"]
flags = {}
for code in FLAG_CODES:
    b64 = open(f"{SCRATCH}/flags/{code}.png.b64").read().strip()
    flags[code] = "data:image/png;base64," + b64

rates_json = json.dumps(CURRENCIES, ensure_ascii=False)
flags_json = json.dumps(flags)

# Historia diaria real (promedio buy/sell por día) desde Snowflake SRC_TAKENOS_PRODUCTION_RATE.
# Solo ARS y BOB tienen serie diaria sin huecos; el resto de las monedas no tiene historial logueado.
HISTORY = {
    "ARS": [
        {"d": "2026-07-30", "buy": 1541.87, "sell": 1582.57}, {"d": "2026-07-31", "buy": 1547.3936, "sell": 1588.2391},
        {"d": "2026-08-01", "buy": 1551.37, "sell": 1592.32}, {"d": "2026-08-02", "buy": 1551.37, "sell": 1592.32},
        {"d": "2026-08-03", "buy": 1554.9038, "sell": 1595.9525}, {"d": "2026-08-04", "buy": 1553.9522, "sell": 1594.9689},
        {"d": "2026-08-05", "buy": 1551.3893, "sell": 1592.3414}, {"d": "2026-08-06", "buy": 1555.7019, "sell": 1587.3586},
        {"d": "2026-08-07", "buy": 1556.0399, "sell": 1587.5379}, {"d": "2026-08-08", "buy": 1554.73, "sell": 1586.2},
        {"d": "2026-08-09", "buy": 1554.73, "sell": 1586.2}, {"d": "2026-08-10", "buy": 1560.0274, "sell": 1591.6057},
        {"d": "2026-08-11", "buy": 1562.3809, "sell": 1594.0104}, {"d": "2026-08-12", "buy": 1565.6468, "sell": 1597.3412},
        {"d": "2026-08-13", "buy": 1566.1751, "sell": 1597.8798}, {"d": "2026-08-14", "buy": 1555.9207, "sell": 1587.4173},
        {"d": "2026-08-15", "buy": 1555.12, "sell": 1586.6},
    ],
    "BOB": [
        {"d": "2026-07-01", "buy": 9.8876, "sell": 10.2679}, {"d": "2026-07-02", "buy": 9.8579, "sell": 10.2282},
        {"d": "2026-07-03", "buy": 9.8625, "sell": 10.2354}, {"d": "2026-07-04", "buy": 9.8864, "sell": 10.259},
        {"d": "2026-07-05", "buy": 9.8736, "sell": 10.2534}, {"d": "2026-07-06", "buy": 9.8885, "sell": 10.262},
        {"d": "2026-07-07", "buy": 9.8951, "sell": 10.2705}, {"d": "2026-07-08", "buy": 10.1495, "sell": 10.5391},
        {"d": "2026-07-09", "buy": 10.3232, "sell": 10.7164}, {"d": "2026-07-10", "buy": 10.4445, "sell": 10.8445},
        {"d": "2026-07-11", "buy": 10.4338, "sell": 10.8428}, {"d": "2026-07-12", "buy": 10.3158, "sell": 10.7113},
        {"d": "2026-07-13", "buy": 10.3818, "sell": 10.7693}, {"d": "2026-07-14", "buy": 10.4061, "sell": 10.8009},
        {"d": "2026-07-15", "buy": 10.5318, "sell": 10.9451}, {"d": "2026-07-16", "buy": 10.5826, "sell": 10.8646},
        {"d": "2026-07-17", "buy": 10.6029, "sell": 10.8}, {"d": "2026-07-18", "buy": 10.6376, "sell": 10.8475},
        {"d": "2026-07-19", "buy": 10.6469, "sell": 10.9054}, {"d": "2026-07-20", "buy": 10.6788, "sell": 11.0313},
        {"d": "2026-07-21", "buy": 11.0311, "sell": 11.3875}, {"d": "2026-07-22", "buy": 11.2365, "sell": 11.6207},
        {"d": "2026-07-23", "buy": 11.5005, "sell": 11.8898}, {"d": "2026-07-24", "buy": 11.6268, "sell": 12.0083},
        {"d": "2026-07-25", "buy": 11.6582, "sell": 12.038}, {"d": "2026-07-26", "buy": 11.4345, "sell": 11.8177},
        {"d": "2026-07-27", "buy": 11.5533, "sell": 11.934}, {"d": "2026-07-28", "buy": 11.484, "sell": 11.8626},
        {"d": "2026-07-29", "buy": 11.7889, "sell": 12.1727}, {"d": "2026-07-30", "buy": 11.7497, "sell": 12.1329},
        {"d": "2026-07-31", "buy": 11.8562, "sell": 12.24}, {"d": "2026-08-01", "buy": 11.583, "sell": 11.9646},
        {"d": "2026-08-02", "buy": 11.5533, "sell": 11.9391}, {"d": "2026-08-03", "buy": 11.7202, "sell": 12.0957},
        {"d": "2026-08-04", "buy": 11.6498, "sell": 12.0207}, {"d": "2026-08-05", "buy": 11.4889, "sell": 11.8575},
        {"d": "2026-08-06", "buy": 11.1652, "sell": 11.5423}, {"d": "2026-08-07", "buy": 11.0286, "sell": 11.4113},
        {"d": "2026-08-08", "buy": 11.0319, "sell": 11.3798}, {"d": "2026-08-09", "buy": 11.0385, "sell": 11.3934},
        {"d": "2026-08-10", "buy": 11.2299, "sell": 11.6008}, {"d": "2026-08-11", "buy": 11.3974, "sell": 11.7683},
        {"d": "2026-08-12", "buy": 11.3982, "sell": 11.7697}, {"d": "2026-08-13", "buy": 11.3969, "sell": 11.7667},
        {"d": "2026-08-14", "buy": 11.3588, "sell": 11.7307}, {"d": "2026-08-15", "buy": 11.3244, "sell": 11.6951},
    ],
}
history_json = json.dumps(HISTORY)

html = r"""<!doctype html>
<html lang="es">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Conversor Takenos</title>
<style>
@font-face {
  font-family: 'Space Grotesk';
  font-style: normal;
  font-weight: 400 700;
  font-display: swap;
  src: url(data:font/woff2;base64,__SG__) format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
:root {
  --bg: #ffffff;
  --surface: #f7f2ff;
  --surface-2: #eee6ff;
  --card: #ffffff;
  --icon-pill: #f1f2f4;
  --text: #111111;
  --text-muted: #5a6772;
  --text-faint: #868686;
  --accent: #6d37d5;
  --accent-strong: #360285;
  --aji: #ff4e00;
  --accent-soft: #deccff;
  --accent-softer: #f7f2ff;
  --border: rgba(17, 17, 17, 0.1);
  --border-strong: rgba(17, 17, 17, 0.16);
  --row-hover: rgba(109, 55, 213, 0.06);
  --focus-ring: #6d37d5;
  --nav-link: #27174c;
  --card-glass: rgba(241, 242, 244, 0.8);
  --card-shadow: 0 14px 28px 0 rgba(25, 28, 31, 0.04), 0 8px 16px 0 rgba(25, 28, 31, 0.04), 0 -1px 0 0 rgba(25, 28, 31, 0.04);
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0d0d0d;
    --surface: #1a1a1a;
    --surface-2: #202020;
    --card: #181818;
    --icon-pill: #232323;
    --text: #f4f4f4;
    --text-muted: #a3a3a3;
    --text-faint: #757575;
    --accent: #8b5cf6;
    --accent-strong: #ad8dfa;
    --aji: #ff7a3d;
    --accent-soft: #2f2438;
    --accent-softer: #201a26;
    --border: rgba(255, 255, 255, 0.09);
    --border-strong: rgba(255, 255, 255, 0.16);
    --row-hover: rgba(139, 92, 246, 0.12);
    --focus-ring: #8b5cf6;
    --nav-link: #e4d9ff;
    --card-glass: rgba(32, 32, 35, 0.8);
    --card-shadow: 0 14px 28px 0 rgba(0, 0, 0, 0.35), 0 8px 16px 0 rgba(0, 0, 0, 0.3), 0 -1px 0 0 rgba(255, 255, 255, 0.04);
  }
  :root:not([data-theme="light"]) .site-nav-logo .logo-light { display: none; }
  :root:not([data-theme="light"]) .site-nav-logo .logo-dark { display: block; }
  :root:not([data-theme="light"]) .footer-logo .logo-light { display: none; }
  :root:not([data-theme="light"]) .footer-logo .logo-dark { display: block; }
}

:root[data-theme="dark"] {
  --bg: #0d0d0d;
  --surface: #1a1a1a;
  --surface-2: #202020;
  --card: #181818;
  --icon-pill: #232323;
  --text: #f4f4f4;
  --text-muted: #a3a3a3;
  --text-faint: #757575;
  --accent: #8b5cf6;
  --accent-strong: #ad8dfa;
  --aji: #ff7a3d;
  --accent-soft: #2f2438;
  --accent-softer: #201a26;
  --border: rgba(255, 255, 255, 0.09);
  --border-strong: rgba(255, 255, 255, 0.16);
  --row-hover: rgba(139, 92, 246, 0.12);
  --focus-ring: #8b5cf6;
  --nav-link: #e4d9ff;
  --card-glass: rgba(32, 32, 35, 0.8);
  --card-shadow: 0 14px 28px 0 rgba(0, 0, 0, 0.35), 0 8px 16px 0 rgba(0, 0, 0, 0.3), 0 -1px 0 0 rgba(255, 255, 255, 0.04);
}

:root[data-theme="dark"] .site-nav-logo .logo-light { display: none; }
:root[data-theme="dark"] .site-nav-logo .logo-dark { display: block; }
:root[data-theme="dark"] .footer-logo .logo-light { display: none; }
:root[data-theme="dark"] .footer-logo .logo-dark { display: block; }

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Space Grotesk', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  line-height: 1.5;
}

.wrap {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px 40px 72px;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}

/* ---- flat hero ---- */
.flat-hero {
  position: relative;
  overflow: visible;
  padding: 10px 0 32px 0;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
  gap: 32px;
  text-align: left;
}

.flat-hero-text {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  min-width: 0;
  margin-top: 20px;
}

.hero-kicker {
  margin: 0;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 500;
  font-size: 13.3px;
  color: var(--accent);
}

.flat-hero h1 { text-wrap: balance; color: var(--accent-strong); }

.flat-hero .sub { margin: 0; max-width: 42ch; }

.hero-flags-img {
  display: block;
  width: 100%;
  max-width: 403px;
  height: auto;
  margin-top: 20px;
}

.hero-card {
  position: relative;
  z-index: 1;
  flex: 0 0 380px;
  width: 380px;
  max-width: 100%;
}

@media (max-width: 900px) {
  .flat-hero { flex-direction: column; align-items: stretch; padding-top: 60px; margin-left: 0; }
  .hero-card { flex: 1 1 auto; width: 100%; align-self: stretch; }
}

@media (max-width: 560px) {
  .flat-hero { padding: 28px 24px 26px; }
  .flat-hero-text { text-align: center; align-items: center; }
}

header.hero {
  display: flex;
  flex-direction: column;
  gap: 14px;
  text-align: center;
}

h1 {
  font-family: 'Space Grotesk', system-ui, sans-serif;
  font-weight: 700;
  font-size: clamp(28px, 5vw, 40px);
  line-height: 1.1;
  margin: 0;
  text-wrap: balance;
  letter-spacing: -0.01em;
}

.sub {
  color: var(--text-muted);
  font-weight: 400;
  font-size: 16px;
  max-width: 46ch;
  margin: 0 auto;
  text-wrap: balance;
}

.card {
  background: var(--surface);
  border: none;
  border-radius: 20px;
  box-shadow: var(--card-shadow);
  padding: 13.3px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field {
  background: var(--card);
  border: 1px solid transparent;
  border-radius: 20px;
  padding: 13.3px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: border-color 0.15s ease;
}

.field:focus-within {
  border-color: var(--accent);
}

.field-labels {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3.3px;
}

.field-label {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 500;
  font-size: 10px;
  letter-spacing: -0.15px;
  line-height: 15px;
  color: var(--text-muted);
}

.amount-input {
  display: block;
  width: 100%;
  overflow: hidden;
  white-space: nowrap;
  border: none;
  outline: none;
  caret-color: var(--accent);
  background: transparent;
  color: var(--text);
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 500;
  font-size: 30px;
  letter-spacing: -0.5px;
  line-height: 1;
  padding: 0;
  min-width: 0;
}

.amount-input::placeholder { color: var(--text-faint); }
.field:focus-within .amount-input { color: var(--accent); }

.currency-picker { position: relative; flex-shrink: 0; }

.picker-btn {
  display: flex;
  align-items: center;
  gap: 6.7px;
  background: var(--card);
  border: 1px solid var(--border-strong);
  border-radius: 999px;
  padding: 5px 10px 5px 5px;
  cursor: pointer;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 11.7px;
  letter-spacing: -0.15px;
  color: var(--text);
}

.fixed-currency-badge {
  display: flex;
  align-items: center;
  gap: 6.7px;
  flex-shrink: 0;
  background: var(--card);
  border: 1px solid var(--border-strong);
  border-radius: 999px;
  padding: 5px 12px 5px 5px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 11.7px;
  letter-spacing: -0.15px;
  color: var(--text);
}

.picker-btn:hover { border-color: var(--accent); }
.picker-btn:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}

.flag-pill {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: var(--icon-pill);
  border-radius: 999px;
  padding: 3.3px;
}

.flag-icon {
  width: 16.7px;
  height: 16.7px;
  border-radius: 50%;
  display: block;
  flex-shrink: 0;
  object-fit: cover;
}

.picker-btn .chev {
  color: var(--text-faint);
  transition: transform 0.15s ease;
}

.picker-btn[aria-expanded="true"] .chev { transform: rotate(180deg); }

.picker-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 260px;
  max-height: 320px;
  overflow-y: auto;
  background: var(--card);
  border: 1px solid var(--border-strong);
  border-radius: 14px;
  padding: 6px;
  z-index: 20;
  display: none;
}

.picker-panel.open { display: block; }

.picker-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  background: none;
  border: none;
  border-radius: 9px;
  padding: 9px 10px;
  cursor: pointer;
  text-align: left;
  font-family: 'Space Grotesk', sans-serif;
  color: var(--text);
}

.picker-row:hover, .picker-row:focus-visible { background: var(--row-hover); }
.picker-row[aria-selected="true"] { background: var(--accent-softer); }

.picker-row .code {
  font-weight: 600;
  font-size: 14px;
  min-width: 38px;
}

.picker-row .name {
  font-weight: 400;
  color: var(--text-muted);
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.swap-row {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: -6px 0;
  position: relative;
  z-index: 1;
}

.convert-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-faint);
  margin: -3.3px 0;
}

.swap-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--aji);
  color: white;
  border: 4px solid var(--card);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s ease;
}

.swap-btn svg { transition: transform 0.25s ease; }
.swap-btn:hover { background: #e04600; }
.swap-btn.spun svg { transform: rotate(180deg); }
.swap-btn:focus-visible { outline: 2px solid var(--focus-ring); outline-offset: 2px; }

@media (prefers-reduced-motion: reduce) {
  .swap-btn svg { transition: none; }
}

.rate-breakdown {
  background: var(--surface-2);
  border-radius: 20px;
  padding: 13.3px;
  display: flex;
  flex-direction: column;
  gap: 8.3px;
}

.rate-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.rate-row-label {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 11.7px;
  letter-spacing: -0.15px;
  color: var(--text-muted);
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
  flex-shrink: 0;
}

.rate-value {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 11.7px;
  color: var(--text-muted);
  white-space: nowrap;
  text-align: right;
}

.rate-row-primary {
  flex-direction: column;
  align-items: flex-start;
  gap: 3.3px;
}

.rate-row-primary .rate-value {
  font-size: 13.3px;
  color: var(--text);
  text-align: left;
  white-space: normal;
}

.rate-caption {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 500;
  font-size: 10px;
  color: var(--text-faint);
}

.calc-disclaimer {
  display: block;
  margin: 0;
  line-height: 1.4;
}

.rate-value-strong { color: var(--accent-strong); }

.hero-cta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6.7px;
  height: 46.7px;
  padding: 0 10px;
  background: var(--accent);
  color: #fff;
  border-radius: 13.3px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 13.3px;
  text-decoration: none;
}

.hero-cta svg { flex-shrink: 0; }
.hero-cta:hover { background: var(--accent-strong); }

@media (max-width: 560px) {
  .card { padding: 16px; gap: 14px; }
  .field { padding: 20px 18px; }
  .rate-breakdown { padding: 18px; gap: 12px; }
  .hero-cta { height: 54px; }
}

section.rates {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.rates-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

h2 {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 20px;
  margin: 0;
  letter-spacing: -0.01em;
}

.rates-note {
  font-size: 10px;
  color: var(--text-faint);
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 500;
}

.info-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  border: 1.5px solid var(--text-faint);
  color: var(--text-faint);
  font-size: 10px;
  font-family: 'Space Grotesk', sans-serif;
  margin-left: 4px;
  vertical-align: middle;
}

.cotiz-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 2px 2px 10px;
  scroll-snap-type: x proximity;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.cotiz-scroll::-webkit-scrollbar { display: none; }

.cotiz-card {
  flex: 0 0 auto;
  width: 208px;
  scroll-snap-align: start;
  background: var(--card);
  border: 1px solid var(--border-strong);
  border-radius: 16px;
  padding: 14px 16px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 14px;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.cotiz-card:hover { border-color: var(--accent); }
.cotiz-card.active { border-color: var(--accent); background: var(--accent-softer); }

.cotiz-pair {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 13px;
}

.cotiz-pair .swap-ic { color: var(--text-faint); font-size: 12px; line-height: 1; }

.cotiz-values {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.cotiz-col { display: flex; flex-direction: column; gap: 3px; min-width: 0; }

.cotiz-label {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 11px;
  color: var(--text-faint);
}

.cotiz-value {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 11.7px;
  white-space: nowrap;
}

/* ---- history ---- */
section.history {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.currency-toggle {
  display: flex;
  gap: 6px;
  background: var(--surface);
  border-radius: 999px;
  padding: 4px;
}

.currency-toggle button {
  display: flex;
  align-items: center;
  gap: 6px;
  border: none;
  background: none;
  border-radius: 999px;
  padding: 6px 14px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
}

.currency-toggle button.active {
  background: var(--card);
  color: var(--text);
  box-shadow: 0 0 0 1px var(--border-strong);
}

.history-rate {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 500;
  font-size: 12.5px;
}

.history-rate b { color: var(--accent); font-weight: 600; }

.range-tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.range-tabs button {
  border: 1px solid var(--border-strong);
  background: var(--card);
  border-radius: 8px;
  padding: 7px 12px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 500;
  font-size: 12.5px;
  color: var(--text-muted);
  cursor: pointer;
}

.range-tabs button.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
  font-weight: 600;
}

.range-tabs button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.chart-card {
  background: var(--card);
  border: 1px solid var(--border-strong);
  border-radius: 16px;
  padding: 16px 16px 8px;
}

.chart-wrap { position: relative; }

.chart-wrap svg { display: block; width: 100%; height: auto; overflow: visible; }

.chart-axis-label {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 500;
  font-size: 8.3px;
  fill: var(--text-faint);
}

.chart-line { fill: none; stroke: var(--accent); stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
.chart-area { fill: var(--accent); opacity: 0.1; }
.chart-gridline { stroke: var(--border); stroke-width: 1; }
.chart-guide { stroke: var(--aji); stroke-width: 1; stroke-dasharray: 3 3; opacity: 0; }
.chart-dot { fill: var(--aji); stroke: var(--card); stroke-width: 2; opacity: 0; }

.chart-tooltip {
  position: absolute;
  pointer-events: none;
  background: var(--card);
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  padding: 6px 10px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  transform: translate(-50%, -110%);
  transition: opacity 0.1s ease;
}

.chart-tooltip .tt-date { color: var(--text-faint); font-family: 'Space Grotesk', sans-serif; font-size: 11px; }
.chart-tooltip .tt-value { font-family: 'Space Grotesk', sans-serif; font-weight: 600; }

.chart-note {
  font-size: 11px;
  color: var(--text-faint);
  margin: 6px 2px 0;
}

/* ---- rate alerts ---- */
section.alerts {
  display: flex;
  flex-direction: column;
}

.alerts-card {
  max-width: 700px;
  margin: 0 auto;
  background: var(--surface);
  border-radius: 16.7px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.alerts-head {
  display: flex;
  flex-direction: column;
  gap: 6.7px;
  text-align: center;
}

.alerts-title {
  margin: 0;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 23.3px;
  line-height: 1.25;
  letter-spacing: -0.01em;
  color: var(--text);
}

.alerts-title .accent-line { display: block; color: var(--accent-strong); }

.alerts-sub {
  margin: 0 auto;
  max-width: 46ch;
  color: var(--text-muted);
  font-size: 12.5px;
}

.alerts-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-top: 16.7px;
  border-top: 1px solid var(--border);
}

.alerts-row-column { flex-direction: column; align-items: stretch; }

.alerts-row-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.alerts-row-text { display: flex; flex-direction: column; gap: 3.3px; }

.alerts-row-label {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 13.3px;
  color: var(--text);
}

.alerts-row-desc {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 11px;
  color: var(--text-muted);
}

.toggle {
  width: 36.7px;
  height: 21.7px;
  border-radius: 999px;
  border: none;
  background: var(--border-strong);
  position: relative;
  flex-shrink: 0;
  cursor: pointer;
  padding: 0;
  transition: background 0.15s ease;
}

.toggle-knob {
  position: absolute;
  top: 1.7px;
  left: 1.7px;
  width: 18.3px;
  height: 18.3px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  transition: transform 0.15s ease;
}

.toggle[aria-checked="true"] { background: var(--accent); }
.toggle[aria-checked="true"] .toggle-knob { transform: translateX(15px); }
.toggle:focus-visible { outline: 2px solid var(--focus-ring); outline-offset: 2px; }

.alerts-threshold {
  display: flex;
  align-items: center;
  gap: 8.3px;
  flex-wrap: wrap;
  margin-top: 13.3px;
}

.alerts-amount {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6.7px;
  background: var(--card);
  border: 1px solid var(--border-strong);
  border-radius: 11.7px;
  padding: 8.3px 10px;
  flex: 1;
  min-width: 116.7px;
}

.alerts-amount .amt-fixed {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 12.5px;
  color: var(--text);
}

.alerts-amount input {
  flex: 1 1 auto;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 12.5px;
  color: var(--text);
}

.alerts-direction {
  flex: 1;
  min-width: 108.3px;
}

.alerts-direction .picker-btn {
  width: 100%;
  justify-content: space-between;
  border-radius: 11.7px;
  padding: 8.3px 10px;
}

.alerts-direction .picker-panel { width: 150px; }
.alerts-direction .dir-icon { flex-shrink: 0; }

.alerts-email { display: flex; flex-direction: column; gap: 6.7px; margin-top: 3.3px; }

.alerts-email-input {
  background: var(--card);
  border: 1px solid var(--border-strong);
  border-radius: 11.7px;
  padding: 11.7px 13.3px;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 12.5px;
  color: var(--text);
  outline: none;
}

.alerts-email-input::placeholder { color: var(--text-faint); }
.alerts-email-input:focus { border-color: var(--accent); }

.alerts-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 46.7px;
  border: none;
  border-radius: 13.3px;
  background: var(--accent);
  color: #fff;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 13.3px;
  cursor: pointer;
  margin-top: 3.3px;
}

.alerts-submit:hover { background: var(--accent-strong); }

.alerts-note {
  margin: 0;
  text-align: center;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 11.7px;
  color: var(--accent-strong);
}

@media (max-width: 560px) {
  .alerts-card { padding: 20px; }
  .alerts-threshold { flex-direction: column; align-items: stretch; }
  .alerts-amount, .alerts-direction { min-width: 0; }
}

.rates-disclaimer {
  text-align: center;
  font-size: 11px;
  color: var(--text-faint);
  max-width: 84ch;
  margin: 0 auto;
}

.site-footer {
  position: relative;
  padding: 33.3px 0 105.3px;
  margin-bottom: -72px;
}

.footer-bg {
  position: absolute;
  z-index: 0;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 100vw;
  transform: translateX(-50%);
  overflow: hidden;
  pointer-events: none;
}

.footer-bg::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image: url(data:image/png;base64,__FOOTER_PATTERN__);
  background-repeat: no-repeat;
  background-size: 100% auto;
  background-position: bottom center;
}

.footer-card {
  position: relative;
  z-index: 1;
  background: var(--card);
  border-radius: 20px;
  padding: 33.3px;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  gap: 26.7px;
}

.footer-top {
  display: flex;
  flex-wrap: wrap;
  gap: 33.3px;
  justify-content: space-between;
}

.footer-brand {
  flex: 1 1 200px;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 13.3px;
}

.footer-logo { display: block; width: fit-content; }
.footer-logo svg { display: block; width: 112px; height: auto; }
.footer-logo .logo-dark { display: none; }

.footer-legal {
  margin: 0;
  font-size: 11px;
  color: var(--text-faint);
  max-width: 32ch;
}

.footer-email {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 11.7px;
  color: var(--accent);
  text-decoration: none;
}

.footer-email:hover { color: var(--accent-strong); }

.footer-links-col {
  display: flex;
  flex-direction: column;
  gap: 12.5px;
}

.footer-links-col a {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 12.5px;
  color: var(--accent);
  text-decoration: none;
}

.footer-links-col a:hover { text-decoration: underline; }
.footer-links-col a.current { text-decoration: underline; }

.footer-social {
  display: flex;
  align-items: center;
  gap: 16.7px;
}

.footer-social a {
  display: flex;
  color: var(--text-faint);
}

.footer-social a:hover { color: var(--accent); }
.footer-social svg { width: 18.3px; height: 18.3px; }

@media (max-width: 480px) {
  .site-footer { padding: 16.7px 0 72.7px; margin-bottom: -56px; }
  .footer-card { padding: 24px; }
}

@media (max-width: 480px) {
  .wrap { padding: 24px 20px 56px; }
  .amount-input { font-size: 17px; }
  table { min-width: 420px; }
}

/* ---- site nav: floating pill, matches takenos.com ---- */
.site-nav {
  position: sticky;
  top: 13.3px;
  z-index: 50;
  padding: 0 13.3px;
  transition: transform 0.25s ease;
}

.site-nav.nav-hidden { transform: translateY(-100px); }

@media (prefers-reduced-motion: reduce) {
  .site-nav { transition: none; }
}

.site-nav-inner {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 35px;
  flex-wrap: wrap;
  padding: 8.3px 8.3px 8.3px 18.3px;
  background: var(--surface);
  border-radius: 18.3px;
  box-shadow: 0 0.5px 0.5px -1px rgba(0, 0, 0, 0.18), 0 1.9px 1.9px -2px rgba(0, 0, 0, 0.16), 0 8px 8px -3px rgba(0, 0, 0, 0.06);
}

.site-nav-actions { margin-left: auto; }

.site-nav-logo { display: flex; align-items: center; }
.site-nav-logo svg { display: block; width: 112px; height: auto; }
.site-nav-logo .logo-dark { display: none; }

.site-nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
}

.site-nav-links a {
  color: var(--nav-link);
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 13.3px;
  text-decoration: none;
}

.site-nav-links a:hover { text-decoration: underline; }

.site-nav-links a.current { text-decoration: underline; }

.site-nav-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.site-nav-cta {
  background: var(--accent);
  color: #fff;
  border-radius: 8.3px;
  padding: 10px 20px;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 11.7px;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
}

.site-nav-cta:hover { background: var(--accent-strong); }

.nav-hamburger {
  display: none;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--nav-link);
  cursor: pointer;
  flex-shrink: 0;
  margin-left: auto;
}

.nav-hamburger svg { width: 22px; height: 22px; }

.nav-mobile-panel {
  display: none;
  flex-direction: column;
  gap: 4px;
  max-width: 1000px;
  margin: 10px auto 0;
  padding: 10px;
  border-radius: 18.3px;
  background: var(--surface);
  box-shadow: 0 0.5px 0.5px -1px rgba(0, 0, 0, 0.18), 0 1.9px 1.9px -2px rgba(0, 0, 0, 0.16), 0 8px 8px -3px rgba(0, 0, 0, 0.06);
}

.nav-mobile-panel.open { display: flex; }

.nav-mobile-panel a {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  border-radius: 12px;
  color: var(--nav-link);
  font-family: 'Space Grotesk', sans-serif;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  text-align: left;
}

.nav-mobile-panel a:hover { background: var(--row-hover); }

.nav-mobile-panel a.current { text-decoration: underline; }

.nav-mobile-panel .nav-mobile-divider {
  height: 1px;
  background: var(--border);
  margin: 6px 8px;
}

.nav-mobile-panel .site-nav-cta {
  border-radius: 12px;
  justify-content: center;
}

@media (max-width: 640px) {
  .site-nav-links, .site-nav-actions { display: none; }
  .nav-hamburger { display: flex; }
}

@media (max-width: 480px) {
  .site-nav { padding: 0 8.3px; }
}
</style>

<nav class="site-nav">
  <div class="site-nav-inner">
    <a class="site-nav-logo" id="navLogo" href="https://takenos.com" target="_blank" rel="noopener" aria-label="Takenos">
      <span class="logo-light">__LOGO_BLACK_SVG__</span>
      <span class="logo-dark">__LOGO_SVG__</span>
    </a>
    <div class="site-nav-links">
      <a class="current" href="https://takenos.com" target="_blank" rel="noopener">Personal</a>
      <a href="https://takenos.com" target="_blank" rel="noopener">Business</a>
    </div>
    <div class="site-nav-actions">
      <a class="site-nav-cta" href="https://takenos.com" target="_blank" rel="noopener">Descargar app</a>
    </div>
    <button class="nav-hamburger" id="navHamburger" type="button" aria-label="Abrir menú" aria-expanded="false">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
        <path d="M4 7h16M4 12h16M4 17h16"></path>
      </svg>
    </button>
  </div>
  <div class="nav-mobile-panel" id="navMobilePanel">
    <a class="current" href="https://takenos.com" target="_blank" rel="noopener">Personal</a>
    <a href="https://takenos.com" target="_blank" rel="noopener">Business</a>
    <div class="nav-mobile-divider"></div>
    <a class="site-nav-cta" href="https://takenos.com" target="_blank" rel="noopener">Descargar app</a>
  </div>
</nav>

<script>
(function () {
  var hamburger = document.getElementById("navHamburger");
  var mobilePanel = document.getElementById("navMobilePanel");
  function closeMobilePanel() {
    mobilePanel.classList.remove("open");
    hamburger.setAttribute("aria-expanded", "false");
  }
  hamburger.addEventListener("click", function () {
    var open = mobilePanel.classList.toggle("open");
    hamburger.setAttribute("aria-expanded", open ? "true" : "false");
  });
  document.addEventListener("click", function (e) {
    if (!mobilePanel.classList.contains("open")) return;
    if (mobilePanel.contains(e.target) || hamburger.contains(e.target)) return;
    closeMobilePanel();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeMobilePanel();
  });

  var siteNav = document.querySelector(".site-nav");
  var lastScrollY = window.scrollY;
  var ticking = false;
  function onScroll() {
    var y = window.scrollY;
    if (y > lastScrollY && y > 80) {
      siteNav.classList.add("nav-hidden");
      closeMobilePanel();
    } else if (y < lastScrollY) {
      siteNav.classList.remove("nav-hidden");
    }
    lastScrollY = y;
    ticking = false;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) {
      requestAnimationFrame(onScroll);
      ticking = true;
    }
  }, { passive: true });
})();
</script>

<div class="wrap">
  <header class="flat-hero">
    <div class="flat-hero-text">
      <p class="hero-kicker" id="heroKicker">Cotiza USD a ARS al tipo de cambio real</p>
      <h1 id="heroTitle">Dólares americanos a Pesos argentinos</h1>
      <p class="sub">Convertí, enviá y recibí dinero directo desde la app, al tipo de cambio real y sin comisiones ocultas.</p>
      <img class="hero-flags-img" src="data:image/png;base64,__FLAG_STACK__" alt="" aria-hidden="true">
    </div>

    <div class="card hero-card" id="calculator">
      <div class="field">
        <div class="field-labels">
          <span class="field-label">Recibís</span>
          <input class="amount-input" id="fromAmount" inputmode="decimal" autocomplete="off" value="100" aria-label="Monto a convertir">
        </div>
        <div class="currency-picker" id="fromPicker"></div>
      </div>

      <div class="swap-row">
        <button class="swap-btn" id="swapBtn" type="button" aria-label="Invertir monedas" title="Invertir monedas">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M7 10L3 6L7 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3 6H16C18.2091 6 20 7.79086 20 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M17 14L21 18L17 22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M21 18H8C5.79086 18 4 16.2091 4 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <div class="field">
        <div class="field-labels">
          <span class="field-label">Cantidad en Takenos</span>
          <input class="amount-input" id="usdAmount" inputmode="decimal" autocomplete="off" value="0" aria-label="Cantidad en Takenos (USD)">
        </div>
        <div class="fixed-currency-badge">
          <span class="flag-pill"><img class="flag-icon" src="__USD_FLAG__" alt=""></span>
          <span>USD</span>
        </div>
      </div>

      <div class="convert-indicator" aria-hidden="true">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 4v15M6 13l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <div class="field">
        <div class="field-labels">
          <span class="field-label">Convertido a</span>
          <output class="amount-input" id="toAmount" aria-live="polite">0</output>
        </div>
        <div class="currency-picker" id="toPicker"></div>
      </div>

      <div class="rate-breakdown">
        <div class="rate-row rate-row-primary">
          <span class="rate-value" id="rateLine">1 USD = 1 USD</span>
        </div>
        <div class="rate-row">
          <span class="rate-row-label">Comisiones<span class="info-dot" aria-hidden="true">i</span></span>
          <span class="rate-value">Según método de pago</span>
        </div>
        <p class="rate-caption calc-disclaimer">Tipo de cambio medio del mercado a las __ASOF_TIME__<span class="info-dot" aria-hidden="true">i</span></p>
      </div>

      <a class="hero-cta" href="https://takenos.com" target="_blank" rel="noopener">
        <span>Abrí tu cuenta en Takenos</span>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </a>
    </div>
  </header>

  <section class="rates">
    <div class="rates-head">
      <h2>Cotizaciones<span class="info-dot" aria-hidden="true">i</span></h2>
      <span class="rates-note" id="asOf">actualizado __ASOF__</span>
    </div>
    <div class="cotiz-scroll" id="cotizScroll"></div>
  </section>

  <section class="alerts">
    <div class="alerts-card">
      <div class="alerts-head">
        <h2 class="alerts-title"><span class="accent-line">Estate siempre al tanto</span>de los últimos cambios</h2>
        <p class="alerts-sub">Suscribite para recibir alertas de tipo de cambio directo en tu correo y no te pierdas ninguna novedad.</p>
      </div>

      <div class="alerts-row">
        <div class="alerts-row-text">
          <span class="alerts-row-label">Notificaciones diarias</span>
          <span class="alerts-row-desc">Quiero recibir un resumen diario en mi correo</span>
        </div>
        <button class="toggle" id="toggleDaily" type="button" role="switch" aria-checked="false" aria-label="Activar notificaciones diarias">
          <span class="toggle-knob"></span>
        </button>
      </div>

      <div class="alerts-row alerts-row-column">
        <div class="alerts-row-top">
          <div class="alerts-row-text">
            <span class="alerts-row-label">Notificarme cuando</span>
            <span class="alerts-row-desc">Te avisamos apenas el tipo de cambio cruce ese valor</span>
          </div>
          <button class="toggle" id="toggleThreshold" type="button" role="switch" aria-checked="false" aria-label="Activar alerta de tipo de cambio">
            <span class="toggle-knob"></span>
          </button>
        </div>
        <div class="alerts-threshold">
          <div class="alerts-amount">
            <span class="amt-fixed">1</span>
            <div class="currency-picker" id="alertFromPicker"></div>
          </div>
          <div class="currency-picker alerts-direction" id="alertDirectionWrap"></div>
          <div class="alerts-amount">
            <input id="alertThresholdValue" inputmode="decimal" autocomplete="off" value="1.487,75" aria-label="Valor umbral">
            <div class="currency-picker" id="alertToPicker"></div>
          </div>
        </div>
      </div>

      <div class="alerts-email">
        <label class="alerts-row-label" for="alertEmail">Tu dirección de correo electrónico</label>
        <input class="alerts-email-input" id="alertEmail" type="email" placeholder="Correo electrónico..." autocomplete="email">
      </div>

      <button class="alerts-submit" id="alertsSubmit" type="button">Recibir alertas de tipo de cambio</button>
      <p class="alerts-note" id="alertsNote" hidden>&iexcl;Listo! Te avisaremos por correo.</p>
    </div>
  </section>

  <section class="history">
    <div class="rates-head">
      <h2>Historial de tipo de cambio</h2>
    </div>
    <div class="history-top">
      <div class="currency-toggle" id="historyCurrencyToggle"></div>
      <span class="history-rate" id="historyRate"></span>
    </div>
    <div class="chart-card">
      <div class="range-tabs" id="historyRangeTabs"></div>
      <div class="chart-wrap" id="chartWrap">
        <svg id="historyChart" viewBox="0 0 600 220" preserveAspectRatio="none"></svg>
        <div class="chart-tooltip" id="chartTooltip">
          <div class="tt-date" id="ttDate"></div>
          <div class="tt-value" id="ttValue"></div>
        </div>
      </div>
      <p class="chart-note" id="chartNote"></p>
    </div>
  </section>

  <p class="rates-disclaimer">Tasas de referencia de Takenos, no incluyen comisiones de terceros ni de medios de pago. &middot; Este tipo de cambio aplica únicamente a depósitos y retiros, no a pagos con la TakeCard.</p>

  <footer class="site-footer">
    <div class="footer-bg" aria-hidden="true"></div>
    <div class="footer-card">
      <div class="footer-top">
        <div class="footer-brand">
          <a class="footer-logo" href="https://takenos.com" target="_blank" rel="noopener" aria-label="Takenos">
            <span class="logo-light">__LOGO_BLACK_SVG__</span>
            <span class="logo-dark">__LOGO_SVG__</span>
          </a>
          <p class="footer-legal">Global Flow S.A.U, CUIT: 30-71825754-5., es un proveedor de servicios de activos virtuales (en adelante, &ldquo;PSAV&rdquo;) debidamente inscrito bajo el N&deg;54 en el Registro de PSAV de la Comisión Nacional de Valores (República Argentina).</p>
          <a class="footer-email" href="mailto:support@takenos.com">support@takenos.com</a>
        </div>
        <nav class="footer-links-col">
          <a class="current" href="https://takenos.com" target="_blank" rel="noopener">Inicio</a>
          <a href="https://takenos.com/blog" target="_blank" rel="noopener">Blog</a>
          <a href="https://takenos.com/notas-medios" target="_blank" rel="noopener">En los Medios</a>
          <a href="https://takenos.com/business" target="_blank" rel="noopener">Cuenta empresa</a>
          <a href="https://takenos.com/inversiones" target="_blank" rel="noopener">Inversiones</a>
          <a href="https://takenos.com/tarjeta-internacional" target="_blank" rel="noopener">Tarjeta internacional</a>
        </nav>
        <nav class="footer-links-col">
          <a href="https://takenos.com/promociones" target="_blank" rel="noopener">Promociones</a>
          <a href="https://help.takenos.com/en/" target="_blank" rel="noopener">Preguntas frecuentes</a>
          <a href="https://takenos.peopleforce.io/careers" target="_blank" rel="noopener">Súmate al equipo</a>
          <a href="https://help.takenos.com/en/articles/11403392-terminos-y-condiciones" target="_blank" rel="noopener">Términos y condiciones</a>
          <a href="https://help.takenos.com/en/articles/11403396-politicas-de-privacidad" target="_blank" rel="noopener">Políticas de privacidad</a>
        </nav>
      </div>
      <div class="footer-social">
        <a href="https://x.com/TakenosApp" target="_blank" rel="noopener" aria-label="X (Twitter)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 4l16 16M20 4L4 20" stroke-linecap="round"/></svg>
        </a>
        <a href="https://www.instagram.com/takenosapp" target="_blank" rel="noopener" aria-label="Instagram">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17" cy="7" r="1" fill="currentColor" stroke="none"/></svg>
        </a>
        <a href="https://www.tiktok.com/@takenos_app" target="_blank" rel="noopener" aria-label="TikTok">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M15 3v10.5a3.5 3.5 0 1 1-3.5-3.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 3c0 3 2.5 5 5 5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </a>
        <a href="https://www.linkedin.com/company/takenos/" target="_blank" rel="noopener" aria-label="LinkedIn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="3"/><path d="M8 10.5v6M8 7.8v.1M12.5 16.5v-3.7c0-1.1.7-1.9 2-1.9 1.2 0 1.8.8 1.8 1.9v3.7M12.5 12.3v4.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </a>
      </div>
    </div>
  </footer>
</div>

<script>
(function () {
  var RATES = __RATES_JSON__;
  RATES.USD = { buy: 1, sell: 1, name: "Dólar estadounidense", decimals: 2 };
  var FLAGS = __FLAGS_JSON__;
  var ORDER = ["USD", "ARS", "BRL", "MXN", "COP", "CLP", "PEN", "BOB", "PYG", "EUR", "GBP"];
  var ORDER_NO_USD = ORDER.filter(function (c) { return c !== "USD"; });
  var PLURAL_NAMES = {
    USD: "Dólares americanos",
    ARS: "Pesos argentinos",
    BOB: "Bolivianos",
    MXN: "Pesos mexicanos",
    BRL: "Reales brasileños",
    EUR: "Euros",
    CLP: "Pesos chilenos",
    GBP: "Libras esterlinas",
    PYG: "Guaraníes paraguayos",
    COP: "Pesos colombianos",
    PEN: "Soles peruanos"
  };

  var state = { from: "BRL", to: "ARS" };

  function toUSD(amount, cur) {
    if (cur === "USD") return amount;
    return amount / RATES[cur].buy;
  }
  function fromUSD(amountUsd, cur) {
    if (cur === "USD") return amountUsd;
    return amountUsd * RATES[cur].sell;
  }
  function convert(amount, from, to) {
    if (from === to) return amount;
    return fromUSD(toUSD(amount, from), to);
  }
  function fmt(value, cur) {
    var d = RATES[cur].decimals;
    return value.toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function fmtRate(value) {
    var d = value >= 100 ? 2 : 4;
    return value.toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function flagImg(code) {
    return '<span class="flag-pill"><img class="flag-icon" src="' + FLAGS[code] + '" alt=""></span>';
  }

  function buildPicker(containerId, selected, onChange, orderList) {
    var list = orderList || ORDER;
    var container = document.getElementById(containerId);
    var btn = document.createElement("button");
    btn.className = "picker-btn";
    btn.type = "button";
    btn.setAttribute("aria-haspopup", "listbox");
    btn.setAttribute("aria-expanded", "false");

    var panel = document.createElement("div");
    panel.className = "picker-panel";
    panel.setAttribute("role", "listbox");

    function renderBtn() {
      btn.innerHTML =
        flagImg(selected.value) + '<span>' + selected.value + '</span>' +
        '<svg class="chev" width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">' +
        '<path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }

    function renderPanel() {
      panel.innerHTML = "";
      list.forEach(function (code) {
        var r = RATES[code];
        var row = document.createElement("button");
        row.type = "button";
        row.className = "picker-row";
        row.setAttribute("role", "option");
        row.setAttribute("aria-selected", code === selected.value ? "true" : "false");
        row.innerHTML =
          flagImg(code) + '<span class="code">' + code + '</span>' +
          '<span class="name">' + r.name + '</span>';
        row.addEventListener("click", function () {
          selected.value = code;
          renderBtn();
          renderPanel();
          closePanel();
          onChange();
        });
        panel.appendChild(row);
      });
    }

    function openPanel() {
      panel.classList.add("open");
      btn.setAttribute("aria-expanded", "true");
      document.addEventListener("click", outsideClick, true);
    }
    function closePanel() {
      panel.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
      document.removeEventListener("click", outsideClick, true);
    }
    function outsideClick(e) {
      if (!container.contains(e.target)) closePanel();
    }

    btn.addEventListener("click", function () {
      panel.classList.contains("open") ? closePanel() : openPanel();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closePanel();
    });

    renderBtn();
    renderPanel();
    container.appendChild(btn);
    container.appendChild(panel);

    return { refresh: function () { renderBtn(); renderPanel(); } };
  }

  var fromSel = { value: state.from };
  var toSel = { value: state.to };

  function parseAmount(id) {
    var raw = document.getElementById(id).value.replace(/\./g, "").replace(",", ".");
    var amount = parseFloat(raw);
    if (isNaN(amount) || amount < 0) amount = 0;
    return amount;
  }

  function refreshRateAndHero() {
    var rate = convert(1, state.from, state.to);
    document.getElementById("rateLine").innerHTML =
      "1 " + state.from + " = <span class=\"rate-value-strong\">" + fmtRate(rate) + " " + state.to + "</span>";
    document.querySelectorAll("#cotizScroll .cotiz-card").forEach(function (card) {
      card.classList.toggle("active", card.dataset.code === state.to || card.dataset.code === state.from);
    });
    var heroTitle = document.getElementById("heroTitle");
    var heroKicker = document.getElementById("heroKicker");
    if (heroTitle) heroTitle.textContent = (PLURAL_NAMES[state.from] || state.from) + " a " + (PLURAL_NAMES[state.to] || state.to);
    if (heroKicker) heroKicker.textContent = "Cotiza " + state.from + " a " + state.to + " al tipo de cambio real";
  }

  function recompute() {
    state.from = fromSel.value;
    state.to = toSel.value;
    var amount = parseAmount("fromAmount");
    var result = convert(amount, state.from, state.to);
    document.getElementById("toAmount").textContent = fmt(result, state.to);
    document.getElementById("usdAmount").value = fmt(toUSD(amount, state.from), "USD");
    refreshRateAndHero();
  }

  function recomputeFromUsd() {
    state.from = fromSel.value;
    state.to = toSel.value;
    var usdAmount = parseAmount("usdAmount");
    document.getElementById("fromAmount").value = fmt(fromUSD(usdAmount, state.from), state.from);
    document.getElementById("toAmount").textContent = fmt(fromUSD(usdAmount, state.to), state.to);
    refreshRateAndHero();
  }

  var fromPicker = buildPicker("fromPicker", fromSel, recompute, ORDER_NO_USD);
  var toPicker = buildPicker("toPicker", toSel, recompute, ORDER_NO_USD);

  document.getElementById("fromAmount").addEventListener("input", recompute);
  document.getElementById("usdAmount").addEventListener("input", recomputeFromUsd);

  document.getElementById("swapBtn").addEventListener("click", function () {
    this.classList.toggle("spun");
    var tmp = fromSel.value;
    fromSel.value = toSel.value;
    toSel.value = tmp;
    fromPicker.refresh();
    toPicker.refresh();
    recompute();
  });

  var cotizScroll = document.getElementById("cotizScroll");
  ORDER_NO_USD.forEach(function (code) {
    var r = RATES[code];
    var card = document.createElement("div");
    card.className = "cotiz-card";
    card.dataset.code = code;
    card.innerHTML =
      '<div class="cotiz-pair">' + flagImg("USD") + 'USD' +
      '<span class="swap-ic">&#8644;</span>' + flagImg(code) + code + '</div>' +
      '<div class="cotiz-values">' +
      '<div class="cotiz-col"><span class="cotiz-label">Recibís</span>' +
      '<span class="cotiz-value">' + fmt(r.buy, code) + '</span></div>' +
      '<div class="cotiz-col"><span class="cotiz-label">Enviás</span>' +
      '<span class="cotiz-value">' + fmt(r.sell, code) + '</span></div>' +
      '</div>';
    card.addEventListener("click", function () {
      toSel.value = code;
      toPicker.refresh();
      recompute();
    });
    cotizScroll.appendChild(card);
  });

  function updateCotizFade() {
    var maxScroll = cotizScroll.scrollWidth - cotizScroll.clientWidth;
    var atStart = cotizScroll.scrollLeft <= 2;
    var atEnd = cotizScroll.scrollLeft >= maxScroll - 2;
    var leftStop = atStart ? "0px" : "28px";
    var rightStop = atEnd ? "0px" : "28px";
    var mask = "linear-gradient(to right, transparent 0, black " + leftStop + ", black calc(100% - " + rightStop + "), transparent 100%)";
    cotizScroll.style.webkitMaskImage = mask;
    cotizScroll.style.maskImage = mask;
  }
  cotizScroll.addEventListener("scroll", updateCotizFade);
  window.addEventListener("resize", updateCotizFade);
  updateCotizFade();

  recompute();

  // Cotización ARS en vivo: pega a un Web App de Apps Script que hace de
  // proxy (server-side, sin problema de CORS) hacia la cotización USDT de
  // Takenos en https://api.dolarito.ar. Si LIVE_RATE_URL está vacío o el
  // fetch falla, se queda silenciosamente con el snapshot estático de RATES.
  var LIVE_RATE_URL = "__LIVE_RATE_URL__";
  var LIVE_REFRESH_MS = 5 * 60 * 1000;

  function applyLiveArsRate(data) {
    if (!data || typeof data.buy !== "number" || typeof data.sell !== "number") return;
    RATES.ARS.buy = data.buy;
    RATES.ARS.sell = data.sell;
    var card = cotizScroll.querySelector('.cotiz-card[data-code="ARS"]');
    if (card) {
      var values = card.querySelectorAll(".cotiz-value");
      if (values[0]) values[0].textContent = fmt(data.buy, "ARS");
      if (values[1]) values[1].textContent = fmt(data.sell, "ARS");
    }
    var asOf = document.getElementById("asOf");
    if (asOf) {
      asOf.textContent = "ARS en vivo · actualizado " +
        new Date().toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" });
    }
    recompute();
  }

  function fetchLiveArsRate() {
    if (!LIVE_RATE_URL) return;
    fetch(LIVE_RATE_URL)
      .then(function (res) { return res.ok ? res.json() : null; })
      .then(applyLiveArsRate)
      .catch(function () { /* sin conexión al proxy: se mantiene el snapshot estático */ });
  }

  fetchLiveArsRate();
  setInterval(fetchLiveArsRate, LIVE_REFRESH_MS);

  var HISTORY = __HISTORY_JSON__;
  var RANGES = [
    { key: "6m", label: "6 meses", days: 180 },
    { key: "3m", label: "3 meses", days: 90 },
    { key: "1m", label: "1 mes", days: 30 },
    { key: "2w", label: "2 semanas", days: 14 },
    { key: "1w", label: "1 semana", days: 7 }
  ];
  var HIST_CURRENCIES = Object.keys(HISTORY);
  var histState = { currency: HIST_CURRENCIES[0], range: null };
  var MONTHS_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

  function rangeSpanDays(series) {
    var first = new Date(series[0].d + "T00:00:00Z");
    var last = new Date(series[series.length - 1].d + "T00:00:00Z");
    return Math.round((last - first) / 86400000);
  }
  function rangeAvailable(series, days) {
    return rangeSpanDays(series) >= days - 1;
  }
  function filterRange(series, days) {
    var last = new Date(series[series.length - 1].d + "T00:00:00Z");
    var cutoff = new Date(last.getTime() - (days - 1) * 86400000);
    return series.filter(function (p) { return new Date(p.d + "T00:00:00Z") >= cutoff; });
  }
  function defaultRangeFor(series) {
    for (var i = 0; i < RANGES.length; i++) {
      if (rangeAvailable(series, RANGES[i].days)) return RANGES[i].key;
    }
    return RANGES[RANGES.length - 1].key;
  }
  function fmtDateShort(dstr) {
    var parts = dstr.split("-");
    return parseInt(parts[2], 10) + " " + MONTHS_ES[parseInt(parts[1], 10) - 1];
  }

  function renderCurrencyToggle() {
    var el = document.getElementById("historyCurrencyToggle");
    el.innerHTML = "";
    HIST_CURRENCIES.forEach(function (code) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = code;
      btn.className = code === histState.currency ? "active" : "";
      btn.addEventListener("click", function () {
        histState.currency = code;
        histState.range = defaultRangeFor(HISTORY[code]);
        renderCurrencyToggle();
        renderRangeTabs();
        renderChart();
      });
      el.appendChild(btn);
    });
  }

  function renderRangeTabs() {
    var el = document.getElementById("historyRangeTabs");
    el.innerHTML = "";
    var series = HISTORY[histState.currency];
    RANGES.forEach(function (r) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = r.label;
      var available = rangeAvailable(series, r.days);
      btn.disabled = !available;
      if (!available) btn.title = "Todavía no hay " + r.label + " de historial para esta moneda";
      if (r.key === histState.range) btn.className = "active";
      btn.addEventListener("click", function () {
        if (btn.disabled) return;
        histState.range = r.key;
        renderRangeTabs();
        renderChart();
      });
      el.appendChild(btn);
    });
  }

  function renderChart() {
    var series = HISTORY[histState.currency];
    var rangeDef = RANGES.filter(function (r) { return r.key === histState.range; })[0];
    var data = filterRange(series, rangeDef.days);
    var cur = histState.currency;

    var last = data[data.length - 1];
    document.getElementById("historyRate").innerHTML =
      "1 USD = <b>" + fmt(last.buy, cur) + " " + cur + "</b>";

    var spanDays = rangeSpanDays(series);
    document.getElementById("chartNote").textContent =
      spanDays < rangeDef.days - 1 ? "Historial disponible desde el " + fmtDateShort(series[0].d) + "." : "";

    var W = 600, H = 220, padL = 54, padR = 10, padT = 14, padB = 26;
    var plotW = W - padL - padR, plotH = H - padT - padB;
    var values = data.map(function (p) { return p.buy; });
    var min = Math.min.apply(null, values), max = Math.max.apply(null, values);
    var span = (max - min) || Math.max(1, max * 0.02);
    var yPad = span * 0.12;
    var yMin = min - yPad, yMax = max + yPad;

    function xAt(i) { return padL + (data.length === 1 ? plotW / 2 : (i / (data.length - 1)) * plotW); }
    function yAt(v) { return padT + (1 - (v - yMin) / (yMax - yMin)) * plotH; }

    var linePoints = data.map(function (p, i) { return xAt(i) + "," + yAt(p.buy); }).join(" ");
    var areaPoints = linePoints + " " + xAt(data.length - 1) + "," + (padT + plotH) + " " + xAt(0) + "," + (padT + plotH);
    var gridLines = [yMax - (yMax - yMin) * 0.02, (yMin + yMax) / 2, yMin + (yMax - yMin) * 0.02];
    var dCount = data.length;

    var svg = document.getElementById("historyChart");
    var dotsMarkup = data.map(function (p, i) {
      return '<circle class="chart-dot" data-i="' + i + '" cx="' + xAt(i) + '" cy="' + yAt(p.buy) + '" r="4"></circle>';
    }).join("");

    svg.innerHTML =
      gridLines.map(function (v) {
        return '<line class="chart-gridline" x1="' + padL + '" x2="' + (W - padR) + '" y1="' + yAt(v) + '" y2="' + yAt(v) + '"></line>' +
          '<text class="chart-axis-label" x="2" y="' + (yAt(v) + 3) + '">' + fmt(v, cur) + '</text>';
      }).join("") +
      '<polygon class="chart-area" points="' + areaPoints + '"></polygon>' +
      '<polyline class="chart-line" points="' + linePoints + '"></polyline>' +
      '<text class="chart-axis-label" x="' + xAt(0) + '" y="' + (H - 4) + '">' + fmtDateShort(data[0].d) + '</text>' +
      '<text class="chart-axis-label" x="' + xAt(dCount - 1) + '" y="' + (H - 4) + '" text-anchor="end">' + fmtDateShort(data[dCount - 1].d) + '</text>' +
      '<line class="chart-guide" id="chartGuide" x1="0" x2="0" y1="' + padT + '" y2="' + (padT + plotH) + '"></line>' +
      dotsMarkup +
      '<rect id="chartOverlay" x="' + padL + '" y="0" width="' + plotW + '" height="' + H + '" fill="transparent"></rect>';

    var overlay = document.getElementById("chartOverlay");
    var guide = document.getElementById("chartGuide");
    var tooltip = document.getElementById("chartTooltip");

    function showAt(i) {
      var p = data[i];
      guide.setAttribute("x1", xAt(i));
      guide.setAttribute("x2", xAt(i));
      guide.style.opacity = "1";
      svg.querySelectorAll(".chart-dot").forEach(function (dot) {
        dot.style.opacity = dot.dataset.i == i ? "1" : "0";
      });
      var rect = svg.getBoundingClientRect();
      var px = xAt(i) * (rect.width / W);
      var py = yAt(p.buy) * (rect.height / H);
      tooltip.style.left = px + "px";
      tooltip.style.top = py + "px";
      tooltip.style.opacity = "1";
      document.getElementById("ttDate").textContent = fmtDateShort(p.d);
      document.getElementById("ttValue").textContent = "1 USD = " + fmt(p.buy, cur) + " " + cur;
    }
    function hide() {
      guide.style.opacity = "0";
      svg.querySelectorAll(".chart-dot").forEach(function (dot) { dot.style.opacity = "0"; });
      tooltip.style.opacity = "0";
    }
    function handleMove(clientX) {
      var rect = svg.getBoundingClientRect();
      var xSvg = (clientX - rect.left) * (W / rect.width);
      var idx = Math.round(((xSvg - padL) / plotW) * (dCount - 1));
      idx = Math.max(0, Math.min(dCount - 1, idx));
      showAt(idx);
    }
    overlay.addEventListener("mousemove", function (e) { handleMove(e.clientX); });
    overlay.addEventListener("mouseleave", hide);
    overlay.addEventListener("touchstart", function (e) { handleMove(e.touches[0].clientX); }, { passive: true });
    overlay.addEventListener("touchmove", function (e) { handleMove(e.touches[0].clientX); }, { passive: true });
    overlay.addEventListener("touchend", hide);
  }

  histState.range = defaultRangeFor(HISTORY[histState.currency]);
  renderCurrencyToggle();
  renderRangeTabs();
  renderChart();

  function initToggle(id) {
    var btn = document.getElementById(id);
    btn.addEventListener("click", function () {
      var checked = btn.getAttribute("aria-checked") === "true";
      btn.setAttribute("aria-checked", checked ? "false" : "true");
    });
  }
  initToggle("toggleDaily");
  initToggle("toggleThreshold");

  var alertFromSel = { value: "USD" };
  var alertToSel = { value: "ARS" };
  buildPicker("alertFromPicker", alertFromSel, function () {});
  buildPicker("alertToPicker", alertToSel, function () {});

  function buildDirectionPicker(containerId, selected, onChange) {
    var container = document.getElementById(containerId);
    var options = [
      { value: "down", label: "Baje de", color: "var(--aji)", icon: '<path d="M2.25 6L9 12.75l4.306-4.306a11.95 11.95 0 0 1 5.814 5.518l2.74 1.22m0 0l-5.94 2.28m5.94-2.28l-2.28-5.94" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>' },
      { value: "up", label: "Suba de", color: "var(--accent)", icon: '<path d="M2.25 18L9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.94" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>' }
    ];
    function optionByValue(v) { return options.filter(function (o) { return o.value === v; })[0]; }

    var btn = document.createElement("button");
    btn.className = "picker-btn";
    btn.type = "button";
    btn.setAttribute("aria-haspopup", "listbox");
    btn.setAttribute("aria-expanded", "false");

    var panel = document.createElement("div");
    panel.className = "picker-panel";
    panel.setAttribute("role", "listbox");

    function dirIcon(opt) {
      return '<svg class="dir-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" style="color:' + opt.color + '" aria-hidden="true">' + opt.icon + '</svg>';
    }
    function renderBtn() {
      var opt = optionByValue(selected.value);
      btn.innerHTML =
        dirIcon(opt) + '<span>' + opt.label + '</span>' +
        '<svg class="chev" width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">' +
        '<path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }
    function renderPanel() {
      panel.innerHTML = "";
      options.forEach(function (opt) {
        var row = document.createElement("button");
        row.type = "button";
        row.className = "picker-row";
        row.setAttribute("role", "option");
        row.setAttribute("aria-selected", opt.value === selected.value ? "true" : "false");
        row.innerHTML = dirIcon(opt) + '<span class="name">' + opt.label + '</span>';
        row.addEventListener("click", function () {
          selected.value = opt.value;
          renderBtn();
          renderPanel();
          closePanel();
          onChange();
        });
        panel.appendChild(row);
      });
    }
    function openPanel() {
      panel.classList.add("open");
      btn.setAttribute("aria-expanded", "true");
      document.addEventListener("click", outsideClick, true);
    }
    function closePanel() {
      panel.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
      document.removeEventListener("click", outsideClick, true);
    }
    function outsideClick(e) {
      if (!container.contains(e.target)) closePanel();
    }
    btn.addEventListener("click", function () {
      panel.classList.contains("open") ? closePanel() : openPanel();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closePanel();
    });

    renderBtn();
    renderPanel();
    container.appendChild(btn);
    container.appendChild(panel);
    return { refresh: function () { renderBtn(); renderPanel(); } };
  }

  var alertDirectionSel = { value: "down" };
  buildDirectionPicker("alertDirectionWrap", alertDirectionSel, function () {});

  var alertsSubmit = document.getElementById("alertsSubmit");
  var alertsNote = document.getElementById("alertsNote");
  var alertEmail = document.getElementById("alertEmail");
  alertsSubmit.addEventListener("click", function () {
    if (!alertEmail.value || !alertEmail.checkValidity()) {
      alertEmail.focus();
      return;
    }
    alertsNote.hidden = false;
  });
})();
</script>
"""

def scale_css_sizes(css_text, factor=1.2):
    props = [
        "font-size", "padding-top", "padding-bottom", "padding-left", "padding-right", "padding",
        "margin-top", "margin-bottom", "margin-left", "margin-right", "margin",
        "gap", "row-gap", "column-gap",
        "width", "height", "min-height", "max-height", "min-width",
        "top", "left", "right", "bottom",
        "border-radius",
    ]
    prop_pattern = r"(?<![\w-])(" + "|".join(props) + r")(\s*:\s*)([^;]+)(;)"

    def scale_value(value):
        def repl_num(m):
            num = float(m.group(1))
            scaled = num * factor
            text = str(int(scaled)) if scaled == int(scaled) else str(round(scaled, 1))
            return text + "px"
        return re.sub(r"(-?\d+(?:\.\d+)?)px", repl_num, value)

    def repl(m):
        return m.group(1) + m.group(2) + scale_value(m.group(3)) + m.group(4)

    return re.sub(prop_pattern, repl, css_text)


style_match = re.search(r"(<style>)([\s\S]*?)(</style>)", html)
scaled_style = scale_css_sizes(style_match.group(2))
html = html[:style_match.start(2)] + scaled_style + html[style_match.end(2):]

html = html.replace("__SG__", sg)
html = html.replace("__LOGO_SVG__", logo_svg)
html = html.replace("__LOGO_BLACK_SVG__", logo_black_svg)
html = html.replace("__FLAG_STACK__", flag_stack_b64)
html = html.replace("__FOOTER_PATTERN__", footer_pattern_b64)
html = html.replace("__RATES_JSON__", rates_json)
html = html.replace("__FLAGS_JSON__", flags_json)
html = html.replace("__USD_FLAG__", flags["USD"])
html = html.replace("__HISTORY_JSON__", history_json)
html = html.replace("__ASOF__", "14 ago 2026")
html = html.replace("__ASOF_TIME__", "16:20")
html = html.replace("__LIVE_RATE_URL__", LIVE_RATE_URL)

open(OUT_DIR / "conversor-takenos.html", "w").write(html)
print("bytes:", len(html.encode()))
