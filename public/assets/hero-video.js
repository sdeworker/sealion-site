/* Hero 背景视频 + 点击播放完整版
   · 背景版静音循环；减弱动画偏好时移除，只留封面
   · 点击播放按钮打开灯箱，播放带声音的完整版 */
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var bg = document.querySelector('.hero-video video');
  if (bg) {
    if (reduce) { bg.remove(); }
    else {
      var tryPlay = function () {
        var p = bg.play();
        if (p && p.catch) p.catch(function () { bg.style.display = 'none'; });
      };
      if (bg.readyState >= 2) tryPlay();
      else bg.addEventListener('loadeddata', tryPlay, { once: true });
    }
  }

  var btn = document.querySelector('[data-hero-play]');
  if (!btn) return;
  var box, vid, lastFocus;

  function close() {
    if (!box) return;
    vid.pause();
    box.hidden = true;
    document.body.style.overflow = '';
    if (lastFocus) lastFocus.focus();
  }

  function open() {
    lastFocus = document.activeElement;
    if (!box) {
      box = document.createElement('div');
      box.className = 'hero-lb';
      box.hidden = true;
      box.setAttribute('role', 'dialog');
      box.setAttribute('aria-modal', 'true');
      box.setAttribute('aria-label', btn.getAttribute('aria-label') || 'video');
      box.innerHTML =
        '<button class="hero-lb-close" type="button" aria-label="Close">&times;</button>' +
        '<video controls playsinline preload="none" ' +
        'poster="/assets/2026/video/company-intro-poster.webp">' +
        '<source src="/assets/2026/video/company-intro.mp4" type="video/mp4"></video>';
      document.body.appendChild(box);
      vid = box.querySelector('video');
      box.querySelector('.hero-lb-close').addEventListener('click', close);
      box.addEventListener('click', function (e) { if (e.target === box) close(); });
    }
    box.hidden = false;
    document.body.style.overflow = 'hidden';
    vid.currentTime = 0;
    vid.play().catch(function () {});
    box.querySelector('.hero-lb-close').focus();
  }

  btn.addEventListener('click', open);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && box && !box.hidden) close();
  });
})();
