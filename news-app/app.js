(() => {
  'use strict';

  // 静的JSONを読み込む（ビルド時にGitHub Actionsが生成）
  const DATA_URL = category => `./data/${category}.json`;

  const state = {
    category: 'politics',
    edition: detectEdition(),
    cache: {},
    loading: false,
  };

  const els = {
    today:        document.getElementById('today'),
    editionBadge: document.getElementById('edition-badge'),
    leadWrap:     document.getElementById('lead-wrap'),
    newsList:     document.getElementById('news-list'),
    status:       document.getElementById('status'),
    refreshBtn:   document.getElementById('refresh-btn'),
    sourceNote:   document.getElementById('source-note'),
    editionBtns:  document.querySelectorAll('.edition-btn'),
    catBtns:      document.querySelectorAll('.cat-btn'),
  };

  const SOURCE_NOTES = {
    politics:  '出典: Google ニュース（共同通信・時事通信・ロイター・産経・東京新聞ほかの無料記事を集約）',
    economics: '出典: Google ニュース（共同通信・時事通信・ロイター・産経・東京新聞ほかの無料記事を集約）',
    ai:        '出典: Anthropic / OpenAI / Google AI / Hugging Face / MIT News / arXiv / ITmedia AI+ / Ledge.ai',
  };

  function detectEdition() {
    const h = new Date().getHours();
    return (h >= 5 && h < 14) ? 'morning' : 'evening';
  }

  function formatToday() {
    const d = new Date();
    const days = ['日', '月', '火', '水', '木', '金', '土'];
    return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日（${days[d.getDay()]}）`;
  }

  function pubTime(item) {
    if (item && typeof item.pubTimestamp === 'number' && item.pubTimestamp > 0) {
      return item.pubTimestamp * 1000;
    }
    const t = new Date(item && item.pubDate).getTime();
    return isNaN(t) ? 0 : t;
  }

  function formatAbsolute(ms) {
    if (!ms) return '';
    const d = new Date(ms);
    const hh = String(d.getHours()).padStart(2, '0');
    const mm = String(d.getMinutes()).padStart(2, '0');
    return `${d.getMonth() + 1}/${d.getDate()} ${hh}:${mm}`;
  }

  // 相対時刻表記。直近のものは「N分前」「N時間前」、24h超は絶対時刻
  function formatRelative(ms) {
    if (!ms) return '';
    const diff = Date.now() - ms;
    const min = 60 * 1000, hour = 60 * min, day = 24 * hour;
    if (diff < 0) return 'まもなく';
    if (diff < min) return 'たった今';
    if (diff < hour) return `${Math.floor(diff / min)}分前`;
    if (diff < day) return `${Math.floor(diff / hour)}時間前`;
    return formatAbsolute(ms);
  }

  // 朝刊/夕刊フィルタ
  //   朝刊: 直近24時間のニュース（前日夕方〜当日朝までの動き）
  //   夕刊: 直近12時間のニュース（その日の動きにフォーカス）
  // 該当が3件未満なら全件にフォールバック（記事不足で空にならないように）
  function filterByEdition(items, edition) {
    const now = Date.now();
    const windowMs = edition === 'morning' ? 24 * 60 * 60 * 1000 : 12 * 60 * 60 * 1000;
    const filtered = items.filter(item => {
      const t = pubTime(item);
      return t > 0 && (now - t) <= windowMs;
    });
    return filtered.length >= 3 ? filtered : items;
  }

  async function fetchFeed(category) {
    const res = await fetch(DATA_URL(category), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { items: data.items || [], fetchedAt: data.fetched_at };
  }

  async function loadNews(force = false) {
    if (state.loading) return;
    state.loading = true;
    els.refreshBtn.disabled = true;

    const cacheKey = state.category;
    let cached = state.cache[cacheKey];

    if (!cached || force) {
      showStatus('<div class="spinner" role="status" aria-label="読み込み中"></div>記事を取得しています…');
      els.leadWrap.innerHTML = '';
      els.newsList.innerHTML = '';
      try {
        cached = await fetchFeed(state.category);
        state.cache[cacheKey] = cached;
      } catch (err) {
        showError(`記事を取得できませんでした: ${err.message}`);
        state.loading = false;
        els.refreshBtn.disabled = false;
        return;
      }
    }

    render(cached.items);
    showFetchedAt(cached.fetchedAt);
    state.loading = false;
    els.refreshBtn.disabled = false;
  }

  function showFetchedAt(iso) {
    if (!iso) { clearStatus(); return; }
    const ms = new Date(iso).getTime();
    if (!ms || ms < 946684800000) { clearStatus(); return; } // 2000年以前は無効値とみなす
    els.status.className = 'status';
    els.status.textContent = `データ取得: ${formatRelative(ms)}（${formatAbsolute(ms)}）`;
  }

  function render(items) {
    const sorted = [...items].sort((a, b) => pubTime(b) - pubTime(a));
    const filtered = filterByEdition(sorted, state.edition);

    els.leadWrap.innerHTML = '';
    els.newsList.innerHTML = '';

    if (filtered.length === 0) {
      showStatus('この版の記事は見つかりませんでした。');
      return;
    }

    const maxCards = state.category === 'economics' ? 29 : 15;
    const [lead, ...rest] = filtered;
    els.leadWrap.appendChild(buildLead(lead));
    rest.slice(0, maxCards).forEach(item => els.newsList.appendChild(buildCard(item)));
  }

  function buildLead(item) {
    const { title, source } = splitTitle(item.title);
    const ms = pubTime(item);
    const a = document.createElement('a');
    a.className = 'lead';
    a.href = item.link;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.innerHTML = `
      <span class="lead-tag">トップニュース</span>
      <h2 class="lead-title"></h2>
      <div class="lead-meta">
        <span class="meta-time"></span>
        <span class="meta-sep">・</span>
        <span class="meta-source"></span>
      </div>
    `;
    a.querySelector('.lead-title').textContent = title;
    a.querySelector('.meta-time').textContent = ms ? `${formatRelative(ms)}（${formatAbsolute(ms)}）` : '';
    a.querySelector('.meta-source').textContent = source || item.sourceName || '';
    return a;
  }

  function buildCard(item) {
    const { title, source } = splitTitle(item.title);
    const ms = pubTime(item);
    const a = document.createElement('a');
    a.className = 'news-card';
    a.href = item.link;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.innerHTML = `
      <h3 class="news-card-title"></h3>
      <div class="news-card-meta">
        <span class="meta-time"></span>
        <span class="meta-sep">・</span>
        <span class="meta-source"></span>
      </div>
    `;
    a.querySelector('.news-card-title').textContent = title;
    a.querySelector('.meta-time').textContent = formatRelative(ms);
    a.querySelector('.meta-source').textContent = source || item.sourceName || '';
    return a;
  }

  // Google ニュースのタイトルは「記事見出し - 媒体名」形式なので分離する
  function splitTitle(raw) {
    if (!raw) return { title: '', source: '' };
    const idx = raw.lastIndexOf(' - ');
    if (idx === -1) return { title: raw, source: '' };
    return { title: raw.slice(0, idx).trim(), source: raw.slice(idx + 3).trim() };
  }

  function stripHtml(s) {
    const tmp = document.createElement('div');
    tmp.innerHTML = s;
    return (tmp.textContent || tmp.innerText || '').trim();
  }

  function showStatus(html) {
    els.status.className = 'status';
    els.status.innerHTML = html;
  }

  function showError(msg) {
    els.status.className = 'status error';
    els.status.textContent = msg;
  }

  function clearStatus() {
    els.status.className = 'status';
    els.status.innerHTML = '';
  }

  function updateEditionUI() {
    els.editionBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.edition === state.edition);
    });
    els.editionBadge.textContent = state.edition === 'morning' ? '朝刊' : '夕刊';
    els.editionBadge.className = `edition-badge ${state.edition}`;
  }

  function updateCategoryUI() {
    els.catBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.category === state.category);
    });
    if (els.sourceNote && SOURCE_NOTES[state.category]) {
      els.sourceNote.textContent = SOURCE_NOTES[state.category];
    }
  }

  function init() {
    els.today.textContent = formatToday();
    updateEditionUI();
    updateCategoryUI();

    els.editionBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        state.edition = btn.dataset.edition;
        updateEditionUI();
        const cached = state.cache[state.category];
        if (cached) { render(cached.items); showFetchedAt(cached.fetchedAt); }
        else loadNews();
      });
    });

    els.catBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        state.category = btn.dataset.category;
        updateCategoryUI();
        loadNews();
      });
    });

    els.refreshBtn.addEventListener('click', () => loadNews(true));

    loadNews();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
