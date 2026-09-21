
(function () {
  'use strict';

  var $  = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var THEME_KEY = 'rev-theme';
  function storedTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch (e) { return null; }
  }
  function resolvedTheme() {
    var t = document.documentElement.getAttribute('data-theme');
    if (t === 'dark' || t === 'light') return t;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function applyTheme(t) {
    if (t === 'auto' || !t) document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', t);
    try { t ? localStorage.setItem(THEME_KEY, t) : localStorage.removeItem(THEME_KEY); } catch (e) {}
    document.dispatchEvent(new CustomEvent('themechange'));
  }
  function initTheme() {
    var btn = $('#theme-toggle');
    if (!btn) return;
    var order = ['auto', 'light', 'dark'];
    var glyph = { auto: '◐ 자동', light: '○ 밝게', dark: '● 어둡게' };
    function label() {
      var cur = storedTheme() || 'auto';
      btn.textContent = glyph[cur];
      btn.setAttribute('aria-label', '화면 밝기: ' + glyph[cur].slice(2));
    }
    label();
    btn.addEventListener('click', function () {
      var cur = storedTheme() || 'auto';
      applyTheme(order[(order.indexOf(cur) + 1) % order.length]);
      label();
    });
  }

  function slug(s, used) {
    var base = s.toLowerCase().trim()
      .replace(/[^가-힣\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/^-+|-+$/g, '') || 'sec';
    var id = base, i = 2;
    while (used[id]) { id = base + '-' + i++; }
    used[id] = 1;
    return id;
  }

  function buildToc() {
    var body = $('.report-body');
    var host = $('#toc');
    if (!body || !host) return;

    var heads = $$('h2, h3', body).filter(function (h) {
      return !h.classList.contains('no-number') && !h.closest('.revisions');
    });
    if (heads.length < 3) { host.remove(); return; }

    var used = {};
    $$('[id]', document).forEach(function (n) { used[n.id] = 1; });

    var ol = document.createElement('ol');
    var sub = null;

    heads.forEach(function (h) {
      if (!h.id) h.id = slug(h.textContent, used);

      var li = document.createElement('li');
      var a  = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent.replace(/^§\s*/, '').trim();
      li.appendChild(a);

      if (h.tagName === 'H2') {
        ol.appendChild(li);
        sub = null;
      } else {
        if (!sub) {
          sub = document.createElement('ol');
          (ol.lastElementChild || ol).appendChild(sub);
        }
        sub.appendChild(li);
      }
    });

    var t = document.createElement('div');
    t.className = 'toc-title';
    t.textContent = '목차';
    host.appendChild(t);
    host.appendChild(ol);
  }

  function headingAnchors() {
    var body = $('.report-body');
    if (!body) return;
    var used = {};
    $$('[id]', document).forEach(function (n) { used[n.id] = 1; });

    $$('h2, h3, h4', body).forEach(function (h) {
      if (h.classList.contains('no-number') && !h.id) return;
      if (!h.id) h.id = slug(h.textContent, used);
      if ($('.anchor', h)) return;
      var a = document.createElement('a');
      a.className = 'anchor';
      a.href = '#' + h.id;
      a.textContent = '§';
      a.setAttribute('aria-label', '이 절로 가는 링크');
      h.insertBefore(a, h.firstChild);
    });
  }

  function footnotePopovers() {
    var refs = $$('sup[role="doc-noteref"] a, a.footnote, cite.ref a');
    if (!refs.length) return;
    if (window.matchMedia && window.matchMedia('(hover: none)').matches) return;

    var pop = document.createElement('div');
    pop.id = 'fn-pop';
    pop.hidden = true;
    document.body.appendChild(pop);
    var timer;

    function show(ref) {
      var id = decodeURIComponent((ref.getAttribute('href') || '').slice(1));
      var note = document.getElementById(id);
      if (!note) return;
      pop.innerHTML = note.innerHTML;
      pop.hidden = false;

      var r = ref.getBoundingClientRect();
      var w = pop.offsetWidth;
      var left = window.scrollX + r.left + r.width / 2 - w / 2;
      left = Math.max(window.scrollX + 8, Math.min(left, window.scrollX + document.documentElement.clientWidth - w - 8));
      var top = window.scrollY + r.bottom + 8;
      if (r.bottom + pop.offsetHeight + 20 > window.innerHeight) {
        top = window.scrollY + r.top - pop.offsetHeight - 8;
      }
      pop.style.left = left + 'px';
      pop.style.top  = top + 'px';
    }
    function hide() { pop.hidden = true; }

    refs.forEach(function (ref) {
      ref.addEventListener('mouseenter', function () { clearTimeout(timer); show(ref); });
      ref.addEventListener('focus',      function () { show(ref); });
      ref.addEventListener('mouseleave', function () { timer = setTimeout(hide, 180); });
      ref.addEventListener('blur',       hide);
    });
    pop.addEventListener('mouseenter', function () { clearTimeout(timer); });
    pop.addEventListener('mouseleave', hide);
    window.addEventListener('beforeprint', hide);
  }

  function buildRevisions() {
    var host = $('#revisions');
    if (!host) return;

    var body = $('.report-body');
    var rows = [];

    if (body) {
      $$('.addendum, .correction', body).forEach(function (el, i) {
        var date = el.getAttribute('data-date') || '';
        var kind = el.getAttribute('data-label') ||
                   (el.classList.contains('correction') ? '정정' : '추가');
        if (!el.id) el.id = 'rev-note-' + (i + 1);
        var text = (el.getAttribute('data-note') || el.textContent || '')
                     .replace(/\s+/g, ' ').trim();
        if (text.length > 90) text = text.slice(0, 90) + '…';
        rows.push({ date: date, kind: kind, text: text, href: '#' + el.id });
      });
    }

    if (host.getAttribute('data-seeded') === 'true') return;
    if (!rows.length) { host.remove(); return; }

    rows.sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : 0; });

    var tbody = $('#revisions tbody');
    if (!tbody) {
      host.insertAdjacentHTML('beforeend',
        '<div class="table-scroll"><table><thead><tr>' +
        '<th>판</th><th>일자</th><th>구분</th><th>변경 내용</th>' +
        '</tr></thead><tbody></tbody></table></div>');
      tbody = $('#revisions tbody');
    }

    var total = rows.length;
    rows.forEach(function (r, i) {
      var rev = '1.' + (total - i);
      var tr = document.createElement('tr');
      tr.innerHTML =
        '<td>' + rev + '</td>' +
        '<td>' + esc(r.date) + '</td>' +
        '<td>' + esc(r.kind) + '</td>' +
        '<td><a href="' + r.href + '">' + esc(r.text) + '</a></td>';
      tbody.insertBefore(tr, tbody.firstChild);
    });

    var latest = rows[0].date;
    var slot = $('#revised-slot');
    if (slot && latest) {
      slot.textContent = latest + ' (rev. 1.' + total + ')';
      var wrap = slot.closest('div');
      if (wrap) wrap.hidden = false;
    }
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
    });
  }

  function wrapTables() {
    $$('.report-body > table').forEach(function (t) {
      var d = document.createElement('div');
      d.className = 'table-scroll';
      t.parentNode.insertBefore(d, t);
      d.appendChild(t);
    });
  }

  var MERMAID_SRC = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js';

  function collectFences(lang) {
    var sel = 'div.language-' + lang + ', figure.language-' + lang +
              ', code.language-' + lang + ', pre > code.' + lang;
    var seen = [], out = [];
    $$(sel).forEach(function (el) {
      var code = el.tagName === 'CODE' ? el : el.querySelector('code');
      if (!code || seen.indexOf(code) >= 0) return;
      seen.push(code);
      var outer;
      if (el.tagName === 'CODE') {
        outer = el.closest('div.language-' + lang) ||
                el.closest('div.highlight, figure.highlight, pre') || el;
      } else {
        outer = el;
      }
      out.push({ src: code.textContent, node: outer });
    });
    return out;
  }

  function initMermaid() {
    var found = collectFences('mermaid');
    if (!found.length) return;

    var blocks = found.map(function (f) {
      var d = document.createElement('div');
      d.className = 'diagram';
      d.setAttribute('data-state', 'pending');
      d.setAttribute('data-src', f.src);
      f.node.parentNode.replaceChild(d, f.node);
      return d;
    });

    function fail(msg) {
      blocks.forEach(function (d) {
        d.removeAttribute('data-state');
        d.innerHTML = '<div class="diagram-error">다이어그램을 그리지 못했습니다. ' +
                      esc(msg || '') + '\n\n' + esc(d.getAttribute('data-src')) + '</div>';
      });
    }

    var s = document.createElement('script');
    s.src = MERMAID_SRC;
    s.async = true;
    s.onerror = function () { fail('(mermaid 로드 실패 — 오프라인일 수 있습니다)'); };
    s.onload = function () {
      if (!window.mermaid) return fail('');
      var render = function () {
        var dark = resolvedTheme() === 'dark';
        try {
          window.mermaid.initialize({
            startOnLoad: false,
            securityLevel: 'strict',
            theme: dark ? 'dark' : 'neutral',
            fontFamily: 'Georgia, "Noto Serif KR", serif',
            themeVariables: { fontSize: '14px' },
            flowchart: { curve: 'linear', useMaxWidth: true },
            sequence: { useMaxWidth: true },
            gantt: { useMaxWidth: true }
          });
          blocks.forEach(function (d, i) {
            d.removeAttribute('data-state');
            var src = d.getAttribute('data-src');
            window.mermaid.render('mmd-' + Date.now() + '-' + i, src)
              .then(function (res) { d.innerHTML = res.svg; })
              .catch(function (e) {
                d.innerHTML = '<div class="diagram-error">' + esc(String(e && e.message || e)) +
                              '\n\n' + esc(src) + '</div>';
              });
          });
        } catch (e) { fail(String(e && e.message || e)); }
      };
      render();
      document.addEventListener('themechange', render);
    };
    document.head.appendChild(s);
  }

  var RESERVED = ['type', 'title', 'caption', 'unit', 'max', 'series', 'height'];

  function parseChart(src) {
    var t = src.trim();
    if (t.charAt(0) === '{') { return JSON.parse(t); }

    var spec = { type: 'bar', labels: [], series: [] };
    var names = null, rows = [];

    t.split('\n').forEach(function (line) {
      line = line.trim();
      if (!line || line.charAt(0) === '#') return;
      var i = line.indexOf(':');
      if (i < 0) return;
      var key = line.slice(0, i).trim();
      var val = line.slice(i + 1).trim();
      var lower = key.toLowerCase();

      if (RESERVED.indexOf(lower) >= 0) {
        if (lower === 'series') names = val.split(',').map(function (s) { return s.trim(); });
        else if (lower === 'max' || lower === 'height') spec[lower] = parseFloat(val);
        else spec[lower] = val;
      } else {
        rows.push({
          label: key,
          vals: val.split(',').map(function (s) { return parseFloat(s.trim()); })
        });
      }
    });

    var width = rows.reduce(function (m, r) { return Math.max(m, r.vals.length); }, 1);
    spec.labels = rows.map(function (r) { return r.label; });
    for (var k = 0; k < width; k++) {
      spec.series.push({
        name: (names && names[k]) || (width > 1 ? '계열 ' + (k + 1) : ''),
        data: rows.map(function (r) { return isNaN(r.vals[k]) ? 0 : r.vals[k]; })
      });
    }
    return spec;
  }

  function niceMax(v) {
    if (v <= 0) return 1;
    var mag = Math.pow(10, Math.floor(Math.log10(v)));
    var n = v / mag;
    var step = n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10;
    return step * mag;
  }

  function fmt(n) {
    if (Math.abs(n) >= 1000) return n.toLocaleString('ko-KR');
    return String(Math.round(n * 100) / 100);
  }

  function svgEl(name, attrs) {
    var e = document.createElementNS('http://www.w3.org/2000/svg', name);
    for (var k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    return e;
  }

  function renderChart(spec) {
    var type = (spec.type || 'bar').toLowerCase();
    var labels = spec.labels || [];
    var series = (spec.series || []).filter(function (s) { return s && s.data; });
    if (!labels.length || !series.length) throw new Error('labels 또는 series 가 비어 있습니다.');

    var W = 680;
    var padL = 46, padR = 14, padT = 14;
    var padB = 34 + (series.length > 1 ? 20 : 0);
    var H = spec.height || (type === 'hbar' ? Math.max(140, labels.length * 30 + padT + padB) : 260);

    var peak = 0;
    series.forEach(function (s) {
      s.data.forEach(function (v) { peak = Math.max(peak, Math.abs(+v || 0)); });
    });
    var max = spec.max || niceMax(peak) || 1;

    if (type === 'hbar') {
      padL = Math.min(160, 8 + labels.reduce(function (m, l) {
        return Math.max(m, String(l).length * 7.2);
      }, 40));
    }

    var plotW = W - padL - padR;
    var plotH = H - padT - padB;
    var svg = svgEl('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img' });
    if (spec.title) {
      var ttl = svgEl('title');
      ttl.textContent = spec.title;
      svg.appendChild(ttl);
    }

    var TICKS = 4;
    var i, j, k;

    if (type === 'hbar') {
      for (k = 0; k <= TICKS; k++) {
        var gx = padL + plotW * k / TICKS;
        svg.appendChild(svgEl('line', { x1: gx, y1: padT, x2: gx, y2: padT + plotH, 'class': k ? 'c-grid' : 'c-base' }));
        var tx = svgEl('text', { x: gx, y: padT + plotH + 16, 'class': 'c-tick', 'text-anchor': 'middle' });
        tx.textContent = fmt(max * k / TICKS) + (k === TICKS && spec.unit ? ' ' + spec.unit : '');
        svg.appendChild(tx);
      }
      var rowH = plotH / labels.length;
      var bh = Math.min(18, rowH * 0.62 / series.length);
      labels.forEach(function (lab, idx) {
        var cy = padT + rowH * (idx + 0.5);
        var lt = svgEl('text', { x: padL - 8, y: cy + 4, 'class': 'c-label', 'text-anchor': 'end' });
        lt.textContent = lab;
        svg.appendChild(lt);
        series.forEach(function (s, si) {
          var v = +s.data[idx] || 0;
          var w = Math.max(0, v / max * plotW);
          var y = cy - (bh * series.length) / 2 + bh * si;
          svg.appendChild(svgEl('rect', { x: padL, y: y, width: w, height: Math.max(1, bh - 2), 'class': 'c-bar s' + (si % 3) }));
          var vt = svgEl('text', { x: padL + w + 5, y: y + bh - 4, 'class': 'c-value' });
          vt.textContent = fmt(v);
          svg.appendChild(vt);
        });
      });
    } else {
      for (k = 0; k <= TICKS; k++) {
        var gy = padT + plotH - plotH * k / TICKS;
        svg.appendChild(svgEl('line', { x1: padL, y1: gy, x2: padL + plotW, y2: gy, 'class': k ? 'c-grid' : 'c-base' }));
        var ty = svgEl('text', { x: padL - 8, y: gy + 4, 'class': 'c-tick', 'text-anchor': 'end' });
        ty.textContent = fmt(max * k / TICKS);
        svg.appendChild(ty);
      }

      var slotW = plotW / labels.length;
      labels.forEach(function (lab, idx) {
        var cx = padL + slotW * (idx + 0.5);
        var lt = svgEl('text', { x: cx, y: padT + plotH + 18, 'class': 'c-label', 'text-anchor': 'middle' });
        lt.textContent = lab;
        svg.appendChild(lt);
      });

      if (type === 'line' || type === 'area') {
        series.forEach(function (s, si) {
          var pts = s.data.map(function (v, idx) {
            return [padL + slotW * (idx + 0.5), padT + plotH - (+v || 0) / max * plotH];
          });
          svg.appendChild(svgEl('path', {
            d: 'M' + pts.map(function (p) { return p[0].toFixed(1) + ' ' + p[1].toFixed(1); }).join(' L'),
            'class': 'c-line s' + (si % 3)
          }));
          pts.forEach(function (p) {
            svg.appendChild(svgEl('circle', { cx: p[0], cy: p[1], r: 3, 'class': 'c-dot s' + (si % 3) }));
          });
        });
      } else {
        var bw = Math.min(46, slotW * 0.68 / series.length);
        labels.forEach(function (lab, idx) {
          var cx = padL + slotW * (idx + 0.5);
          series.forEach(function (s, si) {
            var v = +s.data[idx] || 0;
            var h = Math.max(0, v / max * plotH);
            var x = cx - (bw * series.length) / 2 + bw * si;
            svg.appendChild(svgEl('rect', {
              x: x, y: padT + plotH - h, width: Math.max(1, bw - 2), height: h,
              'class': 'c-bar s' + (si % 3)
            }));
            var vt = svgEl('text', {
              x: x + (bw - 2) / 2, y: padT + plotH - h - 5,
              'class': 'c-value', 'text-anchor': 'middle'
            });
            vt.textContent = fmt(v);
            svg.appendChild(vt);
          });
        });
      }
    }

    if (series.length > 1) {
      var lx = padL;
      series.forEach(function (s, si) {
        var g = svgEl('g');
        g.appendChild(svgEl('rect', { x: lx, y: H - 14, width: 10, height: 10, 'class': 'c-bar s' + (si % 3) }));
        var t2 = svgEl('text', { x: lx + 15, y: H - 5, 'class': 'c-legend' });
        t2.textContent = s.name || ('계열 ' + (si + 1));
        g.appendChild(t2);
        svg.appendChild(g);
        lx += 28 + String(s.name || '').length * 8;
      });
    }
    return svg;
  }

  function initCharts() {
    collectFences('chart').forEach(function (f) {
      var fig = document.createElement('figure');
      fig.className = 'chart';
      try {
        var spec = parseChart(f.src);
        fig.appendChild(renderChart(spec));
        var cap = spec.caption || spec.title;
        if (cap) {
          var fc = document.createElement('figcaption');
          fc.textContent = cap;
          fig.appendChild(fc);
        }
      } catch (e) {
        fig.innerHTML = '<div class="diagram-error">그래프를 그리지 못했습니다. ' +
                        esc(String(e && e.message || e)) + '\n\n' + esc(f.src) + '</div>';
      }
      f.node.parentNode.replaceChild(fig, f.node);
    });
  }

  function initCitations() {
    if (!document.getElementById('references')) return;
    $$('cite[data-ref]').forEach(function (c) {
      var n  = c.getAttribute('data-ref');
      var li = document.getElementById('ref-' + n);
      if (!li) { c.hidden = true; return; }
      var src  = li.getAttribute('data-source') || '출처';
      var date = li.getAttribute('data-date') || '';
      var a = document.createElement('a');
      a.href = '#ref-' + n;
      a.textContent = date ? src + ' ' + date : src;
      c.className = 'ref';
      c.textContent = '';
      c.appendChild(a);
    });
  }

  function initRefPanel() {
    var section = document.getElementById('references');
    var btn = $('#ref-toggle');
    var src = section && section.querySelector('ol.reflist');
    if (!section || !btn || !src) { if (btn) btn.hidden = true; return; }

    var panel = document.createElement('aside');
    panel.id = 'ref-panel';
    panel.hidden = true;
    panel.setAttribute('aria-label', '참고자료');
    panel.innerHTML = '<button type="button" class="close" aria-label="닫기">×</button><h2>참고자료</h2>';

    var ol = document.createElement('ol');
    ol.className = 'reflist';
    $$('li', src).forEach(function (li) {
      var c = li.cloneNode(true);
      c.setAttribute('data-n', li.id.replace('ref-', ''));
      c.removeAttribute('id');
      ol.appendChild(c);
    });
    panel.appendChild(ol);
    document.body.appendChild(panel);

    function open()  { panel.hidden = false; btn.setAttribute('aria-expanded', 'true');  btn.textContent = '참고자료 닫기'; }
    function close() { panel.hidden = true;  btn.setAttribute('aria-expanded', 'false'); btn.textContent = '참고자료 따로 보기'; }

    btn.addEventListener('click', function () { panel.hidden ? open() : close(); });
    $('.close', panel).addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) close(); });
    window.addEventListener('beforeprint', close);

    document.addEventListener('click', function (e) {
      var a = e.target.closest('cite.ref a');
      if (!a || panel.hidden) return;
      e.preventDefault();
      var n = a.getAttribute('href').replace('#ref-', '');
      $$('li', ol).forEach(function (li) { li.classList.toggle('on', li.getAttribute('data-n') === n); });
      var hit = $('li[data-n="' + n + '"]', ol);
      if (hit) hit.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    });
  }

  function boot() {
    initTheme();
    initMermaid();
    initCharts();
    initCitations();
    headingAnchors();
    buildToc();
    buildRevisions();
    wrapTables();
    footnotePopovers();
    initRefPanel();

    $$('[data-print]').forEach(function (el) {
      el.addEventListener('click', function () { window.print(); });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else { boot(); }
})();
