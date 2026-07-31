/* 打印时在页脚盖一个出处戳：网址 + 日期。零依赖。 */
(function () {
  var el = document.querySelector('[data-print-stamp]');
  if (!el) return;
  function stamp() {
    var d = new Date();
    el.textContent = location.href + '　·　' + d.getFullYear() + '-' +
      String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }
  stamp();
  window.addEventListener('beforeprint', stamp);
})();
