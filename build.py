#!/usr/bin/env python3
"""Generates the static Logic Mix site (8 languages) from content/. Output goes to the repository root.

Usage: python3 build.py [--check]   (--check fails when generated files are out of date)
Edit content/*.md, content/ui.json, content/*.properties, never the generated HTML.
"""
import html, re, sys
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
C = ROOT / "content"
LANGS = ["en", "ru", "uk", "it", "de", "fr", "es", "zh-CN"]
UI = json.loads((C / "ui.json").read_text(encoding="utf-8"))
URL = re.compile(r"https://[^\s)]+")


def props(name):
    d = {}
    for line in (C / name).read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    return d


PRIV = props("privacy_config.properties")
SITE = props("site.properties")
EMAIL = PRIV.get("contactEmail") or SITE.get("contactEmail", "")


def sub(t):
    for val, ph in ((PRIV.get("version"), "[VERSION]"), (PRIV.get("effectiveDate"), "[EFFECTIVE_DATE]"), (EMAIL, "[CONTACT_EMAIL]")):
        if val:
            t = t.replace(ph, val)
    return t


def inline(t):
    esc = html.escape(t, quote=True)
    esc = URL.sub(lambda m: f'<a href="{m.group(0)}" rel="noopener">{m.group(0)}</a>', esc)
    return re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", lambda m: f'<a href="mailto:{m.group(0)}">{m.group(0)}</a>', esc)


