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

  /* ---------- 3. 客户 logo 漂浮云 ----------
     不是几条传送带，是一片有纵深的云：远层小而淡、走得慢，
     近层大而清晰、走得快，相邻层方向相反。速度差就是景深。 */
  var layers = document.querySelectorAll('[data-cloud] .pcloud-l');
  if (layers.length && !reduce) {
    for (var q = 0; q < layers.length; q++) {
      var L = layers[q], track = L.firstElementChild;
      if (!track || L.children.length !== 1) continue;
      var copy = track.cloneNode(true);
      copy.setAttribute('aria-hidden', 'true');
      var ls = copy.querySelectorAll('a');
      for (var r = 0; r < ls.length; r++) ls[r].setAttribute('tabindex', '-1');
      L.appendChild(copy);
      L.classList.add('is-running');
    }
  }

})();
