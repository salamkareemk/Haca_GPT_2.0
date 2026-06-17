/* ─── app.js — HACA GPT 2.0 Chat Logic ──────────────────────────────────── */

const API_BASE = '';  // Same origin — Flask serves both frontend and API

// ── DOM refs ──────────────────────────────────────────────────────────────────
const messagesArea   = document.getElementById('messagesArea');
const messageInput   = document.getElementById('messageInput');
const sendBtn        = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const charCount      = document.getElementById('charCount');
const clearBtn       = document.getElementById('clearBtn');
const menuBtn        = document.getElementById('menuBtn');
const sidebar        = document.getElementById('sidebar');
const welcomeCard    = document.getElementById('welcomeCard');

// ── State ─────────────────────────────────────────────────────────────────────
let isLoading = false;
let conversationHistory = [];

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  checkHealth();
  bindEvents();
  messageInput.focus();
});

// ── Event Bindings ────────────────────────────────────────────────────────────
function bindEvents() {
  // Send on button click
  sendBtn.addEventListener('click', handleSend);

  // Send on Enter (Shift+Enter = newline)
  messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled) handleSend();
    }
  });

  // Character count + button enable
  messageInput.addEventListener('input', () => {
    const len = messageInput.value.length;
    charCount.textContent = `${len} / 1000`;
    sendBtn.disabled = len === 0 || isLoading;
    autoResize(messageInput);
  });

  // Clear chat
  clearBtn.addEventListener('click', clearChat);

  // Sidebar toggle (mobile)
  menuBtn.addEventListener('click', () => sidebar.classList.toggle('open'));
  document.addEventListener('click', (e) => {
    if (sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) && e.target !== menuBtn) {
      sidebar.classList.remove('open');
    }
  });

  // Quick buttons in sidebar
  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      sendMessage(btn.dataset.q);
      sidebar.classList.remove('open');
    });
  });

  // Starter chips on welcome card
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => sendMessage(chip.dataset.q));
  });
}

// ── Health Check ──────────────────────────────────────────────────────────────
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    const data = await res.json();
    const badge = document.getElementById('modelBadge');
    if (data.status === 'ok') {
      badge.textContent = `⚡ ${data.documents_indexed} docs indexed`;
      badge.style.color = 'var(--gold)';
    }
  } catch {
    /* silent fail */
  }
}

// ── Handle Send ───────────────────────────────────────────────────────────────
function handleSend() {
  const text = messageInput.value.trim();
  if (!text || isLoading) return;
  sendMessage(text);
}

async function sendMessage(text) {
  if (!text || isLoading) return;

  // Hide welcome card on first message
  if (welcomeCard && welcomeCard.parentNode) {
    welcomeCard.style.animation = 'fadeUp .3s ease reverse';
    setTimeout(() => welcomeCard.remove(), 250);
  }

  // Reset input
  messageInput.value = '';
  charCount.textContent = '0 / 1000';
  sendBtn.disabled = true;
  autoResize(messageInput);

  // Add user message
  appendMessage('user', text);
  conversationHistory.push({ role: 'user', content: text });

  // Show typing indicator
  setLoading(true);

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || `Server error ${res.status}`);
    }

    setLoading(false);

    const answer = data.answer || 'Sorry, I could not generate a response.';
    const sources = data.sources || [];
    const confidence = data.confidence || 0;
    const followUps = data.follow_ups || [];

    appendAIMessage(answer, sources, confidence, followUps);
    conversationHistory.push({ role: 'assistant', content: answer });

  } catch (err) {
    setLoading(false);
    appendAIMessage(
      `⚠️ **Connection Error**\n\nI couldn't reach the server. Please make sure the HACA GPT server is running.\n\n*Error: ${err.message}*`,
      [], 0, []
    );
  }

  messageInput.focus();
}

