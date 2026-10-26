/** Static SVG rendering for the three deliberately limited journal flowcharts. */
const THEMES = [
  ['R4 cover joint stack', 'Schematic · not to scale · screw head to tip'],
  ['R6 torque and axial retention', 'Intended functions · not measured load capacity'],
  ['Current saved thruster assembly', 'Arrows mean inclusion · not force or torque paths'],
];

const xml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;',
})[character]);

function parseFlowchart(code) {
  if (typeof code !== 'string') throw new TypeError('Diagram source must be a string');
  const lines = code.trim().split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const header = /^flowchart (TB|LR)$/.exec(lines.shift() ?? '');
  if (!header) throw new Error('Only flowchart TB or LR is supported');
  const endpoint = '([A-Za-z][A-Za-z0-9_]*)(?:\\["([^"\\r\\n]+)"\\])?';
  const edgePattern = new RegExp(`^${endpoint}\\s*-->\\s*${endpoint}$`);
  const nodes = new Map();
  const edges = [];
  const knownEdges = new Set();
  function declare(id, label) {
    if (label === undefined) return;
    if (!label.trim() || label.length > 100 || /[\u0000-\u001f\u007f]/.test(label)) {
      throw new Error(`Unsupported label for node ${id}`);
    }
    if (nodes.has(id) && nodes.get(id) !== label) throw new Error(`Conflicting node label: ${id}`);
    nodes.set(id, label);
  }
  for (const line of lines) {
    const match = edgePattern.exec(line);
    if (!match) throw new Error(`Unsupported flowchart statement: ${line}`);
    const [, from, fromLabel, to, toLabel] = match;
    declare(from, fromLabel);
    declare(to, toLabel);
    const key = `${from}->${to}`;
    if (from === to || knownEdges.has(key)) throw new Error(`Unsupported repeated/self edge: ${key}`);
    knownEdges.add(key);
    edges.push({ from, to });
  }
  if (!edges.length) throw new Error('A diagram must contain edges');
  for (const { from, to } of edges) {
    if (!nodes.has(from) || !nodes.has(to)) throw new Error(`Undeclared endpoint: ${from} -> ${to}`);
  }
  return { direction: header[1], nodes, edges };
}

function chains(graph, expectedLengths) {
  const incoming = new Map([...graph.nodes.keys()].map((id) => [id, 0]));
  const next = new Map();
  for (const { from, to } of graph.edges) {
    if (next.has(from) || incoming.get(to) > 0) throw new Error('Expected independent unbranched chains');
    next.set(from, to);
    incoming.set(to, incoming.get(to) + 1);
  }
  const roots = [...incoming].filter(([, count]) => count === 0).map(([id]) => id);
  const visited = new Set();
  const result = roots.map((root) => {
    const chain = [];
    for (let id = root; id !== undefined; id = next.get(id)) {
      if (visited.has(id)) throw new Error('Cycles or shared nodes are unsupported');
      visited.add(id);
      chain.push(id);
    }
    return chain;
  });
  if (visited.size !== graph.nodes.size || result.length !== expectedLengths.length ||
      result.some((chain, index) => chain.length !== expectedLengths[index])) {
    throw new Error('Diagram topology does not match the expected journal diagram');
  }
  return result;
}

function wrap(label, maxCharacters) {
  const lines = [];
  let line = '';
  for (const word of label.split(/\s+/)) {
    if (word.length > maxCharacters) throw new Error('Label contains a word too long for the diagram');
    if (line && `${line} ${word}`.length > maxCharacters) {
      lines.push(line);
      line = word;
    } else line = line ? `${line} ${word}` : word;
  }
  if (line) lines.push(line);
  return lines;
}

/**
 * Convert one journal Mermaid fence into a self-contained accessible SVG.
 * @param {string} code Fence contents (without the ```mermaid delimiters).
 * @param {number} index Zero-based journal diagram index: 0, 1 or 2.
 * @returns {{svg: string, alt: string}}
 * @throws On unsupported Mermaid syntax, undefined nodes or unexpected topology.
 */
