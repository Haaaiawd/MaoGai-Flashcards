(function () {
  'use strict';

  const STORAGE_KEY = 'maogai-card-v1';
  const STATE = { KNOWN: 'known', FUZZY: 'fuzzy', UNKNOWN: 'unknown' };

  let mode = 'order';
  let list = [];
  let cursor = 0;
  let statusMap = load();
  let animating = false;

  const $ = (id) => document.getElementById(id);
  const dom = {
    statTotal: $('stat-total'),
    statKnown: $('stat-known'),
    statFuzzy: $('stat-fuzzy'),
    statUnknown: $('stat-unknown'),
    cardIndex: $('card-index'),
    chapter: $('chapter'),
    status: $('status'),
    question: $('question'),
    card: $('card'),
    sheetKeywords: $('sheet-keywords'),
    sheetJingle: $('sheet-jingle'),
    sheetAnswer: $('sheet-answer'),
    keywordsBody: $('keywords-body'),
    jingleBody: $('jingle-body'),
    answerBody: $('answer-body'),
    btnKeywords: $('btn-keywords'),
    btnJingle: $('btn-jingle'),
    btnAnswer: $('btn-answer'),
    markKnown: $('mark-known'),
    markFuzzy: $('mark-fuzzy'),
    markUnknown: $('mark-unknown'),
    btnPrev: $('btn-prev'),
    btnNext: $('btn-next'),
    resetCard: $('reset-card'),
    resetAll: $('reset-all'),
    btnZoom: $('btn-zoom'),
    zoomOverlay: $('zoom-overlay'),
    zoomClose: $('zoom-close'),
    zoomBody: $('zoom-body'),
  };

  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
    catch (e) { return {}; }
  }
  function save() { localStorage.setItem(STORAGE_KEY, JSON.stringify(statusMap)); }

  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // 常见缩写 → 全文中的展开形式
  const ALIAS_MAP = {
    '马列': ['马克思列宁主义', '马克思', '列宁'],
    '马': ['马克思'],
    '两个结合': ['相结合'],
    '两个联盟': ['联盟'],
    '四个阶段': ['阶段'],
    '一化是主体': ['工业化'],
    '三改是两翼': ['三改'],
    '重轻农': ['重工业', '轻工业', '农业'],
    '关键在党': ['关键在于'],
  };

  // 通用高亮：text 中匹配 keywords（含别名+模糊），用 className 包裹
  function highlightText(text, keywords, className) {
    const ranges = [];

    keywords.forEach(kw => {
      const matchTargets = [kw];
      if (ALIAS_MAP[kw]) matchTargets.push(...ALIAS_MAP[kw]);
      for (const alias in ALIAS_MAP) {
        if (kw.includes(alias) && !matchTargets.includes(alias)) {
          matchTargets.push(...ALIAS_MAP[alias]);
        }
      }

      matchTargets.forEach(target => {
        if (text.includes(target)) {
          let idx = 0;
          while ((idx = text.indexOf(target, idx)) !== -1) {
            ranges.push([idx, idx + target.length]);
            idx += target.length;
          }
        } else if (target.length >= 2) {
          // 模糊：从最长子串往下找，至少2字
          for (let len = target.length - 1; len >= 2; len--) {
            let found = false;
            for (let start = 0; start <= target.length - len; start++) {
              const sub = target.substring(start, start + len);
              if (text.includes(sub)) {
                let idx2 = 0;
                while ((idx2 = text.indexOf(sub, idx2)) !== -1) {
                  ranges.push([idx2, idx2 + sub.length]);
                  idx2 += sub.length;
                }
                found = true;
                break;
              }
            }
            if (found) break;
          }
        }
      });
    });

    if (ranges.length === 0) return escapeHtml(text);

    // 合并重叠区间
    ranges.sort((a, b) => a[0] - b[0]);
    const merged = [ranges[0]];
    for (let i = 1; i < ranges.length; i++) {
      const last = merged[merged.length - 1];
      if (ranges[i][0] <= last[1]) {
        last[1] = Math.max(last[1], ranges[i][1]);
      } else {
        merged.push(ranges[i]);
      }
    }

    let html = '';
    let pos = 0;
    merged.forEach(([start, end]) => {
      html += escapeHtml(text.substring(pos, start));
      html += '<span class="' + className + '">' + escapeHtml(text.substring(start, end)) + '</span>';
      pos = end;
    });
    html += escapeHtml(text.substring(pos));
    return html;
  }

  function highlightKeywords(text, keywords) {
    return highlightText(text, keywords, 'answer-kw');
  }

  function buildList() {
    if (mode === 'weak') {
      list = QUESTIONS
        .map((q, i) => ({ i, s: statusMap[q.id] }))
        .filter(x => x.s === STATE.FUZZY || x.s === STATE.UNKNOWN)
        .map(x => x.i);
    } else {
      list = QUESTIONS.map((_, i) => i);
    }
    cursor = 0;
  }

  function setMode(m) {
    mode = m;
    document.querySelectorAll('.mode-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.mode === m);
    });
    buildList();
    render(true);
  }

  function render(skipAnim) {
    if (list.length === 0) {
      dom.question.textContent = '暂无弱项题目';
      dom.cardIndex.textContent = '—';
      dom.chapter.textContent = '先标记几道「不会」';
      dom.status.className = 'status none';
      dom.status.textContent = '—';
      [dom.sheetKeywords, dom.sheetJingle, dom.sheetAnswer].forEach(s => s.hidden = true);
      return;
    }
    const idx = list[cursor];
    const q = QUESTIONS[idx];
    const s = statusMap[q.id];

    dom.cardIndex.textContent = `${cursor + 1} / ${list.length}`;
    dom.chapter.textContent = q.chapter;
    dom.status.className = 'status ' + (s || 'none');
    dom.status.textContent = s === STATE.KNOWN ? '已会' : s === STATE.FUZZY ? '模糊' : s === STATE.UNKNOWN ? '不会' : '未练';
    dom.question.textContent = q.question;

    dom.keywordsBody.innerHTML = '<div class="kw-list">' +
      q.keywords.map((k, n) => `<div class="kw-item"><span class="kw-num">${n + 1}</span><span class="kw-text">${k}</span></div>`).join('') +
      '</div>';

    dom.jingleBody.innerHTML = highlightText(q.jingle, q.keywords, 'jingle-keyword');
    dom.answerBody.innerHTML = highlightKeywords(q.answer, q.keywords);

    dom.sheetKeywords.hidden = true;
    dom.sheetJingle.hidden = true;
    dom.sheetAnswer.hidden = true;
    dom.btnKeywords.disabled = false;
    dom.btnJingle.disabled = false;
    dom.btnAnswer.disabled = false;

    renderStats();

    if (!skipAnim) {
      dom.card.classList.remove('slide-in');
      void dom.card.offsetWidth;
      dom.card.classList.add('slide-in');
    }
  }

  function renderStats() {
    let k = 0, f = 0, u = 0;
    QUESTIONS.forEach(q => {
      const s = statusMap[q.id];
      if (s === STATE.KNOWN) k++;
      else if (s === STATE.FUZZY) f++;
      else if (s === STATE.UNKNOWN) u++;
    });
    dom.statTotal.textContent = QUESTIONS.length;
    dom.statKnown.textContent = k;
    dom.statFuzzy.textContent = f;
    dom.statUnknown.textContent = u;
  }

  function show(type) {
    if (type === 'keywords') { dom.sheetKeywords.hidden = false; dom.btnKeywords.disabled = true; }
    if (type === 'jingle') { dom.sheetJingle.hidden = false; dom.btnJingle.disabled = true; }
    if (type === 'answer') {
      dom.sheetAnswer.hidden = !dom.sheetAnswer.hidden;
    }
  }

  function next(markState) {
    if (list.length === 0 || animating) return;
    animating = true;

    const direction = markState === STATE.KNOWN ? 'slide-left' : 'slide-right';
    dom.card.classList.add(direction);

    setTimeout(() => {
      dom.card.classList.remove(direction, 'slide-in');
      if (mode === 'random') {
        let n;
        do { n = Math.floor(Math.random() * QUESTIONS.length); }
        while (QUESTIONS.length > 1 && n === list[cursor]);
        list[cursor] = n;
      } else {
        cursor = (cursor + 1) % list.length;
        if (mode === 'weak' && markState === STATE.KNOWN) {
          list.splice(cursor - 1 < 0 ? list.length - 1 : cursor - 1, 1);
          if (cursor >= list.length) cursor = 0;
        }
      }
      render(true);
      dom.card.classList.add('slide-in');
      setTimeout(() => {
        dom.card.classList.remove('slide-in');
        animating = false;
      }, 450);
    }, 320);
  }

  function prev() {
    if (mode === 'random' || list.length === 0 || animating) return;
    cursor = (cursor - 1 + list.length) % list.length;
    render(true);
  }

  function mark(state) {
    if (list.length === 0) return;
    const idx = list[cursor];
    statusMap[QUESTIONS[idx].id] = state;
    save();
    renderStats();
    next(state);
  }

  function resetCard() {
    dom.sheetKeywords.hidden = true;
    dom.sheetJingle.hidden = true;
    dom.sheetAnswer.hidden = true;
    dom.btnKeywords.disabled = false;
    dom.btnJingle.disabled = false;
    dom.btnAnswer.disabled = false;
  }

  function resetAll() {
    if (!confirm('确定重置全部学习进度？此操作不可恢复。')) return;
    statusMap = {};
    save();
    setMode('order');
  }

  function openZoom() {
    if (list.length === 0) return;
    const idx = list[cursor];
    const q = QUESTIONS[idx];

    let html = '';
    html += '<div class="zoom-chapter">' + escapeHtml(q.chapter) + '</div>';
    html += '<div class="zoom-question">' + escapeHtml(q.question) + '</div>';

    // 骨架：始终显示
    html += '<div class="zoom-sheet"><div class="zoom-sheet-title">骨架</div><div class="zoom-sheet-body">';
    html += '<div class="zoom-kw-list">' +
      q.keywords.map((k, n) => '<div class="zoom-kw-item"><span class="zoom-kw-num">' + (n + 1) + '</span><span class="zoom-kw-text">' + escapeHtml(k) + '</span></div>').join('') +
      '</div>';
    html += '</div></div>';

    // 串记：始终显示，用通用高亮
    html += '<div class="zoom-sheet zoom-sheet-jingle"><div class="zoom-sheet-title">串记</div><div class="zoom-sheet-body">' +
      highlightText(q.jingle, q.keywords, 'zoom-jingle-keyword') + '</div></div>';

    // 全文：始终显示，关键词高亮
    html += '<div class="zoom-sheet zoom-sheet-answer"><div class="zoom-sheet-title">全文</div><div class="zoom-sheet-body">' +
      highlightKeywords(q.answer, q.keywords) + '</div></div>';

    dom.zoomBody.innerHTML = html;
    dom.zoomOverlay.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function closeZoom() {
    dom.zoomOverlay.hidden = true;
    document.body.style.overflow = '';
  }

  dom.btnKeywords.addEventListener('click', () => show('keywords'));
  dom.btnJingle.addEventListener('click', () => show('jingle'));
  dom.btnAnswer.addEventListener('click', () => show('answer'));
  dom.markKnown.addEventListener('click', () => mark(STATE.KNOWN));
  dom.markFuzzy.addEventListener('click', () => mark(STATE.FUZZY));
  dom.markUnknown.addEventListener('click', () => mark(STATE.UNKNOWN));
  dom.btnPrev.addEventListener('click', prev);
  dom.btnNext.addEventListener('click', () => next());
  dom.resetCard.addEventListener('click', resetCard);
  dom.resetAll.addEventListener('click', resetAll);
  dom.btnZoom.addEventListener('click', openZoom);
  dom.zoomClose.addEventListener('click', closeZoom);
  dom.zoomOverlay.addEventListener('click', (e) => {
    if (e.target === dom.zoomOverlay) closeZoom();
  });

  document.querySelectorAll('.mode-btn').forEach(b => {
    b.addEventListener('click', () => setMode(b.dataset.mode));
  });

  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'Escape') { closeZoom(); return; }
    if (!dom.zoomOverlay.hidden) return;
    switch (e.key) {
      case '1': show('keywords'); break;
      case '2': show('jingle'); break;
      case '3': show('answer'); break;
      case 'ArrowLeft': prev(); break;
      case 'ArrowRight': next(); break;
      case 'q': case 'Q': mark(STATE.KNOWN); break;
      case 'w': case 'W': mark(STATE.FUZZY); break;
      case 'e': case 'E': mark(STATE.UNKNOWN); break;
    }
  });

  setMode('order');
})();
