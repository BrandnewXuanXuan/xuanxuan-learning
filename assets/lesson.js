// 單元頁共用：註冊 service worker（路徑相對於網站根目錄）。
(() => {
  const root = document.currentScript.getAttribute('data-root') || '../../';
  if ('serviceWorker' in navigator) navigator.serviceWorker.register(root + 'sw.js').catch(() => {});
})();
