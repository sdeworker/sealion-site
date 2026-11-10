(() => {
  const banner = document.querySelector("[data-home-banner]");
  if (!banner) return;

  const slides = Array.from(banner.querySelectorAll("[data-banner-slide]"));
  const dots = Array.from(banner.querySelectorAll("[data-banner-dot]"));
  if (slides.length < 2 || slides.length !== dots.length) return;

  const controls = banner.querySelector("[data-banner-controls]");
  const toggle = controls.querySelector("[data-banner-toggle]");
  const status = banner.querySelector("[data-banner-status]");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const slideInterval = 5000;
  let current = 0;
  let autoplay = !reduceMotion.matches;
  let timer;

  function showSlide(index, announce) {
    const next = (index + slides.length) % slides.length;
    if (next === current) return;

    slides[current].classList.remove("is-active");
    slides[current].setAttribute("aria-hidden", "true");
    dots[current].removeAttribute("aria-current");
    slides[next].classList.add("is-active");
    slides[next].removeAttribute("aria-hidden");
    dots[next].setAttribute("aria-current", "true");
    current = next;

    if (announce) {
      status.textContent = dots[current].getAttribute("aria-label");
    }
  }

  function scheduleAdvance() {
    window.clearTimeout(timer);
    if (!autoplay || document.hidden) return;

    timer = window.setTimeout(() => {
      const next = (current + 1) % slides.length;
      const photo = slides[next].querySelector("img");
      if (photo.complete && photo.naturalWidth > 0) showSlide(next, false);
      scheduleAdvance();
    }, slideInterval);
  }

  function updatePlayback() {
    const label = autoplay ? toggle.dataset.pauseLabel : toggle.dataset.resumeLabel;
    banner.dataset.autoplay = autoplay ? "on" : "off";
    toggle.setAttribute("aria-label", label);
    toggle.title = label;
    scheduleAdvance();
  }

  function selectSlide(index) {
    showSlide(index, true);
    scheduleAdvance();
  }

  controls.querySelector("[data-banner-prev]").addEventListener("click", () => selectSlide(current - 1));
  controls.querySelector("[data-banner-next]").addEventListener("click", () => selectSlide(current + 1));
  dots.forEach((dot, index) => dot.addEventListener("click", () => selectSlide(index)));

  toggle.addEventListener("click", () => {
    autoplay = !autoplay;
    updatePlayback();
  });

  controls.addEventListener("focusin", (event) => {
    if (autoplay && event.target.matches(":focus-visible")) {
      autoplay = false;
      updatePlayback();
    }
  });

  reduceMotion.addEventListener("change", (event) => {
    if (event.matches) {
      autoplay = false;
      updatePlayback();
    }
  });

  document.addEventListener("visibilitychange", scheduleAdvance);
  controls.hidden = false;
  updatePlayback();
})();
