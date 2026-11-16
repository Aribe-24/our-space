/**
 * Our Space — Interactive Vanilla JS
 * Cozy micro-interactions, dark mode, heart animations, and live time updates
 */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initHeartTap();
  initEmojiSelector();
  initModals();
  initDismissBanner();
  initLiveClocks();
  initAjaxCheckin();
  initAjaxThisOrThat();
  initActivityToasts();
  initDoodlePad();
  initCopyLocation();
});

function initCopyLocation() {
  const copyButton = document.querySelector('[data-copy-my-location]');
  if (!copyButton) return;
  copyButton.addEventListener('click', () => {
    const myCity = document.getElementById('id_city')?.value;
    const myTimezone = document.getElementById('id_timezone')?.value;
    if (!myCity || !myTimezone) {
      showActivityToast('Add your own city and timezone first.', 'error');
      return;
    }
    document.getElementById('partner-city').value = myCity;
    document.getElementById('partner-timezone').value = myTimezone;
    showActivityToast('Jay’s location now matches yours. Save to confirm.');
  });
}

function initDoodlePad() {
  const canvas = document.getElementById('doodle-canvas');
  const form = document.getElementById('doodle-form');
  if (!canvas || !form) return;

  const ctx = canvas.getContext('2d');
  const input = document.getElementById('id_image');
  const send = document.getElementById('doodle-send');
  const size = document.getElementById('brush-size');
  let ink = '#381a2c';
  let strokes = [];
  let activeStroke = null;

  function clearCanvas() {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  function pointFromEvent(event) {
    const rect = canvas.getBoundingClientRect();
    return {
      x: (event.clientX - rect.left) * canvas.width / rect.width,
      y: (event.clientY - rect.top) * canvas.height / rect.height,
    };
  }

  function drawStroke(stroke) {
    if (!stroke.points.length) return;
    ctx.strokeStyle = stroke.ink;
    ctx.lineWidth = stroke.width;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
    if (stroke.points.length === 1) {
      ctx.lineTo(stroke.points[0].x + 0.1, stroke.points[0].y + 0.1);
    } else {
      stroke.points.slice(1).forEach(point => ctx.lineTo(point.x, point.y));
    }
    ctx.stroke();
  }

  function redraw() {
    clearCanvas();
    strokes.forEach(drawStroke);
  }

  clearCanvas();
  canvas.addEventListener('pointerdown', event => {
    event.preventDefault();
    canvas.setPointerCapture(event.pointerId);
    activeStroke = { ink, width: Number(size.value), points: [pointFromEvent(event)] };
    strokes.push(activeStroke);
    drawStroke(activeStroke);
  });
  canvas.addEventListener('pointermove', event => {
    if (!activeStroke) return;
    activeStroke.points.push(pointFromEvent(event));
    drawStroke(activeStroke);
  });
  const finishStroke = () => { activeStroke = null; };
  canvas.addEventListener('pointerup', finishStroke);
  canvas.addEventListener('pointercancel', finishStroke);

  document.querySelectorAll('.color-swatch').forEach(swatch => {
    swatch.addEventListener('click', () => {
      ink = swatch.dataset.ink;
      document.querySelectorAll('.color-swatch').forEach(item => item.classList.toggle('selected', item === swatch));
    });
  });
  document.getElementById('doodle-clear')?.addEventListener('click', () => { strokes = []; redraw(); });
  document.getElementById('doodle-undo')?.addEventListener('click', () => { strokes.pop(); redraw(); });

  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!strokes.length) {
      showActivityToast('Draw a little something first ✏️', 'error');
      return;
    }
    send.disabled = true;
    send.textContent = 'Sending…';
    canvas.toBlob(blob => {
      if (!blob) {
        send.disabled = false;
        send.textContent = 'Send to Jay ♡';
        showActivityToast('Could not save that drawing. Please try again.', 'error');
        return;
      }
      const transfer = new DataTransfer();
      transfer.items.add(new File([blob], 'doodle.png', { type: 'image/png' }));
      input.files = transfer.files;
      form.submit();
    }, 'image/png');
  });
}

function initActivityToasts() {
  document.querySelectorAll('.activity-toast').forEach(toast => {
    const close = toast.querySelector('.toast-dismiss');
    let timeout = setTimeout(() => dismissToast(toast), 5200);
    close?.addEventListener('click', () => dismissToast(toast));
    toast.addEventListener('mouseenter', () => clearTimeout(timeout));
    toast.addEventListener('mouseleave', () => { timeout = setTimeout(() => dismissToast(toast), 1800); });
  });
}

