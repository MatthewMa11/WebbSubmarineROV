import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { renderJournalDiagram } from './journal-diagrams.mjs';

const require = createRequire(import.meta.url);
const { marked, Renderer } = await import(pathToFileURL(require.resolve('marked')).href);
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repo = 'https://github.com/MatthewMa11/WebbSubmarineROV';
const escape = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const journals = [
  { slug: 'motor-and-fan-cad-development', label: 'Motor & fan CAD journal', category: 'ENGINEERING JOURNAL', description: 'The motor and fan development story, from the PLA baseline through R14. Every revision includes supporting images and explanations.' },
  { slug: 'club-mission-and-museum-vision', label: 'Club & museum vision journal', category: 'CLUB JOURNAL', description: 'What the club does, what we are learning, and our vision for helping the museum share science and exploration.' }
];
fs.mkdirSync(path.join(root, 'journals'), { recursive: true });
fs.mkdirSync(path.join(root, 'site-assets/diagrams'), { recursive: true });

function rewriteLink(href, image = false) {
  if (/^(https?:|#)/.test(href)) return href;
  if (!href.startsWith('../../')) throw new Error(`Unsupported journal link: ${href}`);
  const target = href.slice(6);
  if (image || target.endsWith('.zip')) return '../' + target;
  return `${repo}/blob/main/${target}`;
}

// Reserve the original image aspect ratio before lazy loading to keep section
// navigation and nearby links stable. The journal source uses PNG and JPEG.
function imageDimensions(href) {
  const bytes = fs.readFileSync(path.join(root, href.slice(6)));
  if (bytes.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10]))) {
    return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
  }
  if (bytes[0] === 0xff && bytes[1] === 0xd8) {
    let offset = 2;
    const frames = new Set([0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf]);
    while (offset + 8 < bytes.length) {
      if (bytes[offset++] !== 0xff) break;
      while (bytes[offset] === 0xff) offset++;
      const marker = bytes[offset++];
      if (marker === 0xda || marker === 0xd9) break;
      const length = bytes.readUInt16BE(offset);
      if (length < 2 || offset + length > bytes.length) break;
      if (frames.has(marker)) return { width: bytes.readUInt16BE(offset + 5), height: bytes.readUInt16BE(offset + 3) };
      offset += length;
    }
  }
  throw new Error(`Unsupported or unreadable image dimensions: ${href}`);
}

