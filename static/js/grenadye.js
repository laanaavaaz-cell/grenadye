// ─── CSRF ─────────────────────────────────────────────────────
function getCookie(name) {
  let val = null;
  document.cookie.split(';').forEach(c => {
    c = c.trim();
    if (c.startsWith(name + '=')) val = decodeURIComponent(c.slice(name.length + 1));
  });
  return val;
}

function csrfFetch(url, opts = {}) {
  opts.headers = { 'X-CSRFToken': getCookie('csrftoken'), ...(opts.headers || {}) };
  opts.credentials = 'same-origin';
  return fetch(url, opts);
}

// ─── MODAL ────────────────────────────────────────────────────
function openPostModal() {
  const modal = document.getElementById('postModal');
  if (modal) {
    modal.classList.add('open');
    const ta = document.getElementById('modal-content');
    if (ta) setTimeout(() => ta.focus(), 100);
  }
}

function closePostModal(e) {
  const modal = document.getElementById('postModal');
  if (!modal) return;
  if (!e || e.target === modal) {
    modal.classList.remove('open');
  }
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closePostModal();
});

// ─── CHAR COUNT ───────────────────────────────────────────────
function updateCharCount(el, counterId, btnId, max) {
  const len = el.value.length;
  const counter = document.getElementById(counterId);
  const btn = document.getElementById(btnId);
  if (counter) {
    counter.textContent = len + '/' + max;
    counter.style.color = len > max * 0.9 ? (len > max ? '#ff4444' : '#ffd400') : '#71767b';
  }
  if (btn) btn.disabled = len === 0 || len > max;
}

// ─── IMAGE PREVIEW ────────────────────────────────────────────
function previewImage(input, previewWrapperId, isReplace) {
  const wrap = document.getElementById(previewWrapperId);
  if (!wrap) return;
  if (input.files && input.files[0]) {
    const url = URL.createObjectURL(input.files[0]);
    if (isReplace) {
      // Replace existing img or placeholder
      let img = wrap.querySelector('img');
      if (!img) {
        img = document.createElement('img');
        img.style.cssText = 'width:100%;height:100%;object-fit:cover;';
        wrap.innerHTML = '';
        wrap.appendChild(img);
      }
      img.src = url;
    } else {
      wrap.innerHTML = `<img src="${url}" style="border-radius:12px;max-height:220px;object-fit:cover;width:100%;" />`;
    }
    // Enable submit if disabled
    const form = input.closest('form');
    if (form) {
      const btn = form.querySelector('.post-btn');
      if (btn) btn.disabled = false;
    }
  }
}

// ─── LIKE POST ────────────────────────────────────────────────
function likePost(postId, btn) {
  csrfFetch(`/post/${postId}/like/`, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      const icon = btn.querySelector('i');
      const count = btn.querySelector('span');
      btn.classList.toggle('liked', data.liked);
      if (icon) icon.className = data.liked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
      if (count) count.textContent = data.likes_count;
    })
    .catch(() => showToast('Error — please try again', 'error'));
}

// ─── LIKE COMMENT ─────────────────────────────────────────────
function likeComment(commentId, btn) {
  csrfFetch(`/comment/${commentId}/like/`, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      const icon = btn.querySelector('i');
      const count = btn.querySelector('span');
      btn.classList.toggle('liked', data.liked);
      if (icon) icon.className = data.liked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
      if (count) count.textContent = data.likes_count;
    })
    .catch(() => showToast('Error — please try again', 'error'));
}

// ─── DELETE POST ──────────────────────────────────────────────
function deletePost(postId, btn) {
  if (!confirm('Delete this post?')) return;
  csrfFetch(`/post/${postId}/delete/`, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.deleted) {
        const card = document.querySelector(`.post-card[data-post-id="${postId}"]`);
        if (card) {
          card.style.transition = 'opacity .3s, transform .3s';
          card.style.opacity = '0';
          card.style.transform = 'translateX(-10px)';
          setTimeout(() => card.remove(), 300);
          showToast('Post deleted');
        } else {
          window.location.href = '/';
        }
      }
    })
    .catch(() => showToast('Error — please try again', 'error'));
}

// ─── FOLLOW ───────────────────────────────────────────────────
function followUser(btn) {
  const username = btn.dataset.username;
  csrfFetch(`/user/${username}/follow/`, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      btn.classList.toggle('following', data.following);
      btn.textContent = data.following ? 'Following' : 'Follow';
      showToast(data.following ? `Following @${username}` : `Unfollowed @${username}`);
    })
    .catch(() => showToast('Error', 'error'));
}

// ─── TOGGLE MENU ──────────────────────────────────────────────
function toggleMenu(btn) {
  const menu = btn.nextElementSibling;
  if (!menu) return;
  menu.classList.toggle('hidden');
  const close = (e) => {
    if (!menu.contains(e.target) && e.target !== btn) {
      menu.classList.add('hidden');
      document.removeEventListener('click', close);
    }
  };
  setTimeout(() => document.addEventListener('click', close), 0);
}

// ─── SHARE ────────────────────────────────────────────────────
function sharePost(postId) {
  const url = `${window.location.origin}/post/${postId}/`;
  if (navigator.share) {
    navigator.share({ title: 'Check this post on Grenadye', url });
  } else {
    navigator.clipboard.writeText(url).then(() => showToast('Link copied!'));
  }
}

// ─── TOAST ───────────────────────────────────────────────────
function showToast(msg, type = 'info') {
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  if (type === 'error') t.style.background = '#ff4444';
  document.body.appendChild(t);
  setTimeout(() => {
    t.style.transition = 'opacity .3s';
    t.style.opacity = '0';
    setTimeout(() => t.remove(), 300);
  }, 2500);
}

// ─── NOTIFICATION POLLING ─────────────────────────────────────
function pollNotifications() {
  fetch('/api/notifications/count/')
    .then(r => r.json())
    .then(data => {
      const badge = document.getElementById('notif-badge');
      const dot = document.getElementById('notif-dot');
      if (badge) {
        badge.textContent = data.count;
        badge.style.display = data.count > 0 ? 'inline-flex' : 'none';
      }
      if (dot) dot.style.display = data.count > 0 ? 'block' : 'none';
    }).catch(() => {});
}

// Start polling if logged in
if (document.querySelector('.bottom-nav') || document.querySelector('.sidebar')) {
  pollNotifications();
  setInterval(pollNotifications, 30000);
}

// ─── COMPOSE AUTO-GROW ────────────────────────────────────────
document.addEventListener('input', e => {
  if (e.target.matches('textarea')) {
    e.target.style.height = 'auto';
    e.target.style.height = e.target.scrollHeight + 'px';
  }
});
