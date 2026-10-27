/* Progressive enhancement: the full site remains usable without this file. */
(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const narrow = window.matchMedia('(max-width: 760px)');
  const header = document.querySelector('.site-header');
  const menu = document.querySelector('.menu-toggle');
  const navigation = document.getElementById('main-nav');

  if (menu && navigation) {
    const setMenu = (open, returnFocus = false) => {
      menu.setAttribute('aria-expanded', String(open));
      navigation.classList.toggle('is-open', open);
      if (returnFocus) menu.focus({ preventScroll: true });
    };
    menu.hidden = false;
    header.classList.add('has-menu');
    menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') setMenu(false, true);
    });
    document.addEventListener('click', event => {
      if (!header.contains(event.target) && menu.getAttribute('aria-expanded') === 'true') {
        setMenu(false, navigation.contains(document.activeElement));
      }
    });
    navigation.addEventListener('click', event => {
      const link = event.target.closest('a');
      if (!link || !narrow.matches) return;
      setMenu(false);
      if (link.getAttribute('href').startsWith('#')) {
        const target = document.getElementById(link.hash.slice(1));
        if (target) {
          target.setAttribute('tabindex', '-1');
          target.focus({ preventScroll: true });
        }
      }
    });
    narrow.addEventListener('change', () => {
      const hadNavFocus = navigation.contains(document.activeElement);
      const hadMenuFocus = document.activeElement === menu;
      setMenu(false, narrow.matches && hadNavFocus);
      if (!narrow.matches && hadMenuFocus) navigation.querySelector('a')?.focus({ preventScroll: true });
    });
  }

  // Animate on entry, without hiding content in CSS or relying on JS to reveal it.
  const reveals = document.querySelectorAll('.section-heading, .project-intro, .design-detail, .journal-entry, .mission-title, .mission-item, .download-row, .reader-hero, .journal-content h2, .journal-figure, .journal-diagram');
  if ('IntersectionObserver' in window && Element.prototype.animate) {
    const animations = new Set();
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        observer.unobserve(entry.target);
        if (reduced.matches) continue;
        const animation = entry.target.animate([
          { opacity: 0.25, transform: 'translateY(18px)' },
          { opacity: 1, transform: 'translateY(0)' }
        ], { duration: 550, easing: 'cubic-bezier(.2,.7,.2,1)' });
        animations.add(animation);
        animation.finished.then(() => animations.delete(animation), () => animations.delete(animation));
      }
    }, { threshold: 0.08 });
    reveals.forEach(element => observer.observe(element));
    const stopMotion = () => animations.forEach(animation => animation.cancel());
    reduced.addEventListener('change', () => { if (reduced.matches) stopMotion(); });
    window.addEventListener('beforeprint', stopMotion);
  }

  const article = document.querySelector('.journal-content');
  const progress = document.querySelector('.reading-progress span');
  const links = [...document.querySelectorAll(article ? '.contents a[href^="#"]' : '#main-nav a[href^="#"]')];
  const sections = links.map(link => ({ link, target: document.getElementById(link.hash.slice(1)) })).filter(item => item.target);
  let scheduled = false;
  const updatePosition = () => {
    scheduled = false;
    const clearance = header.getBoundingClientRect().height + 36;
    let active = null;
    for (const item of sections) {
      if (item.target.getBoundingClientRect().top <= clearance) active = item;
    }
    for (const item of sections) {
      if (item === active) item.link.setAttribute('aria-current', 'location');
      else item.link.removeAttribute('aria-current');
    }
    if (article && progress) {
      const bounds = article.getBoundingClientRect();
      const distance = Math.max(1, bounds.height - window.innerHeight + clearance);
      const amount = Math.max(0, Math.min(1, (clearance - bounds.top) / distance));
      progress.style.transform = `scaleX(${amount})`;
    }
  };
  const requestUpdate = () => {
    if (!scheduled) { scheduled = true; requestAnimationFrame(updatePosition); }
  };
  window.addEventListener('scroll', requestUpdate, { passive: true });
  window.addEventListener('resize', requestUpdate);
  window.addEventListener('load', requestUpdate);
  if ('ResizeObserver' in window && article) new ResizeObserver(requestUpdate).observe(article);
  updatePosition();
})();
