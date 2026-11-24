# Logic Mix site

Official AKYneX Studio site (8 languages): studio home, game catalog, game pages, About, Support, Privacy Policy, Terms.

- Edit `content/` (ui.json, privacy_*.md, terms_*.md, *.properties), then run `python3 build.py`.
- Set `contactEmail` in `content/site.properties` / `privacy_config.properties`.
- Publish: GitHub Settings > Pages > Deploy from branch `main` / root.

## Adding a game
1. Add an entry to `content/games.json` (slug, name, tagline, icon, privacy/terms page keys). A game page and catalog card are generated automatically.
2. Put the icon at `assets/<slug>/` and screenshots (png/jpg/webp) in `assets/<slug>/screens/`; they appear on the game page automatically.
3. Set the Google Play URL in `content/site.properties` (`playStoreUrl=`); the button is hidden while it is empty.
4. Run `python3 build.py`.

## Studio logo
Put `assets/brand/logo-mark.png` (hexagon mark, header/footer) and/or `assets/brand/logo-wide.png` (home hero), then run `python3 build.py`. Without them the header shows the text wordmark.

Public URLs `/<lang>/privacy/` and `/<lang>/terms/` are used by Google Play, AdMob and the app: do not move them.
