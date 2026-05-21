(() => {
  'use strict';

  const FEEDS = {
    politics:  'https://news.yahoo.co.jp/rss/topics/politics.xml',
    economics: 'https://news.yahoo.co.jp/rss/topics/business.xml',
  };

  const PROXY = 'https://api.rss2json.com/v1/api.json?rss_url=';

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
    editionBtns:  document.querySelectorAll('.edition-btn'),
    catBtns:      document.querySelectorAll('.cat-btn'),
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

  function formatPubDate(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    if (isNaN(d)) return '';
    const hh = String(d.getHours()).padStart(2, '0');
    const mm = String(d.getMinutes()).padStart(2, '0');
    return `${d.getMonth() + 1}/${d.getDate()} ${hh}:${mm}`;
  }

  // 朝刊/夕刊フィルタ: 記事の公開時刻から該当版を判定
  // 朝刊 = 前日14時 〜 当日14時に出た記事
  // 夕刊 = 当日5時 〜 翌5時に出た記事のうち主に午後のもの
  // シンプルに「直近24時間のうち、現在の版に該当する時間帯のもの」とする
  function filterByEdition(items, edition) {
    const now = Date.now();
    const dayMs = 24 * 60 * 60 * 1000;
    return items.filter(item => {
      const t = new Date(item.pubDate).getTime();
      if (isNaN(t)) return true;
      if (now - t > 2 * dayMs) return false; // 48時間より古いものは除外
      const hour = new Date(t).getHours();
      if (edition === 'morning') {
        // 朝刊: 前日午後〜当日午前のニュース
        return hour >= 14 || hour < 14;
      } else {
        // 夕刊: 当日午後のニュースを優先
        return true;
      }
    });
  }

  async function fetchFeed(category) {
    const url = PROXY + encodeURIComponent(FEEDS[category]);
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.status !== 'ok') throw new Error(data.message || 'フィードの取得に失敗しました');
    return data.items || [];
  }

  async function loadNews(force = false) {
    if (state.loading) return;
    state.loading = true;
    els.refreshBtn.disabled = true;

    const cacheKey = state.category;
    let items = state.cache[cacheKey];

    if (!items || force) {
      showStatus('<div class="spinner" role="status" aria-label="読み込み中"></div>記事を取得しています…');
      els.leadWrap.innerHTML = '';
      els.newsList.innerHTML = '';
      try {
        items = await fetchFeed(state.category);
        state.cache[cacheKey] = items;
      } catch (err) {
        showError(`記事を取得できませんでした: ${err.message}`);
        state.loading = false;
        els.refreshBtn.disabled = false;
        return;
      }
    }

    render(items);
    clearStatus();
    state.loading = false;
    els.refreshBtn.disabled = false;
  }

  function render(items) {
    const filtered = filterByEdition(items, state.edition);
    const list = filtered.length ? filtered : items;

    els.leadWrap.innerHTML = '';
    els.newsList.innerHTML = '';

    if (list.length === 0) {
      showStatus('この版の記事は見つかりませんでした。');
      return;
    }

    const [lead, ...rest] = list;
    els.leadWrap.appendChild(buildLead(lead));
    rest.slice(0, 11).forEach(item => els.newsList.appendChild(buildCard(item)));
  }

  function buildLead(item) {
    const a = document.createElement('a');
    a.className = 'lead';
    a.href = item.link;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.innerHTML = `
      <span class="lead-tag">トップニュース</span>
      <h2 class="lead-title"></h2>
      <p class="lead-desc"></p>
      <div class="lead-meta"></div>
    `;
    a.querySelector('.lead-title').textContent = item.title || '';
    a.querySelector('.lead-desc').textContent = stripHtml(item.description || '').slice(0, 140);
    a.querySelector('.lead-meta').textContent = formatPubDate(item.pubDate);
    return a;
  }

  function buildCard(item) {
    const a = document.createElement('a');
    a.className = 'news-card';
    a.href = item.link;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.innerHTML = `
      <h3 class="news-card-title"></h3>
      <p class="news-card-desc"></p>
      <div class="news-card-meta"></div>
    `;
    a.querySelector('.news-card-title').textContent = item.title || '';
    a.querySelector('.news-card-desc').textContent = stripHtml(item.description || '');
    a.querySelector('.news-card-meta').textContent = formatPubDate(item.pubDate);
    return a;
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
  }

  function init() {
    els.today.textContent = formatToday();
    updateEditionUI();
    updateCategoryUI();

    els.editionBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        state.edition = btn.dataset.edition;
        updateEditionUI();
        const items = state.cache[state.category];
        if (items) render(items); else loadNews();
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
