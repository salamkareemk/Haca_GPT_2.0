/* app.js — HACA GPT 2.0 */

const API_BASE = '';

const messagesArea    = document.getElementById('messagesArea');
const messageInput    = document.getElementById('messageInput');
const sendBtn         = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const charCount       = document.getElementById('charCount');
const clearBtn        = document.getElementById('clearBtn');
const menuBtn         = document.getElementById('menuBtn');
const sidebar         = document.getElementById('sidebar');
const sidebarOverlay  = document.getElementById('sidebarOverlay');
const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
const welcomeCard     = document.getElementById('welcomeCard');
const statusPill      = document.getElementById('statusPill');
const statusText      = document.getElementById('statusText');
const headerSub       = document.getElementById('headerSub');
const docsCount       = document.getElementById('docsCount');

let isLoading = false;
let conversationHistory = [];

document.addEventListener('DOMContentLoaded', () => {
  checkHealth();
  bindEvents();
  messageInput.focus();
});

function bindEvents() {
  sendBtn.addEventListener('click', handleSend);

  messageInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled) handleSend();
    }
  });

  messageInput.addEventListener('input', () => {
    const len = messageInput.value.length;
    charCount.textContent = `${len} / 1000`;
    sendBtn.disabled = len === 0 || isLoading;
    autoResize(messageInput);
  });

  clearBtn.addEventListener('click', clearChat);

  // Sidebar toggle
  menuBtn.addEventListener('click', openSidebar);
  sidebarCloseBtn.addEventListener('click', closeSidebar);
  sidebarOverlay.addEventListener('click', closeSidebar);

  // Quick buttons
  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      sendMessage(btn.dataset.q);
      closeSidebar();
    });
  });

  // Starter chips
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => sendMessage(chip.dataset.q));
  });
}

function openSidebar() {
  sidebar.classList.add('open');
  sidebarOverlay.classList.add('active');
}
function closeSidebar() {
  sidebar.classList.remove('open');
  sidebarOverlay.classList.remove('active');
}

async function checkHealth() {
  try {
    const res  = await fetch(`${API_BASE}/api/health`);
    const data = await res.json();
    if (data.status === 'ok') {
      statusPill.querySelector('.status-dot').classList.add('online');
      statusText.textContent = 'Online';
      docsCount.textContent  = data.documents_indexed;
      headerSub.textContent  = data.llm_available ? '● GPT-4o-mini connected' : '● Mock mode active';
      headerSub.style.color  = data.llm_available ? '#22c55e' : '#f59e0b';
    }
  } catch {
    statusText.textContent = 'Offline';
    headerSub.textContent  = '● Server not reachable';
    headerSub.style.color  = '#ef4444';
  }
}

function handleSend() {
  const text = messageInput.value.trim();
  if (!text || isLoading) return;
  sendMessage(text);
}

async function sendMessage(text) {
  if (!text || isLoading) return;

  if (welcomeCard && welcomeCard.parentNode) {
    welcomeCard.style.opacity = '0';
    welcomeCard.style.transition = 'opacity .25s';
    setTimeout(() => welcomeCard.remove(), 250);
  }

  messageInput.value = '';
  charCount.textContent = '0 / 1000';
  sendBtn.disabled = true;
  autoResize(messageInput);

  appendUserMessage(text);
  conversationHistory.push({ role: 'user', content: text });
  setLoading(true);

  try {
    const res  = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || `Server error ${res.status}`);

    setLoading(false);
    appendAIMessage(
      data.answer     || 'Sorry, I could not generate a response.',
      data.sources    || [],
      data.confidence || 0,
      data.follow_ups || []
    );
    conversationHistory.push({ role: 'assistant', content: data.answer });

  } catch (err) {
    setLoading(false);
    appendAIMessage(
      `⚠️ **Connection Error**\n\nI couldn't reach the server. Make sure the HACA GPT server is running.\n\n*${err.message}*`,
      [], 0, []
    );
  }

  messageInput.focus();
}

function appendUserMessage(text) {
  const row = document.createElement('div');
  row.className = 'message-row user';

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = '👤';

  const content = document.createElement('div');
  content.className = 'msg-content';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.textContent = text;

  content.appendChild(bubble);
  row.appendChild(avatar);
  row.appendChild(content);
  messagesArea.appendChild(row);
  scrollToBottom();
}

