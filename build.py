#!/usr/bin/env python3
"""Generates the static AKYneX Studio site (8 languages) from content/. Output goes to the repository root.

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


STUDIO = json.loads((C / "ui_studio.json").read_text(encoding="utf-8"))
GAMES = json.loads((C / "games.json").read_text(encoding="utf-8"))
BRAND = "AKYneX Studio"
MARK = next((p for p in ("assets/brand/logo-mark.png", "assets/brand/logo-mark.webp", "assets/brand/logo-mark.svg") if (ROOT / p).exists()), None)
WIDE = next((p for p in ("assets/brand/logo-wide.png", "assets/brand/logo-wide.webp", "assets/brand/logo-wide.svg") if (ROOT / p).exists()), None)

CSS = """:root{--bg1:#0b1230;--bg2:#070c20;--bg3:#04060f;--cyan:#19c8ff;--blue:#2f6bff;--violet:#a23bff;--pink:#ff4fd8;--orange:#ffa21a;--gold:#f5c84b;--gold2:#ffe9a8;--fg:#e8edf8;--muted:#a3aec6;--card:rgba(255,255,255,.05);--line:rgba(120,160,255,.25)}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;min-height:100vh;display:flex;flex-direction:column;color:var(--fg);background:radial-gradient(900px 500px at 85% -5%,rgba(162,59,255,.22),transparent 60%),radial-gradient(800px 500px at 0% 10%,rgba(25,200,255,.16),transparent 60%),linear-gradient(180deg,var(--bg1),var(--bg2) 45%,var(--bg3)) fixed;font:16px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans","PingFang SC","Microsoft YaHei",sans-serif}
body>main{flex:1}
a{color:var(--cyan);word-break:break-word}a:hover{color:#8fe6ff}
.wrap{max-width:1040px;margin:0 auto;padding:0 1.25rem}
header{position:sticky;top:0;z-index:10;backdrop-filter:blur(12px);background:rgba(7,12,32,.82);border-bottom:1px solid var(--line)}
header .wrap{display:flex;align-items:center;gap:1.2rem;flex-wrap:wrap;padding-top:.65rem;padding-bottom:.65rem}
.brand{display:flex;align-items:center;gap:.6rem;text-decoration:none;color:#fff}
.brand img{height:2.4rem;width:auto;display:block}
.wordmark{font-weight:900;font-style:italic;font-size:1.45rem;letter-spacing:.4px;line-height:1;background:linear-gradient(180deg,#fff,#c9d6f5);-webkit-background-clip:text;background-clip:text;color:transparent}
.wordmark b{background:linear-gradient(180deg,#ffd35a,var(--orange));-webkit-background-clip:text;background-clip:text;color:transparent}
.wordmark small{font-size:.62em;font-weight:700;letter-spacing:2px;text-transform:uppercase;font-style:normal;margin-left:.45rem;color:var(--cyan);-webkit-text-fill-color:var(--cyan)}
nav{display:flex;gap:1.1rem;flex-wrap:wrap;flex:1}nav a{color:var(--fg);text-decoration:none;opacity:.85;padding:.2rem 0;border-bottom:2px solid transparent}nav a:hover,nav a[aria-current]{opacity:1;color:#fff;border-color:var(--cyan)}
details.lang{position:relative}details.lang summary{cursor:pointer;list-style:none;padding:.3rem .8rem;border:1px solid var(--line);border-radius:.6rem;background:var(--card)}
details.lang summary::-webkit-details-marker{display:none}
details.lang div{position:absolute;right:0;margin-top:.4rem;min-width:11rem;padding:.4rem;border:1px solid var(--line);border-radius:.8rem;background:#0b1636;display:grid;gap:.1rem}
details.lang a{padding:.35rem .7rem;border-radius:.5rem;color:var(--fg);text-decoration:none}details.lang a:hover,details.lang a[aria-current]{background:var(--card);color:var(--cyan)}
.hero{padding:4.5rem 0 3rem;text-align:center;animation:rise .7s ease both}
.kicker{display:inline-block;padding:.25rem .9rem;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--cyan);font-size:.8rem;letter-spacing:2px;text-transform:uppercase}
.hero .logo-wide{display:block;max-width:min(560px,86%);height:auto;margin:1.2rem auto 0}
.hero h1{font-size:clamp(2.2rem,7vw,4rem);line-height:1.1;margin:1rem 0;font-weight:900;background:linear-gradient(90deg,var(--cyan),var(--violet) 55%,var(--pink) 80%,var(--orange));-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{max-width:640px;margin:0 auto;color:var(--muted);font-size:1.15rem}
.btns{display:flex;gap:.8rem;flex-wrap:wrap;justify-content:center;margin-top:1.6rem}
.btn{display:inline-block;padding:.7rem 1.4rem;border-radius:.8rem;font-weight:700;text-decoration:none;color:#fff;background:linear-gradient(90deg,var(--blue),var(--violet));box-shadow:0 6px 22px rgba(80,90,255,.35);transition:transform .15s,box-shadow .15s}
.btn:hover{transform:translateY(-2px);color:#fff;box-shadow:0 10px 28px rgba(120,90,255,.5)}
.btn.alt{background:var(--card);border:1px solid var(--line);box-shadow:none}
section{padding:1.8rem 0;animation:rise .7s ease both}section>h2{font-size:1.5rem;margin:0 0 1rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:1.1rem;padding:1.2rem 1.4rem}
.games{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.1rem}
.game{display:flex;flex-direction:column;gap:.7rem;text-decoration:none;color:var(--fg);transition:transform .2s,border-color .2s}
.game:hover{transform:translateY(-4px);border-color:var(--cyan);color:var(--fg)}
.game img{width:100%;border-radius:.8rem;display:block;background:#0b1230}
.game h3{margin:0;font-size:1.25rem}.game p{margin:0;color:var(--muted)}
.tag{align-self:flex-start;font-size:.75rem;letter-spacing:1px;text-transform:uppercase;padding:.15rem .6rem;border-radius:999px;border:1px solid var(--line);color:var(--cyan)}
.featured{display:grid;grid-template-columns:1.1fr 1fr;gap:1.6rem;align-items:center}
.featured img{width:100%;border-radius:1rem}
@media(max-width:760px){.featured{grid-template-columns:1fr}}
.pills{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1rem}.pills span{padding:.4rem .9rem;border-radius:999px;border:1px solid var(--line);background:var(--card);font-size:.95rem}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem}
.grid div{aspect-ratio:1.5;display:flex;align-items:center;justify-content:center;text-align:center;padding:.6rem;border-radius:1rem;border:1px solid var(--line);background:var(--card);font-weight:700}
@media(max-width:560px){.grid{grid-template-columns:repeat(2,1fr)}}
.shots{display:flex;gap:.8rem;overflow-x:auto;padding-bottom:.6rem}.shots img{height:420px;width:auto;border-radius:1rem;border:1px solid var(--line)}
.lm{--line:rgba(245,200,75,.3)}
.lm .page-title{background:linear-gradient(180deg,#fff,var(--gold2) 55%,var(--gold));-webkit-background-clip:text;background-clip:text;color:transparent}
.lm section>h2{color:var(--gold)}.lm .btn:not(.alt){background:linear-gradient(180deg,#ffd96a,#e9a81c);color:#2a1c00;box-shadow:0 6px 22px rgba(245,200,75,.3)}.lm .btn:not(.alt):hover{color:#2a1c00}
.lm .grid div,.lm .pills span,.lm .card{border-color:var(--line)}
.page-title{font-size:clamp(1.9rem,5vw,2.8rem);margin:0 0 .6rem}
main.page{padding:3rem 0}main.page>.lead{color:var(--muted);max-width:680px;font-size:1.1rem}
main.doc{padding:2rem 0 3rem}main.doc h1{font-size:1.9rem;margin-top:0}main.doc h2{font-size:1.15rem;margin-top:2rem;color:#fff}
.meta{color:var(--muted);margin:.2rem 0}
.draft{margin:1rem 0;padding:.7rem 1rem;border-left:4px solid var(--cyan);background:var(--card);border-radius:.4rem}
footer{border-top:1px solid var(--line);padding:2rem 0 2.5rem;color:var(--muted);font-size:.92rem;background:rgba(4,6,15,.6)}
footer .wrap{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:1.4rem}
footer h4{margin:0 0 .5rem;color:#fff;font-size:.85rem;letter-spacing:1.5px;text-transform:uppercase}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:.3rem}footer a{text-decoration:none}
footer .copy{grid-column:1/-1;border-top:1px solid var(--line);padding-top:1rem}
@media(max-width:640px){footer .wrap{grid-template-columns:1fr}}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
"""

# Each key is a page type; value is the path below /<lang>/. Existing privacy/terms URLs are unchanged.
PAGES = {"home": "", "games": "games/", "about": "about/", "support": "support/", "privacy": "privacy/", "terms": "terms/"}
for g in GAMES:
    PAGES["game:" + g["slug"]] = f"games/{g['slug']}/"


def depth_of(page):
    return PAGES[page].count("/") + 1


def href(tag, page, from_depth):
    return "../" * from_depth + f"{tag}/{PAGES[page]}index.html"


def S(tag, key):
    return STUDIO[tag][key]


def tr(tag, v):
    # "@ui.key" pulls the text from ui.json, otherwise a per-language dict or plain string
    if isinstance(v, dict):
        return v.get(tag) or v["en"]
    if isinstance(v, str) and v.startswith("@ui."):
        return UI[tag][v[4:]]
    return v


def play_url(g):
    return SITE.get(g.get("playStoreKey", ""), "").strip()


def brand_html(tag, depth):
    root = "../" * depth
    img = f'<img src="{root}{MARK}" alt="">' if MARK else ""
    return (f'<a class="brand" href="{href(tag, "home", depth)}">{img}'
            f'<span class="wordmark">AKYne<b>X</b><small>Studio</small></span></a>')


def layout(tag, page, body, title, cls=""):
    u = UI[tag]
    depth = depth_of(page)
    root = "../" * depth
    cur = "games" if page.startswith("game:") else page
    nav = "".join(
        f'<a href="{href(tag, p, depth)}"{" aria-current=\"page\"" if p == cur else ""}>{label}</a>'
        for p, label in (("home", u["home"]), ("games", S(tag, "nav_games")), ("about", S(tag, "nav_about")),
                         ("support", S(tag, "nav_support")), ("privacy", u["privacy"]))
    )
    langs = "".join(
        f'<a href="{href(t, page, depth)}" hreflang="{t}" lang="{t}"{" aria-current=\"true\"" if t == tag else ""}>{UI[t]["name"]}</a>' for t in LANGS
    )
    alts = "".join(f'<link rel="alternate" hreflang="{t}" href="{href(t, page, depth)}">' for t in LANGS)
    games_li = "".join(f'<li><a href="{href(tag, "game:" + g["slug"], depth)}">{html.escape(g["name"])}</a></li>' for g in GAMES)
    legal_li = "".join(
        f'<li><a href="{href(tag, g["privacy"], depth)}">{html.escape(g["name"])} — {u["privacy"]}</a></li>'
        f'<li><a href="{href(tag, g["terms"], depth)}">{html.escape(g["name"])} — {u["terms"]}</a></li>' for g in GAMES
    )
    contact = f'<li><a href="mailto:{EMAIL}">{EMAIL}</a></li>' if EMAIL else ""
    return f"""<!doctype html>
<html lang="{tag}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="theme-color" content="#070c20">
<title>{html.escape(title)} — {BRAND}</title>{alts}
<link rel="stylesheet" href="{root}style.css"></head>
<body class="{cls}"><header><div class="wrap">{brand_html(tag, depth)}<nav aria-label="Main">{nav}</nav>
<details class="lang"><summary aria-label="{u['lang']}">{u['name']} ▾</summary><div>{langs}</div></details></div></header>
{body}
<footer><div class="wrap"><div>{brand_html(tag, depth)}<p>{S(tag, 'studio_tag')}</p></div>
<div><h4>{S(tag, 'nav_games')}</h4><ul>{games_li}</ul></div>
<div><h4>{u['legal']}</h4><ul>{legal_li}{contact}</ul></div>
<div class="copy">© {BRAND}. {u['rights']}</div></div></footer>
</body></html>
"""


def draft_banner(u):
    if EMAIL and "DRAFT" not in PRIV.get("version", "").upper():
        return ""
    return f'<p class="draft">{html.escape(u["draft"])}</p>'


def game_card(tag, g, depth):
    root = "../" * depth
    return (f'<a class="card game" href="{href(tag, "game:" + g["slug"], depth)}">'
            f'<img src="{root}{g["icon"]}" alt="{html.escape(g["name"])}" loading="lazy">'
            f'<span class="tag">{S(tag, "status")}</span><h3>{html.escape(g["name"])}</h3>'
            f'<p>{html.escape(tr(tag, g["tagline"]))}</p></a>')


def play_btn(tag, g):
    url = play_url(g)
    return f'<a class="btn" href="{html.escape(url)}" rel="noopener">{S(tag, "play")}</a>' if url else ""


def home(tag):
    u = UI[tag]
    root = "../"
    f = next((g for g in GAMES if g.get("featured")), GAMES[0])
    wide = f'<img class="logo-wide" src="{root}{WIDE}" alt="{BRAND}">' if WIDE else ""
    return f"""<main><div class="wrap"><div class="hero"><span class="kicker">{S(tag, 'studio_tag')}</span>{wide}
<h1>{html.escape(S(tag, 'hero_title'))}</h1><p>{html.escape(S(tag, 'hero_sub'))}</p>
<div class="btns"><a class="btn" href="{href(tag, 'games', 1)}">{S(tag, 'cta_games')}</a><a class="btn alt" href="{href(tag, 'about', 1)}">{S(tag, 'nav_about')}</a></div></div>
<section><h2>{S(tag, 'featured_t')}</h2><div class="card featured"><img src="{root}{f['icon']}" alt="{html.escape(f['name'])}">
<div><span class="tag">{S(tag, 'status')}</span><h3 style="font-size:1.8rem;margin:.5rem 0">{html.escape(f['name'])}</h3>
<p>{html.escape(tr(tag, f['tagline']))}</p><div class="btns" style="justify-content:flex-start"><a class="btn" href="{href(tag, 'game:' + f['slug'], 1)}">{S(tag, 'view')}</a>{play_btn(tag, f)}</div></div></div></section></div></main>"""


def games(tag):
    cards = "".join(game_card(tag, g, 2) for g in GAMES)
    return f"""<main class="page"><div class="wrap"><h1 class="page-title">{S(tag, 'games_t')}</h1><p class="lead">{html.escape(S(tag, 'games_lead'))}</p>
<section><div class="games">{cards}</div></section></div></main>"""


def game_page(tag, g):
    u = UI[tag]
    root = "../" * 3
    shots_dir = ROOT / "assets" / g["slug"] / "screens"
    shots = sorted(p.name for p in shots_dir.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")) if shots_dir.exists() else []
    shots_html = ""
    if shots:
        imgs = "".join(f'<img src="{root}assets/{g["slug"]}/screens/{n}" alt="{html.escape(g["name"])}" loading="lazy">' for n in shots)
        shots_html = f'<section><h2>{S(tag, "shots_t")}</h2><div class="shots">{imgs}</div></section>'
    pills = "".join(f"<span>{html.escape(x)}</span>" for x in u["feats"])
    cats = "".join(f"<div>{html.escape(c)}</div>" for c in u["cats"])
    return f"""<main><div class="wrap"><div class="hero"><img src="{root}{g['icon']}" alt="{html.escape(g['name'])}" style="max-width:min(520px,90%);border-radius:1.2rem">
<h1 class="page-title">{html.escape(u['title'])}</h1><p>{html.escape(u['sub'])}</p><div class="btns">{play_btn(tag, g)}
<a class="btn alt" href="{href(tag, g['privacy'], 3)}">{u['privacy']}</a></div></div>
<section><h2>{u['about_t']}</h2><div class="card"><p>{html.escape(u['about'])}</p></div></section>
<section><h2>{u['feat_t']}</h2><div class="pills">{pills}</div></section>
<section><h2>{u['cats_t']}</h2><div class="grid">{cats}</div></section>{shots_html}</div></main>"""


def about(tag):
    u = UI[tag]
    return f"""<main class="page"><div class="wrap"><h1 class="page-title">{html.escape(S(tag, 'about_page_t'))}</h1>
<section><div class="card"><p>{html.escape(S(tag, 'about_p1'))}</p><p>{html.escape(S(tag, 'about_p2'))}</p></div></section></div></main>"""


def support(tag):
    u = UI[tag]
    mail = f'<p><strong>{u["contact"]}:</strong> <a href="mailto:{EMAIL}">{EMAIL}</a></p>' if EMAIL else ""
    docs = "".join(
        f'<li>{html.escape(g["name"])}: <a href="{href(tag, g["privacy"], 2)}">{u["privacy"]}</a> · <a href="{href(tag, g["terms"], 2)}">{u["terms"]}</a></li>'
        for g in GAMES)
    return f"""<main class="page"><div class="wrap"><h1 class="page-title">{S(tag, 'support_t')}</h1><p class="lead">{html.escape(S(tag, 'support_p'))}</p>
<section><div class="card">{mail}</div></section><section><h2>{S(tag, 'docs_t')}</h2><div class="card"><ul>{docs}</ul></div></section></div></main>"""


def doc(tag, kind):
    u = UI[tag]
    text = (C / f"{kind}_{tag}.md").read_text(encoding="utf-8")
    return f'<main class="wrap doc">{draft_banner(u)}{md(text)}</main>'


def build():
    f = {"style.css": CSS, ".nojekyll": ""}
    for t in LANGS:
        u = UI[t]
        f[f"{t}/index.html"] = layout(t, "home", home(t), u["home"])
        f[f"{t}/games/index.html"] = layout(t, "games", games(t), S(t, "games_t"))
        f[f"{t}/about/index.html"] = layout(t, "about", about(t), S(t, "nav_about"))
        f[f"{t}/support/index.html"] = layout(t, "support", support(t), S(t, "support_t"))
        f[f"{t}/privacy/index.html"] = layout(t, "privacy", doc(t, "privacy"), "Logic Mix — " + u["privacy"])
        f[f"{t}/terms/index.html"] = layout(t, "terms", doc(t, "terms"), "Logic Mix — " + u["terms"])
        for g in GAMES:
            f[f"{t}/games/{g['slug']}/index.html"] = layout(t, "game:" + g["slug"], game_page(t, g), g["name"], "lm" if g["slug"] == "logic-mix" else "")
    links = " ".join(f'<a href="{t}/index.html">{UI[t]["name"]}</a>' for t in LANGS)
    tags = json.dumps({t.split("-")[0].lower(): t for t in LANGS})
    f["index.html"] = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{BRAND}</title><meta http-equiv="refresh" content="3;url=en/index.html"><link rel="stylesheet" href="style.css"></head>
<body><main><div class="wrap"><div class="hero"><h1>{BRAND}</h1><p>{links}</p></div></div></main>
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
