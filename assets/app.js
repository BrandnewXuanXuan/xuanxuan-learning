(() => {
  const app = document.getElementById('app');
  const bar = document.getElementById('bar');
  const ICONS = 'assets/icons.svg';
  const ROT = [-1.4, 1.1, .8, -1, -.6, 1.3, 1, -1.2];
  let catalog = null;

  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const icon = (id, cls = 'i') => `<svg class="${cls}" aria-hidden="true"><use href="${ICONS}#${id}"/></svg>`;

  // 主題狀態：learned 全部學完；open 有可學的單元；idle 還沒有單元
  function topicState(t) {
    const ls = (t.lessons || []).filter((l) => l.status !== 'planned');
    if (!ls.length) return 'idle';
    return ls.every((l) => l.status === 'learned') ? 'learned' : 'open';
  }
  const tally = (topics) => {
    const s = topics.map(topicState);
    return { learned: s.filter((x) => x === 'learned').length, open: s.filter((x) => x === 'open').length, idle: s.filter((x) => x === 'idle').length };
  };
  const marks = (st) => (st === 'learned' ? '<span class="stamp">學完</span>' : st === 'open' ? '<span class="ribbon" aria-label="可以學"></span>' : '');
  const tallyHtml = ({ learned, open, idle }) => `<div class="tally">
    <span><i class="dot d-stamp"></i>學完 ${learned}</span><span><i class="dot d-mark"></i>可以學 ${open}</span><span><i class="dot d-idle"></i>還沒開始 ${idle}</span></div>`;

  function setBar(back, title, right = '') {
    bar.innerHTML = (back ? `<a class="back" href="${back}" aria-label="返回">${icon('back')}</a>` : '') +
      `<span class="bar-title">${esc(title)}</span>` + right;
  }
  const domainPills = (activeId) => `<nav class="domains" aria-label="領域">${catalog.domains.map((d) =>
    `<a class="dom${d.id === activeId ? ' on' : ''}" href="#/d/${d.id}">${icon(d.icon)}${esc(d.short || d.title)}</a>`).join('')}</nav>`;

  function home() {
    setBar(null, '軒軒自修室', `<a class="bar-link" href="#/log">${icon('trail')}學習軌跡</a>`);
    const cards = catalog.domains.map((d, i) => {
      const t = tally(d.topics);
      const st = t.learned && t.learned === d.topics.length ? 'learned' : (t.open || t.learned) ? 'open' : 'idle';
      return `<a class="card wide${st === 'idle' ? ' idle' : ''}" href="#/d/${d.id}" style="--c: var(--clay); --r:${ROT[i % 8] / 2}deg; --d:${i * 60}ms">
        <span class="tab">${icon(d.icon)}${esc(d.short || d.title)}</span>
        <div class="name">${esc(d.title)}</div><div class="desc">${esc(d.summary)}</div>
        <div class="st">${d.topics.length} 個主題・學完 ${t.learned}</div></a>`;
    }).join('');
    app.innerHTML = `<h1>想學的，都在這</h1><p class="sub">一個領域一疊卡。學完回研究夥伴，寫成自己的筆記才算數。</p><div class="stack">${cards}</div>`;
  }

  function domain(id) {
    const d = catalog.domains.find((x) => x.id === id);
    if (!d) return notFound();
    setBar(catalog.domains.length > 1 ? '#/' : null, '軒軒自修室', `<a class="bar-link" href="#/log">${icon('trail')}學習軌跡</a>`);
    const cards = d.topics.map((t, i) => {
      const st = topicState(t);
      const n = (t.lessons || []).filter((l) => l.status !== 'planned').length;
      return `<a class="card${st === 'idle' ? ' idle' : ''}" href="#/t/${d.id}/${t.id}" style="--c: var(--${t.color}); --r:${ROT[i % 8]}deg; --d:${i * 50}ms">
        <span class="tab">${icon(t.icon)}</span><div class="name">${esc(t.title)}</div>
        <div class="st">${n ? `${n} 個單元` : '還沒有單元'}</div>${marks(st)}</a>`;
    }).join('');
    app.innerHTML = `${domainPills(d.id)}<h1>${esc(d.title)}</h1><p class="sub">${esc(d.summary)}</p>${tallyHtml(tally(d.topics))}<div class="grid">${cards}</div>`;
  }

  function topic(did, tid) {
    const d = catalog.domains.find((x) => x.id === did);
    const t = d && d.topics.find((x) => x.id === tid);
    if (!t) return notFound();
    setBar(`#/d/${d.id}`, d.title);
    const ls = t.lessons || [];
    const cards = ls.map((l, i) => {
      const st = l.status === 'learned' ? 'learned' : l.status === 'ready' ? 'open' : 'idle';
      const meta = l.status === 'learned' ? `${esc(l.learnedAt)} 學完` : l.status === 'ready' ? `${esc(l.added)} 加入` : '規劃中';
      const inner = `<span class="tab">${icon(t.icon)}${esc(l.short || '')}</span><div class="name">${esc(l.title)}</div>
        <div class="desc">${esc(l.summary)}</div><div class="st">${meta}</div>${marks(st)}`;
      const style = `--c: var(--${t.color}); --r:${ROT[i % 8] / 2}deg; --d:${i * 60}ms`;
      return l.file && l.status !== 'planned' ? `<a class="card wide" href="${l.file}" style="${style}">${inner}</a>` : `<div class="card wide idle" style="${style}">${inner}</div>`;
    }).join('');
    app.innerHTML = `<h1>${esc(t.title)}</h1><p class="sub">${esc(t.summary)}</p>` +
      (ls.length ? `<div class="stack">${cards}</div>` : '<p class="empty">這個主題還沒有單元。想先學它，就跟研究夥伴說一聲。</p>');
  }

  function log() {
    setBar('#/', '學習軌跡');
    const items = catalog.domains.flatMap((d) => d.topics.flatMap((t) => (t.lessons || [])
      .filter((l) => l.status !== 'planned').map((l) => ({ d, t, l, date: l.learnedAt || l.added }))))
      .sort((a, b) => (b.date || '').localeCompare(a.date || ''));
    app.innerHTML = `<h1>學習軌跡</h1><p class="sub">同一批單元，按時間排。</p>` + (items.length ? `<div class="trail">${items.map(({ d, t, l, date }) => `
      <div class="trail-item ${l.status}"><span class="pin"></span><div class="trail-date">${esc(date)}・${l.status === 'learned' ? '學完' : '加入'}</div>
      <a href="${l.file}">${esc(l.title)}</a><div class="where">${esc(d.short || d.title)} › ${esc(t.title)}</div></div>`).join('')}</div>` : '<p class="empty">還沒有內容。</p>');
  }

  function notFound() { setBar('#/', '找不到'); app.innerHTML = '<p class="empty">找不到這一頁。</p>'; }

  function route() {
    const p = location.hash.replace(/^#\/?/, '').split('/').filter(Boolean);
    if (!p.length) {
      // 只有一個領域時，首頁直接是那個領域
      if (catalog.domains.length === 1) return domain(catalog.domains[0].id);
      home();
    } else if (p[0] === 'd') domain(p[1]);
    else if (p[0] === 't') topic(p[1], p[2]);
    else if (p[0] === 'log') log();
    else notFound();
    window.scrollTo(0, 0);
  }

  // 每個領域一個檔案（data/domains/<id>.json），由 data/domains.json 列出順序
  const getJSON = (u) => fetch(u, { cache: 'no-cache' }).then((r) => { if (!r.ok) throw new Error(u); return r.json(); });
  getJSON('data/domains.json')
    .then((idx) => Promise.all(idx.domains.map((id) => getJSON(`data/domains/${id}.json`))))
    .then((list) => { catalog = { domains: list }; route(); window.addEventListener('hashchange', route); })
    .catch(() => { app.innerHTML = '<p class="empty">讀取目錄失敗，請稍後再試。</p>'; });

  if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
})();
