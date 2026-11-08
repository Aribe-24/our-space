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
});

/* ==========================================================================
   1. Theme Management (Dark Mode)
   ========================================================================== */
function initTheme() {
  const toggleBtn = document.getElementById('theme-toggle-btn');
  const savedTheme = localStorage.getItem('our_space_theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');

  applyTheme(initialTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      localStorage.setItem('our_space_theme', next);
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
