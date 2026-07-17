/* Sealion Tech — minimal image lightbox. Zero dependencies, no localStorage. */
(function () {
  var triggers = document.querySelectorAll('[data-lightbox]');
  if (!triggers.length) return;

  var overlay = document.createElement('div');
  overlay.className = 'lb-overlay';
  overlay.innerHTML =
    '<button class="lb-close" aria-label="关闭">&times;</button>' +
    '<button class="lb-prev" aria-label="上一张">&lsaquo;</button>' +
    '<img class="lb-img" alt="">' +
    '<button class="lb-next" aria-label="下一张">&rsaquo;</button>';
  document.body.appendChild(overlay);

  var imgEl = overlay.querySelector('.lb-img');
  var groups = {};
  Array.prototype.forEach.call(triggers, function (t) {
    var g = t.getAttribute('data-lightbox');
    (groups[g] = groups[g] || []).push(t);
  });

  var currentGroup = [], currentIndex = 0;

  function show(i) {
    currentIndex = (i + currentGroup.length) % currentGroup.length;
    var t = currentGroup[currentIndex];
    imgEl.src = t.getAttribute('href');
    imgEl.alt = t.getAttribute('aria-label') || '';
  }
  function open(group, index) {
    currentGroup = groups[group];
    show(index);
    overlay.classList.add('open');
    document.documentElement.style.overflow = 'hidden';
  }
  function close() {
    overlay.classList.remove('open');
    document.documentElement.style.overflow = '';
  }

  Array.prototype.forEach.call(triggers, function (t) {
    t.addEventListener('click', function (e) {
      e.preventDefault();
      var g = t.getAttribute('data-lightbox');
      open(g, groups[g].indexOf(t));
    });
  });

  overlay.querySelector('.lb-close').addEventListener('click', close);
  overlay.querySelector('.lb-prev').addEventListener('click', function () { show(currentIndex - 1); });
  overlay.querySelector('.lb-next').addEventListener('click', function () { show(currentIndex + 1); });
  overlay.addEventListener('click', function (e) { if (e.target === overlay) close(); });
  document.addEventListener('keydown', function (e) {
    if (!overlay.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(currentIndex - 1);
    if (e.key === 'ArrowRight') show(currentIndex + 1);
  });
})();
