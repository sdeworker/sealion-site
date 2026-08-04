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


  /* ---------- 4. 时间轴：年份可点 + 逐条浮现 ---------- */
  var tl = document.querySelector('[data-timeline]');
  if (tl) {
    var items = [].slice.call(tl.querySelectorAll('.tl-i'));
    var nav = tl.querySelector('[data-tl-nav]');
    // 年份按钮：点了把那一年滑到视野中间
    if (nav && items.length) {
      nav.removeAttribute('aria-hidden');
      items.forEach(function (it, i) {
        var y = it.querySelector('.tl-y');
        if (!y) return;
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'tl-y-btn' + (i === 0 ? ' is-on' : '');
        btn.textContent = y.textContent;
        btn.addEventListener('click', function () {
          var left = it.offsetLeft - (tl.clientWidth - it.offsetWidth) / 2;
          tl.scrollTo({ left: left, behavior: reduce ? 'auto' : 'smooth' });
          nav.querySelectorAll('.tl-y-btn').forEach(function (b) { b.classList.remove('is-on'); });
          btn.classList.add('is-on');
        });
        nav.appendChild(btn);
      });
      // 横向滚动时同步高亮当前年份
      var sync = function () {
        var mid = tl.scrollLeft + tl.clientWidth / 2, best = 0, dist = 1e9;
        items.forEach(function (it, i) {
          var d = Math.abs(it.offsetLeft + it.offsetWidth / 2 - mid);
          if (d < dist) { dist = d; best = i; }
        });
        var bs = nav.querySelectorAll('.tl-y-btn');
        for (var i = 0; i < bs.length; i++) bs[i].classList.toggle('is-on', i === best);
      };
      tl.addEventListener('scroll', function () {
        clearTimeout(tl._t); tl._t = setTimeout(sync, 90);
      }, { passive: true });
    }
    // 自动滚动：一直向前，到头无缝接回 2008，形成闭环。
    // 做法和客户轮播一样——把整条轨道复制一份接在后面，
    // 滚过第一条的宽度就把 scrollLeft 减掉那个宽度，画面完全相同，看不出接缝。
    if (!reduce) {
      var track = tl.querySelector('.tl-track');
      var loopW = 0;
      if (track && tl.querySelectorAll('.tl-track').length === 1) {
        var dup = track.cloneNode(true);
        dup.setAttribute('aria-hidden', 'true');
        dup.querySelectorAll('a,button').forEach(function (e) { e.setAttribute('tabindex', '-1'); });
        track.parentNode.appendChild(dup);
      }
      var paused = false, last = null;
      var step = function (ts) {
        if (last === null) last = ts;
        var dt = Math.min(64, ts - last); last = ts;
        if (!paused) {
          if (!loopW) loopW = track ? track.scrollWidth : 0;
          tl.scrollLeft += 55 * dt / 1000;            // 约 55px/秒
          if (loopW && tl.scrollLeft >= loopW) tl.scrollLeft -= loopW;
        }
        requestAnimationFrame(step);
      };
      var hold = function () { paused = true; };
      var go = function () { paused = false; };
      tl.addEventListener('mouseenter', hold);
      tl.addEventListener('mouseleave', go);
      tl.addEventListener('focusin', hold);
      tl.addEventListener('touchstart', hold, { passive: true });
      requestAnimationFrame(step);
    }

    // 逐条浮现
    if (reduce || !('IntersectionObserver' in window)) {
      items.forEach(function (it) { it.classList.add('is-in'); });
    } else {
      var io2 = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add('is-in');
          io2.unobserve(e.target);
        });
      }, { root: tl, threshold: 0.25 });
      items.forEach(function (it) { io2.observe(it); });
    }
  }

})();