// ── Append User Message ───────────────────────────────────────────────────────
function appendMessage(role, text) {
  const row = document.createElement('div');
  row.className = `message-row ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = role === 'user' ? '👤' : '🤖';

  const content = document.createElement('div');
  content.className = 'msg-content';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.textContent = text;  // user text is plain

  content.appendChild(bubble);
  row.appendChild(avatar);
  row.appendChild(content);
  messagesArea.appendChild(row);
  scrollToBottom();
}

// ── Append AI Message ─────────────────────────────────────────────────────────
function appendAIMessage(answer, sources, confidence, followUps) {
  const row = document.createElement('div');
  row.className = 'message-row ai';

  // Avatar
  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = '🤖';

  // Content container
  const content = document.createElement('div');
  content.className = 'msg-content';

  // Bubble with markdown
  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.innerHTML = renderMarkdown(answer);

  // Meta row
  const meta = document.createElement('div');
  meta.className = 'msg-meta';

  // Confidence meter
  if (confidence > 0) {
    const confWrap = document.createElement('div');
    confWrap.className = 'confidence-bar-wrap';
    confWrap.innerHTML = `
      <div class="conf-track">
        <div class="conf-fill" style="width:${Math.round(confidence * 100)}%"></div>
      </div>
      <span>${Math.round(confidence * 100)}% confidence</span>`;
    meta.appendChild(confWrap);
  }

  // Source badges
  if (sources.length > 0) {
    const badgeWrap = document.createElement('div');
    badgeWrap.className = 'source-badges';
    sources.forEach(src => {
      const badge = document.createElement('span');
      badge.className = 'source-badge';
      // Clean display name
      badge.textContent = '📄 ' + src.replace(/\.(txt|md|csv)$/i, '')
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
      badgeWrap.appendChild(badge);
    });
    meta.appendChild(badgeWrap);
  }

  // Copy button
  const copyBtn = document.createElement('button');
  copyBtn.className = 'copy-btn';
  copyBtn.textContent = '📋 Copy';
  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(answer).then(() => {
      copyBtn.textContent = '✅ Copied!';
      copyBtn.classList.add('copied');
      setTimeout(() => {
        copyBtn.textContent = '📋 Copy';
        copyBtn.classList.remove('copied');
      }, 2000);
    });
  });
  meta.appendChild(copyBtn);

  content.appendChild(bubble);
  content.appendChild(meta);

  // Follow-up chips
  if (followUps.length > 0) {
    const followArea = document.createElement('div');
    followArea.className = 'follow-up-area';
    followUps.forEach(q => {
      const chip = document.createElement('button');
      chip.className = 'follow-chip';
      chip.textContent = '💬 ' + q;
      chip.addEventListener('click', () => sendMessage(q));
      followArea.appendChild(chip);
    });
    content.appendChild(followArea);
  }

  row.appendChild(avatar);
  row.appendChild(content);
  messagesArea.appendChild(row);

  // Typewriter reveal
  typewriterReveal(bubble);

  scrollToBottom();
}

// ── Typewriter Effect ─────────────────────────────────────────────────────────
function typewriterReveal(element) {
  element.style.opacity = '0';
  // Short delay then fade in smoothly
  setTimeout(() => {
    element.style.transition = 'opacity 0.4s ease';
    element.style.opacity = '1';
  }, 80);
}

// ── Markdown Rendering ────────────────────────────────────────────────────────
function renderMarkdown(text) {
  if (typeof marked !== 'undefined') {
    marked.setOptions({ breaks: true, gfm: true });
    return marked.parse(text);
  }
  // Fallback: basic formatting
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

// ── Loading State ─────────────────────────────────────────────────────────────
function setLoading(loading) {
  isLoading = loading;
  typingIndicator.style.display = loading ? 'flex' : 'none';
  sendBtn.disabled = loading;
  if (loading) scrollToBottom();
}

// ── Clear Chat ────────────────────────────────────────────────────────────────
function clearChat() {
  conversationHistory = [];
  // Remove all messages except re-add welcome card
  messagesArea.innerHTML = `
    <div class="welcome-card" id="welcomeCard">
      <div class="welcome-icon">🤖</div>
      <h2>Welcome to HACA GPT</h2>
      <p>Your intelligent guide to everything at <strong>Haris &amp; Co Academy</strong>. Ask me about courses, fees, faculty, batches, placements, or admissions.</p>
      <div class="starter-chips">
        <button class="chip" data-q="What are the top courses at HACA?">Top Courses</button>
        <button class="chip" data-q="What is the fee for data science course?">Data Science Fees</button>
        <button class="chip" data-q="Tell me about HACA's placement record">Placement Record</button>
        <button class="chip" data-q="What makes HACA different from other institutes?">Why HACA?</button>
      </div>
    </div>`;
  // Re-bind chips
  messagesArea.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => sendMessage(chip.dataset.q));
  });
  messageInput.value = '';
  charCount.textContent = '0 / 1000';
  sendBtn.disabled = true;
  messageInput.focus();
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function scrollToBottom() {
  setTimeout(() => {
    messagesArea.scrollTo({ top: messagesArea.scrollHeight, behavior: 'smooth' });
  }, 50);
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 130) + 'px';
}
