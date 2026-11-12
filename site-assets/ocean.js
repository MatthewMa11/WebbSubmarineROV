/* Decorative ocean scene. No network requests, frameworks, or scroll interception. */
(() => {
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const toggle = document.querySelector('.motion-toggle');
  const scene = document.querySelector('.ocean-scene');
  const hero = document.querySelector('.ocean-hero');
  const canvas = document.querySelector('.ocean-particles');
  const context = canvas?.getContext('2d', { alpha: true });
  let savedPause = false;
  try { savedPause = localStorage.getItem('rov-ocean-motion') === 'paused'; } catch {}
  let paused = savedPause || reduced.matches;
  let heroVisible = true;
  let frame = 0;
  let lastFrame = 0;
  let elapsed = 0;
  let width = 0;
  let height = 0;
  let particles = [];

  function paint() {
    if (!context || !width || !height) return;
    context.clearRect(0, 0, width, height);
    for (const p of particles) {
      const x = p.x * width + Math.sin(elapsed * .13 + p.phase) * 18;
      const y = ((p.y * height - elapsed * p.speed) % height + height) % height;
      context.globalAlpha = p.alpha * (.75 + Math.sin(elapsed * .4 + p.phase) * .25);
      context.fillStyle = p.tint;
      context.beginPath(); context.arc(x, y, p.radius, 0, Math.PI * 2); context.fill();
    }
    context.globalAlpha = 1;
  }
  function canRun() { return context && !paused && heroVisible && document.visibilityState !== 'hidden'; }
  function tick(now) {
    frame = 0;
    if (!canRun()) return;
    if (!lastFrame) lastFrame = now;
    const delta = now - lastFrame;
    if (delta >= 1000 / 30) {
      elapsed += Math.min(delta, 70) / 1000;
      lastFrame = now;
      paint();
    }
    frame = requestAnimationFrame(tick);
  }
  function syncFrames() {
    if (canRun()) {
      if (!frame) { lastFrame = 0; frame = requestAnimationFrame(tick); }
    } else {
      if (frame) cancelAnimationFrame(frame);
      frame = 0;
      lastFrame = 0;
    }
  }
  function resize() {
    if (!context || !scene) return;
    const bounds = scene.getBoundingClientRect();
    width = bounds.width; height = bounds.height;
    const ratio = Math.min(devicePixelRatio || 1, 1.5);
    canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    const count = width < 760 ? 26 : 55;
    particles = Array.from({ length: count }, () => ({
      x: Math.random(), y: Math.random(), radius: .4 + Math.random() * 1.2,
      speed: 2 + Math.random() * 5, alpha: .12 + Math.random() * .35,
      phase: Math.random() * Math.PI * 2, tint: Math.random() > .9 ? '#d99de7' : '#b7fff0'
    }));
    paint();
  }
  function applyMotion() {
    paused = savedPause || reduced.matches;
    root.classList.toggle('motion-on', !paused);
    root.classList.toggle('motion-paused', paused);
    if (toggle) {
      toggle.hidden = false;
      toggle.disabled = reduced.matches;
      toggle.setAttribute('aria-pressed', String(paused));
      toggle.querySelector('.motion-label').textContent = reduced.matches ? 'Reduced motion' : paused ? 'Play scene' : 'Pause scene';
      toggle.querySelector('.motion-icon').textContent = paused ? '▷' : 'Ⅱ';
    }
    if (paused && scene) {
      scene.style.setProperty('--look-x', '0px'); scene.style.setProperty('--look-y', '0px');
      scene.style.setProperty('--dive', '0');
    }
    syncFrames();
    window.dispatchEvent(new CustomEvent('rov-motion-change'));
  }
  toggle?.addEventListener('click', () => {
    savedPause = !paused;
    try { localStorage.setItem('rov-ocean-motion', savedPause ? 'paused' : 'playing'); } catch {}
    applyMotion();
  });
  reduced.addEventListener('change', applyMotion);
  document.addEventListener('visibilitychange', () => {
    root.classList.toggle('page-hidden', document.visibilityState === 'hidden');
    syncFrames();
  });
  if (hero && 'IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      heroVisible = entries[0].isIntersecting;
      root.classList.toggle('scene-offscreen', !heroVisible);
      syncFrames();
    }).observe(hero);
  }
  if (scene && 'ResizeObserver' in window) new ResizeObserver(resize).observe(scene);
  else if (scene) window.addEventListener('resize', resize);
  let scrollFrame = 0;
  function updateDive() {
    scrollFrame = 0;
    if (!hero || !scene || paused) return;
    const bounds = hero.getBoundingClientRect();
    scene.style.setProperty('--dive', String(Math.max(0, Math.min(1, -bounds.top / bounds.height))));
  }
  if (hero) window.addEventListener('scroll', () => {
    if (!scrollFrame && !paused) scrollFrame = requestAnimationFrame(updateDive);
  }, { passive: true });
  let pointerFrame = 0;
  let lookX = 0, lookY = 0;
  if (hero && scene && matchMedia('(pointer: fine)').matches) {
    const updateLook = () => {
      pointerFrame = 0;
      if (paused) return;
      scene.style.setProperty('--look-x', lookX + 'px'); scene.style.setProperty('--look-y', lookY + 'px');
    };
    hero.addEventListener('pointermove', event => {
      if (paused) return;
      const bounds = hero.getBoundingClientRect();
      lookX = ((event.clientX - bounds.left) / bounds.width - .5) * 18;
      lookY = ((event.clientY - bounds.top) / bounds.height - .5) * 12;
      if (!pointerFrame) pointerFrame = requestAnimationFrame(updateLook);
    }, { passive: true });
    hero.addEventListener('pointerleave', () => { lookX = 0; lookY = 0; if (!pointerFrame) pointerFrame = requestAnimationFrame(updateLook); });
  }
  window.addEventListener('beforeprint', () => { if (frame) cancelAnimationFrame(frame); frame = 0; });
  window.addEventListener('afterprint', syncFrames);
  resize(); applyMotion();
})();
