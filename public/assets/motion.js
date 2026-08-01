/* Sealion Tech — 波态：让页面里有"正在发生"的东西。零依赖。
   四件事共用一个 IntersectionObserver 池，减少滚动期的开销。
   全部尊重 prefers-reduced-motion：偏好减弱动画时，各自退回静态终值，
   而不是"没有动画也没有内容"。 */
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 1. 滚动揭示：区块进入视口时轻微上浮淡入 ---------- */
  var reveals = document.querySelectorAll('[data-reveal]');
  if (reveals.length) {
    if (reduce || !('IntersectionObserver' in window)) {
      for (var i = 0; i < reveals.length; i++) reveals[i].classList.add('is-in');
    } else {
      var ro = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add('is-in');
          ro.unobserve(e.target);          // 一次性，不来回闪
        });
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0.05 });
      for (var j = 0; j < reveals.length; j++) ro.observe(reveals[j]);
    }
  }

  /* ---------- 2. 数字滚动：进入视口时从 0 跑到目标值 ---------- */
  var nums = document.querySelectorAll('[data-count]');
  if (nums.length) {
    var run = function (el) {
      var target = parseFloat(el.getAttribute('data-count'));
      var suffix = el.getAttribute('data-suffix') || '';
      if (!isFinite(target)) return;
      var dur = 1100, t0 = null;
      var step = function (ts) {
        if (t0 === null) t0 = ts;
        var p = Math.min(1, (ts - t0) / dur);
        var eased = 1 - Math.pow(1 - p, 3);          // ease-out cubic
        el.textContent = Math.round(target * eased) + (p === 1 ? suffix : '');
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    if (reduce || !('IntersectionObserver' in window)) {
      for (var k = 0; k < nums.length; k++) {
        nums[k].textContent = nums[k].getAttribute('data-count') +
          (nums[k].getAttribute('data-suffix') || '');
      }
    } else {
      var no = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          run(e.target);
          no.unobserve(e.target);
        });
      }, { threshold: 0.4 });
      for (var m = 0; m < nums.length; m++) no.observe(nums[m]);
    }
  }

  /* ---------- 3. 客户 logo 横向滚动 ---------- */
  var marquee = document.querySelector('[data-marquee]');
  if (marquee) {
    var track = marquee.firstElementChild;
    if (track && !reduce && marquee.children.length === 1) {
      // 复制一份接在后面，位移到 -50% 时画面与起点完全相同，于是无缝
      var clone = track.cloneNode(true);
      clone.setAttribute('aria-hidden', 'true');
      // 复制出来的链接不该被键盘走到，否则同一个客户会被读两遍
      var links = clone.querySelectorAll('a');
      for (var n = 0; n < links.length; n++) links[n].setAttribute('tabindex', '-1');
      marquee.appendChild(clone);
      marquee.classList.add('is-running');
      // 按内容宽度定速，保证快慢与条目多少无关
      var w = track.scrollWidth;
      marquee.style.setProperty('--marquee-dur', Math.max(24, Math.round(w / 110)) + 's');
    }
  }
})();
