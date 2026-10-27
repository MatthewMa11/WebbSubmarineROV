# Website development

The site is static HTML/CSS on GitHub Pages. `index.html` is the home page; journal Markdown in `docs/journals/` is rendered by `scripts/build-journals.mjs`. Shared styles are in `site-assets/site.css`, with article styles in `site-assets/journals.css`.

`site-assets/site.js` adds mobile navigation, one-time scroll reveals, active section navigation and journal reading progress. Content and navigation remain available without JavaScript. Motion follows the visitor’s reduced-motion preference, including changes made while a page is open.

## Check a change

1. Run `npm install` (or `pnpm install --frozen-lockfile` to use the included lockfile).
2. Run `npm run build:site` after editing the journal source or generator.
3. Run `npx playwright install chromium` once to install the test browser.
4. Run `npm test`.

The browser checks cover keyboard navigation, scroll animation, reduced motion, no-JavaScript navigation, all three pages at desktop/tablet/phone widths, journal anchors, image loading and print styles. The tests run from the repository root. Optionally set `BROWSER_EXECUTABLE` to use an existing Chrome executable, or `SCREENSHOT_DIR` to an existing directory to save desktop/phone screenshots.

Commit the generated journal HTML alongside source changes. GitHub Pages publishes the root of `main`; keep `.nojekyll` in place.
