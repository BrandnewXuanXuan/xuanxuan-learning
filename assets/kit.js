// 單元頁共用的小工具（規範見 DESIGN.md）
window.Kit = (() => {
  const ICONS = '../../assets/icons.svg' + (document.currentScript ? new URL(document.currentScript.src).search : '');
  const icon = (id) => `<svg aria-hidden="true"><use href="${ICONS}#${id}"/></svg>`;
  // 情境選擇：root 內的 .pick[data-c] 對應 items[i] = [icon, 標題, 說明]
  function picks(root, items) {
    const box = root.querySelector('.answer');
    root.querySelectorAll('.pick').forEach((b) => b.addEventListener('click', () => {
      root.querySelectorAll('.pick').forEach((x) => x.classList.toggle('on', x === b));
      const [ic, t, p] = items[+b.dataset.c];
      box.innerHTML = `<span class="badge">${icon(ic)}</span><div><h4></h4><p></p></div>`;
      box.querySelector('h4').textContent = t; box.querySelector('p').textContent = p;
      box.classList.remove('show'); void box.offsetWidth; box.classList.add('show');
    }));
  }
  // 分段切換：root 內的 .btn[data-k]，點了呼叫 render(key)，並標示選中的按鈕
  function tabs(root, render, first) {
    const bs = root.querySelectorAll('.ctl .btn[data-k]');
    const go = (k) => { bs.forEach((x) => x.classList.toggle('on', x.dataset.k === k)); render(k); };
    bs.forEach((b) => b.addEventListener('click', () => go(b.dataset.k)));
    go(first || bs[0].dataset.k);
  }
  return { icon, picks, tabs };
})();
