/* Sealion Tech — shared homepage back-to-top control. Zero dependencies. */
(function () {
  var button = document.querySelector('[data-back-to-top]');
  if (!button) return;
  var focusTarget = document.querySelector('main');
  var assistantLauncher = document.querySelector('.ai-launcher');

  var reduceMotion = window.matchMedia
    ? window.matchMedia('(prefers-reduced-motion: reduce)')
    : null;
  var ticking = false;

  function syncVisibility() {
    button.classList.toggle('is-visible', window.scrollY >= window.innerHeight);
    ticking = false;
  }

  function scheduleVisibilitySync() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(syncVisibility);
  }

  function syncAssistantOffset() {
    if (!assistantLauncher) return;
    var launcherHeight = assistantLauncher.getBoundingClientRect().height;
    if (launcherHeight > 0) {
      button.style.setProperty('--ai-launcher-height', launcherHeight + 'px');
    }
  }

  button.addEventListener('click', function () {
    var behavior = reduceMotion && reduceMotion.matches ? 'auto' : 'smooth';
    if (focusTarget) focusTarget.focus({ preventScroll: true });
    window.scrollTo({ top: 0, left: 0, behavior: behavior });
  });
  window.addEventListener('scroll', scheduleVisibilitySync, { passive: true });
  window.addEventListener('resize', function () {
    scheduleVisibilitySync();
    syncAssistantOffset();
  });
  if (assistantLauncher && window.ResizeObserver) {
    new ResizeObserver(syncAssistantOffset).observe(assistantLauncher);
  }
  syncAssistantOffset();
  syncVisibility();
})();