for (const journal of journals) {
  const source = fs.readFileSync(path.join(root, 'docs/journals', journal.slug + '.md'), 'utf8');
  const toc = [];
  const slugs = new Set();
  let title = '';
  let diagramCount = 0;
  const renderer = new Renderer();
  renderer.heading = function({ tokens, depth }) {
    const label = this.parser.parseInline(tokens);
    const plain = label.replace(/<[^>]+>/g, '');
    if (depth === 1) { title = plain; return ''; }
    const base = plain.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    let id = base, n = 2;
    while (slugs.has(id)) id = `${base}-${n++}`;
    slugs.add(id);
    if (depth === 2) toc.push({ id, label: plain });
    return `<h${depth} id="${id}">${label}<a class="section-anchor" href="#${id}" aria-label="Link to ${escape(plain)}">#</a></h${depth}>\n`;
  };
  renderer.link = function({ href, title, tokens }) {
    return `<a href="${escape(rewriteLink(href))}"${title ? ` title="${escape(title)}"` : ''}>${this.parser.parseInline(tokens)}</a>`;
  };
  renderer.image = function({ href, text }) {
    const src = rewriteLink(href, true);
    const { width, height } = imageDimensions(href);
    return `<a class="journal-figure" href="${escape(src)}" aria-label="Open full-size image: ${escape(text)}"><img src="${escape(src)}" alt="${escape(text)}" width="${width}" height="${height}" loading="lazy" decoding="async"></a>`;
  };
  renderer.html = ({ text }) => escape(text);
  renderer.code = function({ text, lang }) {
    if (lang !== 'mermaid') return `<pre><code>${escape(text)}</code></pre>\n`;
    const { svg, alt } = renderJournalDiagram(text, diagramCount);
    const dimensions = /viewBox="0 0 (\d+) (\d+)"/.exec(svg);
    if (!dimensions) throw new Error('Diagram must declare its dimensions');
    const filename = `${journal.slug}-${++diagramCount}.svg`;
    fs.writeFileSync(path.join(root, 'site-assets/diagrams', filename), svg);
    return `<figure class="journal-diagram${diagramCount > 1 ? ' diagram-wide' : ''}"><a href="../site-assets/diagrams/${filename}" aria-label="Open full-size diagram: ${escape(alt)}"><img src="../site-assets/diagrams/${filename}" alt="${escape(alt)}" width="${dimensions[1]}" height="${dimensions[2]}" loading="lazy"></a><figcaption>Explanatory schematic · Open diagram to view full size${diagramCount > 1 ? ' · Scroll sideways on smaller screens' : ''}</figcaption></figure>\n`;
  };
  renderer.table = function(token) {
    return '<div class="table-scroll" tabindex="0" role="region" aria-label="Revision map table">' + Renderer.prototype.table.call(this, token) + '</div>\n';
  };
  const content = marked.parse(source, { renderer, gfm: true });
  if (!title) throw new Error(`Missing title: ${journal.slug}`);
  const other = journals.find(j => j !== journal);
  const browse = journals.map(j => `<a href="${j.slug}.html"${j === journal ? ' aria-current="page"' : ''}>${escape(j.label)}</a>`).join('\n');
  const contents = toc.length ? `<details class="contents" open><summary>On this page</summary><nav aria-label="Journal contents">${toc.map(h => `<a href="#${h.id}">${escape(h.label)}</a>`).join('\n')}</nav></details>` : '';
  const readingMinutes = Math.max(1, Math.ceil(source.split(/\s+/).length / 220));
  const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="${escape(journal.description)}"><meta name="theme-color" content="#102c35">
  <title>${escape(journal.label)} | Webb Submarine ROV</title>
  <link rel="stylesheet" href="../site-assets/site.css"><link rel="stylesheet" href="../site-assets/journals.css">
  <script src="../site-assets/site.js" defer></script>
</head>
<body class="reader-page" id="top">
  <div class="reading-progress" aria-hidden="true"><span></span></div>
  <a class="skip-link" href="#journal-content">Skip to journal</a>
  <header class="site-header"><div class="header-inner shell">
    <a class="wordmark" href="../index.html" aria-label="Webb Submarine ROV home"><span>WEBB <span class="wordmark-sub">SUBMARINE ROV</span></span></a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="main-nav" hidden>Menu <span aria-hidden="true">+</span></button>
    <nav id="main-nav" aria-label="Main navigation"><a href="../index.html">Club home</a><a href="../index.html#journal">All journals</a><a href="../index.html#downloads">Design files ↗</a></nav>
  </div></header>
  <main>
    <div class="reader-hero shell">
      <a class="back-home" href="../index.html">← Back to club home</a>
      <p class="eyebrow">${journal.category} <span class="meta-divider" aria-hidden="true">/</span> ${readingMinutes} MIN READ</p>
      <h1>${escape(title)}</h1><p class="reader-intro">${escape(journal.description)}</p>
    </div>
    <div class="reader-layout shell">
      <aside class="reader-sidebar"><div class="journal-switch"><p class="eyebrow">BROWSE JOURNALS</p><nav aria-label="Choose a journal">${browse}</nav></div>${contents}</aside>
      <article class="journal-content" id="journal-content" aria-label="${escape(journal.label)}">
        ${content}
        <div class="reader-next"><p class="eyebrow">KEEP READING</p><a href="${other.slug}.html">${escape(other.label)} <span aria-hidden="true">→</span></a><a class="return-home" href="../index.html">← Return to club home</a></div>
      </article>
    </div>
  </main>
  <footer class="site-footer"><div class="shell footer-top"><p>WEBB<br><span>SUBMARINE ROV</span></p><a class="text-link" href="../index.html">Club home <span aria-hidden="true">↗</span></a></div><div class="shell footer-bottom"><a href="${repo}/blob/main/docs/journals/${journal.slug}.md">View journal source on GitHub</a><span>PROJECT RECORD · OCTOBER 26, 2026</span><a href="#top">Back to top ↑</a></div></footer>
</body></html>
`;
  fs.writeFileSync(path.join(root, 'journals', journal.slug + '.html'), html);
  console.log(`${journal.slug}: ${toc.length} sections, ${(content.match(/class="journal-figure"/g) || []).length} source images, ${diagramCount} diagrams`);
}
