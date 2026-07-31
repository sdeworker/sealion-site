/* 首页头部：压在 Hero 大图上时透明，滚过一屏后变实底。零依赖。 */
(function () {
  var h = document.querySelector('[data-header]');
  if (!h || !document.body.classList.contains('home')) return;
  var solid = false;
  function sync() {
    var want = window.scrollY > 60;
    if (want !== solid) { solid = want; h.classList.toggle('is-solid', want); }
  }
  sync();
  window.addEventListener('scroll', sync, { passive: true });
})();