def md(text):
    out, para, bullets, meta = [], [], [], 0

    def flush():
        if para:
            out.append("<p>" + "<br>".join(inline(x) for x in para) + "</p>")
            para.clear()
        if bullets:
            out.append("<ul>" + "".join(f"<li>{inline(b)}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for raw in text.splitlines():
        l = sub(raw.rstrip())
        if not l.strip():
            flush()
        elif l.startswith("## "):
            flush(); out.append(f"<h2>{inline(l[3:])}</h2>")
        elif l.startswith("# "):
            flush(); out.append(f"<h1>{inline(l[2:])}</h1>"); meta = 2
        elif l.startswith("- "):
            if para: flush()
            bullets.append(l[2:])
        elif meta > 0:
            flush(); out.append(f'<p class="meta">{inline(l)}</p>'); meta -= 1
        else:
            if bullets: flush()
            para.append(l)
    flush()
    return "\n".join(out)


CSS = """:root{--bg1:#0f1b45;--bg2:#08112c;--bg3:#040919;--gold:#f5c84b;--gold2:#ffe9a8;--fg:#e8edf8;--muted:#a3aec6;--card:rgba(255,255,255,.05);--line:rgba(245,200,75,.28)}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;min-height:100vh;color:var(--fg);background:linear-gradient(180deg,var(--bg1),var(--bg2) 45%,var(--bg3)) fixed;font:16px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans","PingFang SC","Microsoft YaHei",sans-serif}
a{color:var(--gold);word-break:break-word}a:hover{color:var(--gold2)}
.wrap{max-width:960px;margin:0 auto;padding:0 1.25rem}
header{position:sticky;top:0;z-index:10;backdrop-filter:blur(10px);background:rgba(8,17,44,.8);border-bottom:1px solid var(--line)}
header .wrap{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;padding-top:.7rem;padding-bottom:.7rem}
.brand{font-weight:800;font-size:1.2rem;color:var(--gold);text-decoration:none;letter-spacing:.3px}
nav{display:flex;gap:1rem;flex-wrap:wrap;flex:1}nav a{color:var(--fg);text-decoration:none;opacity:.85}nav a:hover,nav a[aria-current]{opacity:1;color:var(--gold)}
details.lang{position:relative}details.lang summary{cursor:pointer;list-style:none;padding:.3rem .8rem;border:1px solid var(--line);border-radius:.6rem;background:var(--card)}
details.lang summary::-webkit-details-marker{display:none}
details.lang div{position:absolute;right:0;margin-top:.4rem;min-width:11rem;padding:.4rem;border:1px solid var(--line);border-radius:.8rem;background:#0b1636;display:grid;gap:.1rem}
details.lang a{padding:.35rem .7rem;border-radius:.5rem;color:var(--fg);text-decoration:none}details.lang a:hover,details.lang a[aria-current]{background:var(--card);color:var(--gold)}
.hero{padding:4rem 0 2.5rem;text-align:center}
.hero h1{font-size:clamp(2rem,6vw,3.4rem);line-height:1.15;margin:0 0 1rem;background:linear-gradient(180deg,#fff,var(--gold2) 55%,var(--gold));-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{max-width:640px;margin:0 auto;color:var(--muted);font-size:1.1rem}
section{padding:1.8rem 0}section>h2{font-size:1.5rem;margin:0 0 1rem;color:var(--gold)}
.card{background:var(--card);border:1px solid var(--line);border-radius:1.1rem;padding:1.2rem 1.4rem}
.pills{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1.4rem;justify-content:center}.pills span{padding:.4rem .9rem;border-radius:999px;border:1px solid var(--line);background:var(--card);font-size:.95rem}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem}
.grid div{aspect-ratio:1.5;display:flex;align-items:center;justify-content:center;text-align:center;padding:.6rem;border-radius:1rem;border:1px solid var(--line);background:var(--card);font-weight:700}
@media(max-width:560px){.grid{grid-template-columns:repeat(2,1fr)}}
main.doc{padding:2rem 0 3rem}main.doc h1{font-size:1.9rem;color:var(--gold);margin-top:0}main.doc h2{font-size:1.15rem;margin-top:2rem;color:var(--gold2)}
.meta{color:var(--muted);margin:.2rem 0}
.draft{margin:1rem 0;padding:.7rem 1rem;border-left:4px solid var(--gold);background:var(--card);border-radius:.4rem}
footer{border-top:1px solid var(--line);padding:1.6rem 0 2.5rem;color:var(--muted);font-size:.92rem}footer .wrap{display:flex;flex-wrap:wrap;gap:.6rem 1.4rem;justify-content:space-between}
footer nav{flex:none}
"""

PAGES = {"home": "", "privacy": "privacy/", "terms": "terms/"}


def href(tag, page, from_depth):
    return "../" * from_depth + f"{tag}/{PAGES[page]}index.html"


def layout(tag, page, body):
    u = UI[tag]
    depth = 1 if page == "home" else 2
    root = "../" * depth
    nav = "".join(
        f'<a href="{href(tag, p, depth)}"{" aria-current=\"page\"" if p == page else ""}>{u[k]}</a>'
        for p, k in (("home", "home"), ("privacy", "privacy"), ("terms", "terms"))
    )
    langs = "".join(
        f'<a href="{href(t, page, depth)}" hreflang="{t}" lang="{t}"{" aria-current=\"true\"" if t == tag else ""}>{UI[t]["name"]}</a>' for t in LANGS
    )
    alts = "".join(f'<link rel="alternate" hreflang="{t}" href="{href(t, page, depth)}">' for t in LANGS)
    foot = " ".join(f'<a href="{href(tag, p, depth)}">{u[k]}</a>' for p, k in (("privacy", "privacy"), ("terms", "terms")))
    contact = f'<a href="mailto:{EMAIL}">{EMAIL}</a>' if EMAIL else ""
    return f"""<!doctype html>
<html lang="{tag}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="theme-color" content="#08112c">
<title>Logic Mix — {u[page if page != 'home' else 'home']}</title>{alts}
<link rel="stylesheet" href="{root}style.css"></head>
<body><header><div class="wrap"><a class="brand" href="{href(tag, 'home', depth)}">Logic Mix</a><nav aria-label="Main">{nav}</nav>
<details class="lang"><summary aria-label="{u['lang']}">{u['name']} ▾</summary><div>{langs}</div></details></div></header>
{body}
<footer><div class="wrap"><span>© AKYneX studio. {u['rights']}</span><nav aria-label="{u['legal']}">{foot} {contact}</nav></div></footer>
</body></html>
"""


def draft_banner(u):
    if EMAIL and "DRAFT" not in PRIV.get("version", "").upper():
        return ""
    return f'<p class="draft">{html.escape(u["draft"])}</p>'


def home(tag):
    u = UI[tag]
    pills = "".join(f"<span>{html.escape(f)}</span>" for f in u["feats"])
    cats = "".join(f"<div>{html.escape(c)}</div>" for c in u["cats"])
    dev = html.escape(u["dev"])
    contact = f'<p><strong>{u["contact"]}:</strong> <a href="mailto:{EMAIL}">{EMAIL}</a></p>' if EMAIL else ""
    return f"""<main class="wrap"><div class="hero"><h1>{html.escape(u['title'])}</h1><p>{html.escape(u['sub'])}</p><div class="pills" aria-label="{u['feat_t']}">{pills}</div></div>
<section id="about"><h2>{u['about_t']}</h2><div class="card"><p>{html.escape(u['about'])}</p></div></section>
<section id="categories"><h2>{u['cats_t']}</h2><div class="grid">{cats}</div></section>
<section id="developer"><h2>{u['dev_t']}</h2><div class="card"><p>{dev}</p>{contact}</div></section></main>"""


def doc(tag, kind):
    u = UI[tag]
    text = (C / f"{kind}_{tag}.md").read_text(encoding="utf-8")
    return f'<main class="wrap doc">{draft_banner(u)}{md(text)}</main>'


def build():
    f = {"style.css": CSS, ".nojekyll": ""}
    for t in LANGS:
        f[f"{t}/index.html"] = layout(t, "home", home(t))
        f[f"{t}/privacy/index.html"] = layout(t, "privacy", doc(t, "privacy"))
        f[f"{t}/terms/index.html"] = layout(t, "terms", doc(t, "terms"))
    links = " ".join(f'<a href="{t}/index.html">{UI[t]["name"]}</a>' for t in LANGS)
    tags = json.dumps({t.split("-")[0].lower(): t for t in LANGS})
    f["index.html"] = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Logic Mix</title><meta http-equiv="refresh" content="3;url=en/index.html"><link rel="stylesheet" href="style.css"></head>
<body><main class="wrap"><div class="hero"><h1>Logic Mix</h1><p>{links}</p></div></main>
<script>var m={tags},l=(navigator.language||'en').split('-')[0].toLowerCase();location.replace((m[l]||'en')+'/index.html');</script></body></html>
"""
    return f


if __name__ == "__main__":
    files = build()
    if "--check" in sys.argv:
        bad = [n for n, t in files.items() if not (ROOT / n).exists() or (ROOT / n).read_text(encoding="utf-8") != t]
        print("Out of date: " + ", ".join(bad) if bad else "site is up to date")
        sys.exit(1 if bad else 0)
    for n, t in files.items():
        p = ROOT / n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(t, encoding="utf-8")
    print(f"Wrote {len(files)} files")