function showActivityToast(message, type = 'success') {
  let stack = document.querySelector('.toast-stack');
  if (!stack) {
    stack = document.createElement('div');
    stack.className = 'toast-stack';
    stack.setAttribute('aria-live', 'polite');
    stack.setAttribute('aria-relevant', 'additions');
    document.body.appendChild(stack);
  }
  const toast = document.createElement('div');
  toast.className = `activity-toast toast-${type}`;
  toast.setAttribute('role', 'status');
  const mark = document.createElement('span');
  mark.className = 'toast-mark';
  mark.textContent = type === 'error' ? '×' : '✦';
  const content = document.createElement('span');
  content.textContent = message;
  const close = document.createElement('button');
  close.className = 'toast-dismiss';
  close.type = 'button';
  close.setAttribute('aria-label', 'Dismiss notification');
  close.textContent = '×';
  toast.append(mark, content, close);
  stack.appendChild(toast);
  close.addEventListener('click', () => dismissToast(toast));
  setTimeout(() => dismissToast(toast), 5200);
}

function dismissToast(toast) {
  if (!toast.isConnected) return;
  toast.classList.add('toast-leaving');
  setTimeout(() => toast.remove(), 220);
}

/* ==========================================================================
   1. Theme Management (Dark Mode)
   ========================================================================== */
function initTheme() {
  const toggleBtn = document.getElementById('theme-toggle-btn');
  const savedTheme = localStorage.getItem('our_space_theme_v2');
  const initialTheme = savedTheme || 'dark';

  applyTheme(initialTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      localStorage.setItem('our_space_theme_v2', next);
    });
  }
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const toggleBtn = document.getElementById('theme-toggle-btn');
  if (toggleBtn) {
    toggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
    toggleBtn.setAttribute('title', theme === 'dark' ? 'Switch to light mode' : 'Switch to cozy dark mode');
  }
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  if (themeMeta) themeMeta.content = theme === 'dark' ? '#180D18' : '#FFFBF7';
}

/* ==========================================================================
   2. Floating Hearts Particle Effect & Heart Tap API
   ========================================================================== */
function initHeartTap() {
  const heartBtn = document.getElementById('tap-heart-btn');
  if (!heartBtn) return;

  heartBtn.addEventListener('click', async (e) => {
    // 1. Button bounce effect
    heartBtn.style.transform = 'scale(0.92)';
    setTimeout(() => { heartBtn.style.transform = 'scale(1.08)'; }, 100);
    setTimeout(() => { heartBtn.style.transform = ''; }, 250);

    // 2. Trigger visual hearts explosion
    const rect = heartBtn.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    spawnHeartExplosion(x, y);

    // 3. Play subtle haptic feedback if mobile
    if (navigator.vibrate) {
      navigator.vibrate([50, 100, 50]);
    }

    // 4. Send tap to backend
    const csrfToken = getCsrfToken();
    try {
      const response = await fetch('/tap-heart/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      if (data.status === 'success') {
        showActivityToast(data.message || 'A little heart was sent 💕');
        const noteEl = document.getElementById('tap-status-note');
        if (noteEl) {
          noteEl.innerHTML = `<strong>Sent at ${data.time}!</strong> Jay will see a heart pop up 💕`;
          noteEl.style.color = 'var(--accent-pink)';
        }
      }
    } catch (err) {
      console.log('Tap recorded locally', err);
    }
  });
}

function spawnHeartExplosion(centerX, centerY) {
  const layer = document.getElementById('floating-hearts-layer') || createFloatingLayer();
  const emojis = ['💖', '💕', '🌸', '✨', '💗', '🥰', '💌', '🌹', '💞'];
  const count = 24;

  for (let i = 0; i < count; i++) {
    const heart = document.createElement('div');
    heart.className = 'particle-heart';
    heart.textContent = emojis[Math.floor(Math.random() * emojis.length)];

    // Random spread around tap
    const angle = Math.random() * Math.PI * 2;
    const distance = 30 + Math.random() * 120;
    const startX = centerX + Math.cos(angle) * (15 + Math.random() * 40);
    const startY = centerY + Math.sin(angle) * (15 + Math.random() * 30);

    heart.style.left = `${startX}px`;
    heart.style.top = `${startY}px`;
    heart.style.fontSize = `${1.2 + Math.random() * 1.5}rem`;
    heart.style.animationDuration = `${1.5 + Math.random() * 1.2}s`;

    layer.appendChild(heart);

    setTimeout(() => {
      heart.remove();
    }, 2500);
  }
}

function createFloatingLayer() {
  const layer = document.createElement('div');
  layer.id = 'floating-hearts-layer';
  layer.className = 'floating-hearts-layer';
  document.body.appendChild(layer);
  return layer;
}

/* ==========================================================================
   3. Emoji Selector for Daily Check-in
   ========================================================================== */
