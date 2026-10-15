/* Small enhancements; all text, navigation, and SVGs also work without JavaScript. */
(() => {
  const root = document.documentElement;
  const theme = document.querySelector('.theme-toggle');
  const isDark = () => root.dataset.theme === 'dark' ||
    (!root.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches);
  const updateThemeLabel = () => {
    theme.setAttribute('aria-label', `Switch to ${isDark() ? 'light' : 'dark'} theme`);
    theme.title = theme.getAttribute('aria-label');
  };
  updateThemeLabel();
  theme.addEventListener('click', () => {
    root.dataset.theme = isDark() ? 'light' : 'dark';
    try { localStorage.setItem('docs-theme', root.dataset.theme); } catch (_) {}
    updateThemeLabel();
  });

  const menu = document.querySelector('.menu-toggle');
  const shade = document.querySelector('.nav-shade');
  const setMenu = open => {
    document.body.classList.toggle('nav-open', open);
    menu.setAttribute('aria-expanded', String(open));
    shade.hidden = !open;
  };
  menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
  shade.addEventListener('click', () => setMenu(false));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') { setMenu(false); menu.focus(); }
  });

  document.querySelectorAll('.math').forEach(element => {
    try {
      katex.render(element.textContent, element, {
        displayMode: element.dataset.display === 'true', throwOnError: true, trust: false,
      });
    } catch (error) {
      element.classList.add('math-error');
      console.error('Formula rendering failed:', error);
    }
  });

  const links = [...document.querySelectorAll('.table-of-contents a')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        links.forEach(link => {
          if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      }
    }, { rootMargin: '-120px 0px -60% 0px' });
    document.querySelectorAll('.prose h2, .prose h3').forEach(heading => observer.observe(heading));
  }
})();