export function renderJournalDiagram(code, index) {
  if (!Number.isInteger(index) || index < 0 || index >= THEMES.length) {
    throw new RangeError('Journal diagram index must be 0, 1 or 2');
  }
  const graph = parseFlowchart(code);
  const [title, subtitle] = THEMES[index];
  const boxes = new Map();
  let width;
  let height;
  const place = (id, x, y, w, h, dark = false) => boxes.set(id, { x, y, w, h, dark });

  if (index === 0) {
    if (graph.direction !== 'TB') throw new Error('The R4 stack must run top to bottom');
    const [stack] = chains(graph, [7]);
    width = 620;
    height = 794;
    stack.forEach((id, row) => place(id, 90, 114 + row * 92, 440, 60));
  } else if (index === 1) {
    if (graph.direction !== 'LR') throw new Error('The R6 paths must run left to right');
    const rows = chains(graph, [3, 3]);
    width = 940;
    height = 376;
    rows.forEach((row, rowIndex) => row.forEach((id, column) =>
      place(id, 32 + column * 308, 126 + rowIndex * 128, 260, 92)));
  } else {
    if (graph.direction !== 'LR' || graph.nodes.size !== 5 || graph.edges.length !== 4) {
      throw new Error('The compatibility map requires four inputs and one destination');
    }
    const destination = graph.edges[0].to;
    const inputs = graph.edges.map(({ from }) => from);
    if (new Set(inputs).size !== 4 || inputs.includes(destination) ||
        graph.edges.some(({ to }) => to !== destination)) {
      throw new Error('Every compatibility input must point to the same assembly');
    }
    width = 940;
    height = 574;
    inputs.forEach((id, row) => place(id, 32, 118 + row * 110, 350, 82));
    place(destination, 588, 274, 320, 100, true);
  }

  const prefix = `journal-diagram-${index + 1}`;
  const alt = `${title}. ${subtitle}. ${graph.edges.map(({ from, to }) =>
    `${graph.nodes.get(from)} → ${graph.nodes.get(to)}`).join('; ')}.`;
  const paths = graph.edges.map(({ from, to }, edgeIndex) => {
    const a = boxes.get(from);
    const b = boxes.get(to);
    let d;
    if (index === 0) d = `M ${a.x + a.w / 2} ${a.y + a.h} V ${b.y - 5}`;
    else if (index === 1) d = `M ${a.x + a.w} ${a.y + a.h / 2} H ${b.x - 5}`;
    else {
      const startY = a.y + a.h / 2;
      const endY = b.y + 20 + edgeIndex * 20;
      d = `M ${a.x + a.w} ${startY} C 476 ${startY}, 490 ${endY}, ${b.x - 5} ${endY}`;
    }
    return `<path data-from="${xml(from)}" data-to="${xml(to)}" d="${d}" fill="none" stroke="#178396" stroke-width="2.5" marker-end="url(#${prefix}-arrow)"/>`;
  }).join('\n');

  const nodes = [...boxes].map(([id, box]) => {
    const label = graph.nodes.get(id);
    const lines = wrap(label, Math.floor((box.w - 44) / 10));
    if (lines.length * 25 > box.h - 14) throw new Error(`Label does not fit node ${id}`);
    const startY = box.y + box.h / 2 - (lines.length - 1) * 12.5 + 6;
    const spans = lines.map((line, row) => `<tspan x="${box.x + box.w / 2}" y="${startY + row * 25}">${xml(line)}</tspan>`).join('');
    return `<g data-node="${xml(id)}"><title>${xml(label)}</title><rect x="${box.x}" y="${box.y}" width="${box.w}" height="${box.h}" rx="12" fill="${box.dark ? '#153247' : '#fffdf7'}" stroke="#178396" stroke-width="1.5"/><text text-anchor="middle" font-size="18" font-weight="600" fill="${box.dark ? '#ffffff' : '#153247'}">${spans}</text></g>`;
  }).join('\n');

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="${prefix}-title ${prefix}-description" font-family="Arial, Helvetica, sans-serif">
<title id="${prefix}-title">${xml(title)}</title>
<desc id="${prefix}-description">${xml(alt)}</desc>
<defs><marker id="${prefix}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 Z" fill="#178396"/></marker></defs>
<rect width="${width}" height="${height}" rx="18" fill="#f5f1e7"/>
<rect x="32" y="28" width="5" height="51" rx="2.5" fill="#178396"/>
<text x="50" y="48" fill="#153247" font-size="24" font-weight="700">${xml(title)}</text>
<text x="50" y="76" fill="#40586a" font-size="16">${xml(subtitle)}</text>
${paths}
${nodes}
</svg>`;
  return { svg, alt };
}