function appendAIMessage(answer, sources, confidence, followUps) {
  const row = document.createElement('div');
  row.className = 'message-row ai';

  // Avatar
  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.innerHTML = `<svg viewBox="0 0 24 24" fill="none"><path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor" opacity=".9"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>`;

  const content = document.createElement('div');
  content.className = 'msg-content';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.innerHTML = renderMarkdown(answer);

  // Meta
  const meta = document.createElement('div');
  meta.className = 'msg-meta';

  if (confidence > 0) {
    const conf = document.createElement('div');
    conf.className = 'confidence-bar-wrap';
    conf.innerHTML = `<div class="conf-track"><div class="conf-fill" style="width:0%"></div></div><span>${Math.round(confidence * 100)}% match</span>`;
    meta.appendChild(conf);
    setTimeout(() => {
      conf.querySelector('.conf-fill').style.width = Math.round(confidence * 100) + '%';
    }, 120);
  }

  if (sources.length > 0) {
    const badgeWrap = document.createElement('div');
    badgeWrap.className = 'source-badges';
    [...new Set(sources)].forEach(src => {
      const badge = document.createElement('span');
      badge.className = 'source-badge';
      badge.textContent = '📄 ' + src.replace(/\.(txt|md|csv)$/i, '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      badgeWrap.appendChild(badge);
    });
    meta.appendChild(badgeWrap);
  }

  const copyBtn = document.createElement('button');
  copyBtn.className = 'copy-btn';
  copyBtn.textContent = '📋 Copy';
  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(answer).then(() => {
      copyBtn.textContent = '✅ Copied!';
      copyBtn.classList.add('copied');
      setTimeout(() => { copyBtn.textContent = '📋 Copy'; copyBtn.classList.remove('copied'); }, 2000);
    });
  });
  meta.appendChild(copyBtn);

  content.appendChild(bubble);
  content.appendChild(meta);

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

  // Fade-in reveal
  bubble.style.opacity = '0';
  setTimeout(() => { bubble.style.transition = 'opacity .4s ease'; bubble.style.opacity = '1'; }, 60);

  scrollToBottom();
}

function renderMarkdown(text) {
  if (typeof marked !== 'undefined') {
    marked.setOptions({ breaks: true, gfm: true });
    return marked.parse(text);
  }
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>').replace(/\n/g, '<br>');
}

function setLoading(loading) {
  isLoading = loading;
  typingIndicator.style.display = loading ? 'flex' : 'none';
  sendBtn.disabled = loading;
  if (loading) scrollToBottom();
}

function clearChat() {
  conversationHistory = [];
  messagesArea.innerHTML = `
    <div class="welcome-screen" id="welcomeCard">
      <div class="welcome-glow" aria-hidden="true"></div>
      <div class="welcome-icon-wrap">
        <div class="welcome-icon-ring"></div>
        <div class="welcome-icon">
          <svg viewBox="0 0 24 24" fill="none"><path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor" opacity=".9"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        </div>
      </div>
      <h1 class="welcome-title">Welcome to <span class="gradient-text">HACA GPT</span></h1>
      <p class="welcome-sub">Your intelligent AI guide to <strong>Haris &amp; Co Academy</strong>. Ask me anything — courses, fees, faculty, batches, placements, or admissions.</p>
      <div class="starter-chips">
        <button class="chip" data-q="What are the top courses at HACA?">🎓 Top Courses</button>
        <button class="chip" data-q="What is the fee for data science course?">💰 Data Science Fees</button>
        <button class="chip" data-q="Tell me about HACA's placement record">🚀 Placement Record</button>
        <button class="chip" data-q="What makes HACA different from other institutes?">⭐ Why HACA?</button>
        <button class="chip" data-q="Are there any online courses available?">💻 Online Courses</button>
        <button class="chip" data-q="When is the next batch starting?">📅 Next Batch</button>
      </div>
    </div>`;
  messagesArea.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => sendMessage(chip.dataset.q));
  });
  messageInput.value = '';
  charCount.textContent = '0 / 1000';
  sendBtn.disabled = true;
  messageInput.focus();
}

function scrollToBottom() {
  setTimeout(() => {
    messagesArea.scrollTo({ top: messagesArea.scrollHeight, behavior: 'smooth' });
  }, 50);
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 130) + 'px';
}
