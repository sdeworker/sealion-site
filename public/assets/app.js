/* Sealion Tech — AI technical-sales-engineer widget. Zero dependencies.
   Config (greeting / fallback text / lang) is read from data-* on .ai so the
   same file serves both language pages. No localStorage/sessionStorage. */
(function () {
  var root = document.querySelector('[data-ai]');
  if (!root) return;
  var panel = root.querySelector('[data-ai-panel]');
  var log = root.querySelector('[data-ai-log]');
  var form = root.querySelector('[data-ai-form]');
  var input = root.querySelector('[data-ai-input]');
  var cfg = {
    lang: root.getAttribute('data-lang') || 'zh',
    greeting: root.getAttribute('data-greeting') || '',
    fallback: root.getAttribute('data-fallback') || '',
    error: root.getAttribute('data-error') || ''
  };
  var history = [];
  var started = false, busy = false;

  function open() {
    panel.hidden = false;
    requestAnimationFrame(function () { panel.classList.add('open'); });
    if (!started) { started = true; addMsg('bot', cfg.greeting); }
    setTimeout(function () { input && input.focus(); }, 120);
  }
  function close() {
    panel.classList.remove('open');
    setTimeout(function () { panel.hidden = true; }, 220);
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-open-ai]'), function (b) {
    b.addEventListener('click', open);
  });
  var closeBtn = root.querySelector('[data-ai-close]');
  if (closeBtn) closeBtn.addEventListener('click', close);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !panel.hidden) close();
  });

  function addMsg(role, text) {
    var el = document.createElement('div');
    el.className = 'msg msg--' + role;
    var b = document.createElement('div');
    b.className = 'bubble';
    b.textContent = text;
    el.appendChild(b);
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return b;
  }

  if (input) {
    input.addEventListener('input', function () {
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); }
    });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var text = (input.value || '').trim();
    if (!text || busy) return;
    addMsg('user', text);
    history.push({ role: 'user', content: text });
    input.value = ''; input.style.height = 'auto';
    busy = true;

    var bubble = addMsg('bot', '');
    bubble.classList.add('typing');
    bubble.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';

    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: history, lang: cfg.lang })
    }).then(function (res) {
      if (!res.ok || !res.body) throw new Error('no-backend');
      bubble.classList.remove('typing');
      bubble.textContent = '';
      var reader = res.body.getReader();
      var dec = new TextDecoder();
      var acc = '';
      function pump() {
        return reader.read().then(function (r) {
          if (r.done) return;
          var chunk = dec.decode(r.value, { stream: true });
          chunk.split('\n').forEach(function (line) {
            var s = line.trim();
            if (s.indexOf('data:') !== 0) return;
            var payload = s.slice(5).trim();
            if (!payload || payload === '[DONE]') return;
            try {
              var j = JSON.parse(payload);
              var piece = j.delta || j.text || '';
              if (piece) { acc += piece; bubble.textContent = acc; log.scrollTop = log.scrollHeight; }
            } catch (_) {}
          });
          return pump();
        });
      }
      return pump().then(function () {
        if (!acc) throw new Error('empty');
        history.push({ role: 'assistant', content: acc });
      });
    }).catch(function () {
      // Backend not configured (or unreachable): degrade to a helpful contact prompt.
      bubble.classList.remove('typing');
      bubble.textContent = cfg.fallback || cfg.error;
      history.pop(); // drop the unanswered user turn from context
    }).then(function () {
      busy = false;
      if (input) input.focus();
    });
  });
})();
