/* Hero 背景视频：部分浏览器即便有 autoplay 属性也需显式 play()；
   失败时静默退回封面图，不打扰用户 */
(function () {
  var v = document.querySelector('.hero-video video');
  if (!v) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { v.remove(); return; }
  var tryPlay = function () {
    var p = v.play();
    if (p && p.catch) p.catch(function () { v.style.display = 'none'; });
  };
  if (v.readyState >= 2) tryPlay();
  else v.addEventListener('loadeddata', tryPlay, { once: true });
})();