function initEmojiSelector() {
  const pills = document.querySelectorAll('.emoji-pill');
  const hiddenInput = document.getElementById('id_mood_emoji');
  if (!pills.length || !hiddenInput) return;

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('selected'));
      pill.classList.add('selected');
      hiddenInput.value = pill.getAttribute('data-emoji');
      
      // Spawn mini sparkle
      const rect = pill.getBoundingClientRect();
      spawnHeartExplosion(rect.left + rect.width / 2, rect.top + rect.height / 2);
    });
  });
}

/* ==========================================================================
   4. AJAX Check-in Form (No Page Reload)
   ========================================================================== */
function initAjaxCheckin() {
  const form = document.getElementById('checkin-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('checkin-submit-btn');
    const noteInput = document.getElementById('checkin-note-input');
    const moodInput = document.getElementById('id_mood_emoji');
    const originalText = btn.textContent;

    btn.textContent = 'Saving... ✨';
    btn.disabled = true;

    const formData = new FormData(form);
    const csrfToken = getCsrfToken();

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken,
        },
        body: formData
      });

      if (response.ok) {
        showActivityToast(`Check-in shared ${moodInput.value} · “${noteInput.value}”`);
        btn.textContent = 'Saved! 🥰';
        const rect = btn.getBoundingClientRect();
        spawnHeartExplosion(rect.left + rect.width / 2, rect.top + rect.height / 2);
        setTimeout(() => {
          btn.textContent = 'Update 💕';
          btn.disabled = false;
        }, 1500);
      } else {
        form.submit(); // Fallback to standard post
      }
    } catch (err) {
      form.submit();
    }
  });
}

/* ==========================================================================
   5. Interactive This or That Voting (No Page Reload)
   ========================================================================== */
function initAjaxThisOrThat() {
  document.querySelectorAll('form[action*="this-or-that"]').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const choiceBtn = form.querySelector('.choice-btn');
      const card = form.closest('.card');
      const formData = new FormData(form);
      const csrfToken = getCsrfToken();

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
          },
          body: formData
        });

        const data = await response.json();
        if (data.status === 'success') {
          showActivityToast(data.message || 'Your choice is saved ✨');
          // Highlight selection
          card.querySelectorAll('.choice-btn').forEach(b => b.classList.remove('selected'));
          choiceBtn.classList.add('selected');

          // Burst effect
          const rect = choiceBtn.getBoundingClientRect();
          spawnHeartExplosion(rect.left + rect.width / 2, rect.top + rect.height / 2);

          // Full reload after short delay if status changed so partner picks update
          setTimeout(() => {
            window.location.reload();
          }, 800);
        }
      } catch (err) {
        form.submit();
      }
    });
  });
}

/* ==========================================================================
   6. Modals (Settings & Profile)
   ========================================================================== */
function initModals() {
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.getAttribute('data-modal-open');
      const modal = document.getElementById(targetId);
      if (modal) modal.classList.add('open');
    });
  });

  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const modal = btn.closest('.modal-overlay');
      if (modal) modal.classList.remove('open');
    });
  });

  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('open');
    });
  });
}

/* ==========================================================================
   7. Dismiss Heart Tap Banner
   ========================================================================== */
function initDismissBanner() {
  const dismissBtn = document.getElementById('dismiss-tap-btn');
  if (!dismissBtn) return;

  dismissBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    const banner = dismissBtn.closest('.notification-banner');
    const tapId = dismissBtn.getAttribute('data-tap-id');
    const csrfToken = getCsrfToken();

    if (banner) {
      banner.style.opacity = '0';
      banner.style.transform = 'translateY(-10px)';
      banner.style.transition = 'all 0.3s ease';
      setTimeout(() => banner.remove(), 300);
    }

    if (tapId) {
      try {
        await fetch(`/dismiss-tap/${tapId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
          }
        });
      } catch (err) {
        console.error(err);
      }
    }
  });
}

/* ==========================================================================
   8. Live Clocks (Ticks in real-time)
   ========================================================================== */
function initLiveClocks() {
  const clockEls = document.querySelectorAll('[data-timezone]');
  if (!clockEls.length) return;

  function updateClocks() {
    clockEls.forEach(el => {
      const tz = el.getAttribute('data-timezone');
      try {
        const now = new Date();
        const formatter = new Intl.DateTimeFormat('en-US', {
          timeZone: tz,
          hour: 'numeric',
          minute: '2-digit',
          hour12: true,
        });
        el.textContent = formatter.format(now);
      } catch (e) {
        // Fallback to existing text
      }
    });
  }

  updateClocks();
  setInterval(updateClocks, 10000);
}

/* ==========================================================================
   Utility: Extract CSRF Token
   ========================================================================== */
function getCsrfToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  if (cookieValue) return cookieValue;

  const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
  return csrfInput ? csrfInput.value : '';
}
