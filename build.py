#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Apple 卡片派风格的毛概速背页面"""

import os

BASE = r"D:\PROJECTALL\MaoGai"

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>一天背完作战台</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="app">
    <header class="topbar">
      <h1 class="brand">一天背完作战台</h1>
      <div class="stats">
        <span id="stat-total">0</span> 题
        <span class="dot known"></span><span id="stat-known">0</span>
        <span class="dot fuzzy"></span><span id="stat-fuzzy">0</span>
        <span class="dot unknown"></span><span id="stat-unknown">0</span>
      </div>
    </header>

    <nav class="modes">
      <button class="mode-btn active" data-mode="order">顺序</button>
      <button class="mode-btn" data-mode="random">随机</button>
      <button class="mode-btn" data-mode="weak">弱项</button>
    </nav>

    <div class="card-stage">
      <div class="card" id="card">
        <div class="card-header">
          <span class="card-index" id="card-index">—</span>
          <span class="chapter" id="chapter">—</span>
          <span class="status" id="status">未练</span>
        </div>
        <div class="question" id="question">加载中…</div>
        <div class="scroll-area" id="scroll-area">
          <div class="hint-sheet" id="sheet-keywords" hidden>
            <div class="sheet-title">骨架</div>
            <div class="sheet-body" id="keywords-body"></div>
          </div>
          <div class="hint-sheet sheet-jingle" id="sheet-jingle" hidden>
            <div class="sheet-title">串记</div>
            <div class="sheet-body" id="jingle-body"></div>
          </div>
          <div class="hint-sheet sheet-answer" id="sheet-answer" hidden>
            <div class="sheet-title">全文</div>
            <div class="sheet-body" id="answer-body"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="controls">
      <div class="reveal-bar">
        <button class="chip" id="btn-keywords">骨架</button>
        <button class="chip" id="btn-jingle">串记</button>
        <button class="chip chip-main" id="btn-answer">全文</button>
      </div>
      <div class="mark-bar">
        <button class="mark known" id="mark-known">会了</button>
        <button class="mark fuzzy" id="mark-fuzzy">模糊</button>
        <button class="mark unknown" id="mark-unknown">不会</button>
      </div>
      <div class="secondary">
        <button class="text-btn" id="btn-prev">上一题</button>
        <button class="text-btn" id="reset">重置</button>
        <button class="text-btn" id="btn-next">下一题</button>
      </div>
    </div>
  </div>

  <script src="questions.js"></script>
  <script src="app.js"></script>
