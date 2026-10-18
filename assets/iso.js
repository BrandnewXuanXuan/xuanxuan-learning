// 單元頁共用的等角立體繪圖工具（規範見 DESIGN.md）
window.Iso = (() => {
  const Q = document.currentScript ? new URL(document.currentScript.src).search : '';
  const NS = 'http://www.w3.org/2000/svg';
  const mk = (t, a = {}, txt) => {
    const n = document.createElementNS(NS, t);
    for (const k in a) n.setAttribute(k, a[k]);
    if (txt != null) n.textContent = txt;
    return n;
  };
  // 主題色：讀 CSS token，取不到時用 DESIGN.md 的預設值
  const FALLBACK = { sage: '#7f9d8c', slate: '#7489a8', ochre: '#c9a043', clay: '#c4785a', moss: '#94a06a', dusk: '#8b8fb8', teal: '#5f9a9a', stone: '#a99f90', stamp: '#c4473a', idle: '#dddbd2' };
  const color = (name) => (getComputedStyle(document.documentElement).getPropertyValue('--' + name).trim() || FALLBACK[name] || name);

  function shade(hex, f) {
    const n = parseInt(hex.replace('#', ''), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255;
    const m = (c) => Math.round(f < 0 ? c * (1 + f) : c + (255 - c) * f);
    return `rgb(${m(r)},${m(g)},${m(b)})`;
  }

  // 一塊等角方塊：底面中心 (cx, cy)，半寬 s，高 h。左側 -12%、右側 -26%、頂面 +8%
  function block(cx, cy, s, h, hex) {
    const g = mk('g'), q = s / 2;
    g.append(
      mk('path', { d: `M${cx - s} ${cy - h}L${cx} ${cy + q - h}L${cx} ${cy + q}L${cx - s} ${cy}Z`, fill: shade(hex, -0.12) }),
      mk('path', { d: `M${cx + s} ${cy - h}L${cx} ${cy + q - h}L${cx} ${cy + q}L${cx + s} ${cy}Z`, fill: shade(hex, -0.26) }),
      mk('path', { d: `M${cx} ${cy - q - h}L${cx + s} ${cy - h}L${cx} ${cy + q - h}L${cx - s} ${cy - h}Z`, fill: shade(hex, 0.08) }),
      mk('path', { d: `M${cx - s} ${cy - h}L${cx} ${cy - q - h}L${cx + s} ${cy - h}`, fill: 'none', stroke: 'rgba(255,255,255,.5)', 'stroke-width': 1 })
    );
    return g;
  }
  // 虛線的等角框（門檻、空位）
  function outline(cx, cy, s, h, stroke) {
    const q = s / 2;
    return mk('path', { d: `M${cx} ${cy - q - h}L${cx + s} ${cy - h}L${cx} ${cy + q - h}L${cx - s} ${cy - h}Z`, fill: 'none', stroke, 'stroke-width': 1.5, 'stroke-dasharray': '5 4' });
  }
  function icon(id, x, y, size, cls) {
    const s = mk('svg', { x, y, width: size, height: size, class: cls || '' });
    s.append(mk('use', { href: '../../assets/icons.svg' + Q + '#' + id }));
    return s;
  }
  return { mk, color, shade, block, outline, icon };
})();
