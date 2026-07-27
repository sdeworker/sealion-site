/* 移动端导航开关：真按钮 + aria-expanded，键盘可用，Esc 可关 */
(function () {
  var b = document.querySelector('.burger');
  var n = document.getElementById('site-nav');
  if (!b || !n) return;
  function set(open) {
    b.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  b.addEventListener('click', function () {
    set(b.getAttribute('aria-expanded') !== 'true');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && b.getAttribute('aria-expanded') === 'true') {
      set(false); b.focus();
    }
  });
  n.addEventListener('click', function (e) {
    if (e.target.tagName === 'A') set(false);
  });
})();