</body>
</html>
"""

CSS = """:root {
  --bg: #f2f2f7;
  --surface: #ffffff;
  --ink: #1c1c1e;
  --ink-2: #636366;
  --ink-3: #8e8e93;
  --separator: #e5e5ea;
  --blue: #007aff;
  --blue-soft: #e6f2ff;
  --green: #34c759;
  --green-soft: #e6f9ea;
  --orange: #ff9500;
  --orange-soft: #fff4e6;
  --red: #ff3b30;
  --red-soft: #ffebea;
  --radius: 24px;
  --radius-sm: 16px;
  --radius-xs: 10px;
  --shadow: 0 10px 40px rgba(0,0,0,0.12);
  --shadow-sm: 0 2px 12px rgba(0,0,0,0.08);
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.55;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

.app {
  max-width: 560px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 18px 16px 16px;
  gap: 12px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 0 4px;
}
.brand {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.3px;
  color: var(--ink);
}
.stats {
  font-size: 14px;
  color: var(--ink-3);
  display: flex;
  align-items: center;
  gap: 8px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-left: 4px;
}
.dot.known { background: var(--green); }
.dot.fuzzy { background: var(--orange); }
.dot.unknown { background: var(--red); }

.modes {
  display: flex;
  gap: 8px;
  padding: 0 4px;
}
.mode-btn {
  flex: 1;
  padding: 9px 0;
  border: none;
  background: var(--surface);
  color: var(--ink-2);
  font-size: 14px;
  font-weight: 600;
  border-radius: var(--radius-xs);
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}
.mode-btn.active {
  background: var(--ink);
  color: #fff;
}

.card-stage {
  flex: 1;
  min-height: 0;
  position: relative;
  display: flex;
  align-items: stretch;
  justify-content: center;
  padding: 4px 0;
}
.card {
  width: 100%;
  background: var(--surface);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.35s cubic-bezier(0.25, 1, 0.5, 1), opacity 0.35s ease;
}
.card.slide-left { transform: translateX(-120%) rotate(-6deg); opacity: 0; }
.card.slide-right { transform: translateX(120%) rotate(6deg); opacity: 0; }
.card.slide-in { animation: cardIn 0.45s cubic-bezier(0.25, 1, 0.5, 1) forwards; }

@keyframes cardIn {
  from { transform: translateY(40px) scale(0.94); opacity: 0; }
  to { transform: translateY(0) scale(1); opacity: 1; }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px 12px;
  border-bottom: 1px solid var(--separator);
  font-size: 13px;
}
.card-index { color: var(--ink-3); font-weight: 600; }
.chapter { color: var(--blue); font-weight: 600; }
.status {
  padding: 3px 9px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 12px;
}
.status.none { color: var(--ink-3); background: var(--bg); }
.status.known { color: var(--green); background: var(--green-soft); }
.status.fuzzy { color: var(--orange); background: var(--orange-soft); }
.status.unknown { color: var(--red); background: var(--red-soft); }

.question {
  padding: 22px 20px 18px;
  font-size: 24px;
  font-weight: 700;
  line-height: 1.45;
  letter-spacing: -0.3px;
}

.scroll-area {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.scroll-area::-webkit-scrollbar { display: none; }

.hint-sheet {
  background: var(--blue-soft);
  border-radius: var(--radius-sm);
  padding: 14px 16px;
  animation: sheetIn 0.25s ease;
}
.hint-sheet.sheet-jingle { background: var(--orange-soft); }
.hint-sheet.sheet-answer { background: #f2f2f7; }

@keyframes sheetIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.sheet-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--ink-3);
  margin-bottom: 8px;
}
.sheet-body {
  font-size: 16px;
  line-height: 1.7;
  color: var(--ink);
  white-space: pre-wrap;
}
.sheet-jingle .sheet-body {
  color: var(--orange);
  font-weight: 600;
}
.kw-list { display: flex; flex-direction: column; gap: 8px; }
.kw-item {
  display: flex;
  align-items: baseline;
  gap: 10px;
  background: #fff;
  padding: 10px 12px;
  border-radius: var(--radius-xs);
}
.kw-num {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--blue);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.kw-text { font-weight: 500; }
.jingle-keyword {
  background: #fff;
  color: var(--orange);
  padding: 1px 6px;
  border-radius: 5px;
  font-weight: 800;
}

.controls {
  background: var(--surface);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  padding: 14px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.reveal-bar {
  display: flex;
  gap: 8px;
}
.chip {
  flex: 1;
  padding: 12px 0;
  border: none;
  border-radius: var(--radius-xs);
  background: var(--bg);
  color: var(--ink-2);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.chip:hover { background: var(--separator); }
.chip:disabled { opacity: 0.4; cursor: default; }
.chip-main {
  background: var(--blue);
  color: #fff;
}
.chip-main:hover { background: #0056b3; }

.mark-bar {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}
.mark {
  padding: 14px 0;
  border: none;
  border-radius: var(--radius-xs);
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  cursor: pointer;
  transition: transform 0.1s ease;
}
.mark:active { transform: scale(0.96); }
.mark.known { background: var(--green); }
.mark.fuzzy { background: var(--orange); }
.mark.unknown { background: var(--red); }

.secondary {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.text-btn {
  background: none;
  border: none;
  color: var(--ink-3);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 8px;
  transition: color 0.15s;
}
.text-btn:hover { color: var(--ink); }

@media (max-width: 420px) {
  .app { padding: 14px 12px 12px; }
  .brand { font-size: 18px; }
  .question { font-size: 21px; }
  .stats { font-size: 13px; }
}
"""

JS = """(function () {
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
    reset: $('reset'),
  };

  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
    catch (e) { return {}; }
  }
  function save() { localStorage.setItem(STORAGE_KEY, JSON.stringify(statusMap)); }

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

    let jingleHtml = q.jingle;
    q.keywords.forEach(k => {
      jingleHtml = jingleHtml.split(k).join(`<span class="jingle-keyword">${k}</span>`);
    });
    dom.jingleBody.innerHTML = jingleHtml;
    dom.answerBody.textContent = q.answer;

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
    if (type === 'answer') { dom.sheetAnswer.hidden = false; dom.btnAnswer.disabled = true; }
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

  function resetAll() {
    if (!confirm('确定重置全部进度？')) return;
    statusMap = {};
    save();
    setMode('order');
  }

  dom.btnKeywords.addEventListener('click', () => show('keywords'));
  dom.btnJingle.addEventListener('click', () => show('jingle'));
  dom.btnAnswer.addEventListener('click', () => show('answer'));
  dom.markKnown.addEventListener('click', () => mark(STATE.KNOWN));
  dom.markFuzzy.addEventListener('click', () => mark(STATE.FUZZY));
  dom.markUnknown.addEventListener('click', () => mark(STATE.UNKNOWN));
  dom.btnPrev.addEventListener('click', prev);
  dom.btnNext.addEventListener('click', () => next());
  dom.reset.addEventListener('click', resetAll);

  document.querySelectorAll('.mode-btn').forEach(b => {
    b.addEventListener('click', () => setMode(b.dataset.mode));
  });

  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
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
"""

for name, content in [("index.html", HTML), ("styles.css", CSS), ("app.js", JS)]:
    path = os.path.join(BASE, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {path}")
