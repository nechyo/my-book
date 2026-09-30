
(function () {
  'use strict';

  var $  = function (s, r) { return (r || document).querySelector(s); };
  var ASSET_V = (function () {
    var s = document.currentScript, m = s && s.src && /[?&]v=([^&]+)/.exec(s.src);
    return m ? '?v=' + m[1] : '';
  })();
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
    var refs = $$('sup[role="doc-noteref"] a, a.footnote, cite.ref a, a.att[data-ref], a.vuln[data-ref]');
    if (!refs.length) return;
    if (window.matchMedia && window.matchMedia('(hover: none)').matches) return;

    var pop = document.createElement('div');
    pop.id = 'fn-pop';
    pop.hidden = true;
    document.body.appendChild(pop);
    var timer;

    function show(ref) {
      var id = ref.getAttribute('data-ref') || decodeURIComponent((ref.getAttribute('href') || '').slice(1));
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

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function splitTitle(src) {
    var m = /^\s*---[ \t]*\n([\s\S]*?)\n---[ \t]*\n/.exec(src);
    if (!m) return { title: '', src: src };
    var title = '';
    var rest = m[1].split('\n').filter(function (line) {
      var t = /^(title|caption)\s*:\s*(.*)$/.exec(line);
      if (t) { title = t[2].trim().replace(/^["']|["']$/g, ''); return false; }
      return true;
    });
    var head = rest.join('\n').trim() ? '---\n' + rest.join('\n') + '\n---\n' : '';
    return { title: title, src: head + src.slice(m[0].length) };
  }

  function diagramKind(src) {
    var body = src.replace(/^\s*---[ \t]*\n[\s\S]*?\n---[ \t]*\n/, '');
    var lines = body.split('\n');
    for (var i = 0; i < lines.length; i++) {
      var l = lines[i].trim();
      if (l && l.indexOf('%%') !== 0) return l.split(/\s+/)[0];
    }
    return '';
  }

  function mermaidTheme() {
    var t = {
      paper: cssVar('--paper'), paper2: cssVar('--paper-2'), card: cssVar('--card'),
      ink: cssVar('--ink'), ink2: cssVar('--ink-2'), ink3: cssVar('--ink-3'),
      rule: cssVar('--rule'), rule2: cssVar('--rule-2'), accent: cssVar('--accent'),
      mono: cssVar('--mono')
    };
    t.vars = {
      darkMode: resolvedTheme() === 'dark',
      background: t.paper,
      fontFamily: t.mono,
      fontSize: '13px',
      primaryColor: t.card, primaryTextColor: t.ink, primaryBorderColor: t.ink,
      secondaryColor: t.paper2, secondaryTextColor: t.ink, secondaryBorderColor: t.rule,
      tertiaryColor: t.paper2, tertiaryTextColor: t.ink, tertiaryBorderColor: t.rule,
      mainBkg: t.card, nodeBorder: t.ink, nodeTextColor: t.ink, textColor: t.ink, titleColor: t.ink,
      lineColor: t.ink2, edgeLabelBackground: t.paper, labelBackground: t.paper,
      clusterBkg: t.paper2, clusterBorder: t.rule,
      noteBkgColor: t.paper2, noteBorderColor: t.rule, noteTextColor: t.ink2,
      actorBkg: t.card, actorBorder: t.ink, actorTextColor: t.ink, actorLineColor: t.rule,
      signalColor: t.ink2, signalTextColor: t.ink,
      labelBoxBkgColor: t.paper2, labelBoxBorderColor: t.rule, labelTextColor: t.ink, loopTextColor: t.ink2,
      activationBkgColor: t.paper2, activationBorderColor: t.ink2, sequenceNumberColor: t.paper,
      pie1: t.ink, pie2: t.accent, pie3: t.ink3, pie4: t.rule, pie5: t.ink2, pie6: t.rule2,
      pieStrokeColor: t.paper, pieOuterStrokeColor: t.rule, pieTitleTextColor: t.ink,
      pieSectionTextColor: t.paper, pieLegendTextColor: t.ink,
      taskBkgColor: t.paper2, taskBorderColor: t.ink2, taskTextColor: t.ink, taskTextDarkColor: t.ink,
      activeTaskBkgColor: t.card, activeTaskBorderColor: t.accent, critBkgColor: t.accent, critBorderColor: t.accent,
      doneTaskBkgColor: t.rule2, doneTaskBorderColor: t.ink3, gridColor: t.rule2,
      sectionBkgColor: t.paper2, altSectionBkgColor: t.paper, todayLineColor: t.accent,
      errorBkgColor: t.card, errorTextColor: t.accent
    };
    t.css = [
      '.node rect, .node polygon, .cluster rect, .actor, .note, .labelBox { rx: 0 !important; ry: 0 !important; }',
      '.node rect, .node polygon, .node circle, .node path { stroke-width: 1px; }',
      '.flowchart-link, .edgePath .path, .messageLine0, .messageLine1 { stroke-width: 1px; }',
      '.cluster-label, .cluster-label span { color: ' + t.ink3 + ' !important; }',
      '.edgeLabel, .edgeLabel p { color: ' + t.ink2 + '; font-size: 12px; }',
      '.node.key .label, .node.key .nodeLabel, .node.key .nodeLabel p { color: ' + t.accent + ' !important; font-weight: 600; }',
      'p { margin: 0; }'
    ].join('\n');
    return t;
  }

  function withKeyClass(src, t) {
    var kind = diagramKind(src);
    if (!/^(flowchart|graph|stateDiagram)/.test(kind) || !/:::\s*key\b|\bclass\s+\S+\s+key\b/.test(src)) return src;
    return src.replace(/\s*$/, '') + '\n  classDef key fill:' + t.card + ',stroke:' + t.accent +
           ',stroke-width:2px,color:' + t.accent + ';\n';
  }

  var NON_ASCII = /[^\x00-\x7f]/;

  function sansKorean(root) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null), nodes = [], n;
    while ((n = walker.nextNode())) {
      if (NON_ASCII.test(n.data) && n.parentElement && n.parentElement.closest('foreignObject')) nodes.push(n);
    }
    nodes.forEach(function (node) {
      var frag = document.createDocumentFragment(), buf = '', kr = false;
      function flush() {
        if (!buf) return;
        if (kr) {
          var s = document.createElement('span');
          s.className = 'kr';
          s.textContent = buf;
          frag.appendChild(s);
        } else {
          frag.appendChild(document.createTextNode(buf));
        }
        buf = '';
      }
      node.data.split(/(\s+)/).forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) { buf += part; return; }
        var isKr = NON_ASCII.test(part);
        if (isKr !== kr) { flush(); kr = isKr; }
        buf += part;
      });
      flush();
      node.parentNode.replaceChild(frag, node);
    });
  }

  function initMermaid() {
    var found = collectFences('mermaid');
    if (!found.length) return;

    var blocks = found.map(function (f) {
      var parts = splitTitle(f.src);
      var fig = document.createElement('figure');
      fig.className = 'diagram-fig';
      var d = document.createElement('div');
      d.className = 'diagram';
      d.setAttribute('data-state', 'pending');
      d.setAttribute('data-src', parts.src);
      fig.appendChild(d);
      if (parts.title) {
        var fc = document.createElement('figcaption');
        fc.innerHTML = inlineMd(parts.title);
        fig.appendChild(fc);
      }
      f.node.parentNode.replaceChild(fig, f.node);
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
        var t = mermaidTheme();
        try {
          window.mermaid.initialize({
            startOnLoad: false,
            securityLevel: 'strict',
            theme: 'base',
            themeVariables: t.vars,
            themeCSS: t.css,
            fontFamily: t.mono,
            flowchart: { curve: 'linear', useMaxWidth: true, htmlLabels: true, nodeSpacing: 34, rankSpacing: 40, padding: 10 },
            sequence: { useMaxWidth: true, mirrorActors: false },
            gantt: { useMaxWidth: true }
          });
          blocks.forEach(function (d, i) {
            d.removeAttribute('data-state');
            var src = withKeyClass(d.getAttribute('data-src'), t);
            window.mermaid.render('mmd-' + Date.now() + '-' + i, src)
              .then(function (res) { d.innerHTML = res.svg; sansKorean(d); })
              .catch(function (e) {
                d.innerHTML = '<div class="diagram-error">' + esc(String(e && e.message || e)) +
                              '\n\n' + esc(src) + '</div>';
              });
          });
        } catch (e) { fail(String(e && e.message || e)); }
      };
      var go = function () {
        var fonts = document.fonts && document.fonts.load
          ? document.fonts.load('13px "IBM Plex Mono"').catch(function () {})
          : Promise.resolve();
        fonts.then(render);
      };
      go();
      document.addEventListener('themechange', go);
      if (window.matchMedia) {
        var mq = window.matchMedia('(prefers-color-scheme: dark)');
        if (mq.addEventListener) mq.addEventListener('change', go);
      }
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

  function inlineMd(s) {
    return String(s || '').split(/(`[^`]*`)/).map(function (part, i) {
      if (i % 2) return '<code>' + esc(part.slice(1, -1)) + '</code>';
      return esc(part)
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/(^|\s)\[(\d+(?:\s*,\s*\d+)*)\]/g, function (m, pre, nums) {
          return pre + nums.split(/\s*,\s*/).map(function (n) {
            return '<cite data-ref="' + n + '"></cite>';
          }).join('');
        });
    }).join('');
  }

  function fenceLines(src) {
    return src.split('\n').map(function (l) { return l.trim(); })
      .filter(function (l) { return l && l.indexOf('//') !== 0; });
  }

  function copyText(text, btn) {
    var label = btn.textContent;
    function done() {
      btn.textContent = '복사했습니다';
      setTimeout(function () { btn.textContent = label; }, 1400);
    }
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(ta);
      done();
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else { fallback(); }
  }

  function fenceHead(title, count, unit, copyLabel, getText) {
    var head = document.createElement('div');
    head.className = 'fence-head';
    head.innerHTML = '<span class="fence-title">' + esc(title) + ' <b>' + count + '</b>' + esc(unit) + '</span>';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'fence-copy';
    btn.textContent = copyLabel;
    btn.addEventListener('click', function () { copyText(getText(), btn); });
    head.appendChild(btn);
    return head;
  }

  var IOC_LABEL = {
    md5: 'MD5', sha1: 'SHA-1', sha256: 'SHA-256', sha512: 'SHA-512',
    ipv4: 'IPv4', ipv6: 'IPv6', cidr: 'CIDR', domain: '도메인', url: 'URL',
    email: '이메일', path: '경로', file: '파일명', reg: '레지스트리', mutex: '뮤텍스',
    ua: 'User-Agent', cve: 'CVE', kve: 'KVE', asn: 'ASN', other: '기타'
  };
  var IOC_KEY = {
    md5: 'md5', sha1: 'sha1', 'sha-1': 'sha1', sha256: 'sha256', 'sha-256': 'sha256',
    sha512: 'sha512', ip: 'ipv4', ipv4: 'ipv4', ipv6: 'ipv6', cidr: 'cidr',
    domain: 'domain', host: 'domain', url: 'url', email: 'email', mail: 'email',
    file: 'file', filename: 'file', path: 'path', reg: 'reg', registry: 'reg',
    mutex: 'mutex', ua: 'ua', cve: 'cve', kve: 'kve', asn: 'asn', other: 'other'
  };
  var FILE_EXT = /\.(exe|dll|sys|scr|bat|cmd|ps1|psm1|vbs|vbe|js|jse|wsf|hta|lnk|msi|msp|cab|chm|jar|apk|dmg|iso|vhdx?|rar|7z|gz|tar|docx?|docm|xlsx?|xlsm|pptx?|pdf|rtf|dat|tmp|elf|dylib|php|aspx|jsp)$/i;

  function refang(s) {
    return s.replace(/\[\.\]|\(\.\)|\{\.\}|\[dot\]/gi, '.')
      .replace(/\[:\]/g, ':')
      .replace(/\[@\]|\[at\]/gi, '@')
      .replace(/^hxxp(s?):\/\//i, 'http$1://')
      .replace(/^fxp:\/\//i, 'ftp://');
  }

  function iocType(v) {
    if (/^[a-f0-9]{32}$/i.test(v)) return 'md5';
    if (/^[a-f0-9]{40}$/i.test(v)) return 'sha1';
    if (/^[a-f0-9]{64}$/i.test(v)) return 'sha256';
    if (/^[a-f0-9]{128}$/i.test(v)) return 'sha512';
    if (/^CVE-\d{4}-\d{4,}$/i.test(v)) return 'cve';
    if (/^KVE-\d{4}-\d{4,}$/i.test(v)) return 'kve';
    if (/^AS\d+$/i.test(v)) return 'asn';
    if (/^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/.test(v)) return 'cidr';
    if (/^(\d{1,3}\.){3}\d{1,3}(:\d+)?$/.test(v)) return 'ipv4';
    if (/^[0-9a-f]*:[0-9a-f]*:[0-9a-f:]*$/i.test(v)) return 'ipv6';
    if (/^[a-z][a-z0-9+.-]*:\/\//i.test(v)) return 'url';
    if (/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(v)) return 'email';
    if (/^(HKLM|HKCU|HKCR|HKU|HKCC|HKEY_)/i.test(v)) return 'reg';
    if (/^([a-z]:\\|\\\\|%[a-z_]+%|\/)/i.test(v)) return 'path';
    if (FILE_EXT.test(v)) return 'file';
    if (/^([a-z0-9-]+\.)+[a-z]{2,}$/i.test(v)) return 'domain';
    return 'other';
  }

  function defang(type, v) {
    if (type === 'url') {
      return v.replace(/^http/i, 'hxxp').replace(/^ftp/i, 'fxp')
        .replace(/^([a-z]+:\/\/)([^\/?#]+)/i, function (m, p, host) { return p + host.replace(/\./g, '[.]'); });
    }
    if (type === 'domain' || type === 'ipv4' || type === 'cidr') return v.replace(/\./g, '[.]');
    if (type === 'email') return v.replace('@', '[@]').replace(/\./g, '[.]');
    return v;
  }

  function renderIoc(src) {
    var rows = [];
    fenceLines(src).forEach(function (line) {
      var g = line.match(/^\[(.+)\]$/);
      if (g) { rows.push({ group: g[1].trim() }); return; }
      var note = '';
      var bar = line.indexOf('|');
      if (bar >= 0) { note = line.slice(bar + 1).trim(); line = line.slice(0, bar).trim(); }
      var type = null, value = line;
      var sp = line.indexOf(' ');
      if (sp > 0) {
        var kw = line.slice(0, sp).toLowerCase().replace(/:$/, '');
        if (IOC_KEY[kw]) { type = IOC_KEY[kw]; value = line.slice(sp + 1).trim(); }
      }
      value = refang(value);
      rows.push({ type: type || iocType(value), value: value, note: note });
    });
    var items = rows.filter(function (r) { return !r.group; });
    if (!items.length) throw new Error('지표를 한 줄도 찾지 못했습니다.');

    var fig = document.createElement('figure');
    fig.className = 'fence ioc';
    fig.appendChild(fenceHead('침해 지표', items.length, '건', '전체 복사', function () {
      return items.map(function (r) { return defang(r.type, r.value); }).join('\n');
    }));
    var html = '<div class="fence-scroll"><table><thead><tr><th>유형</th><th>지표</th><th>비고</th></tr></thead><tbody>';
    rows.forEach(function (r) {
      if (r.group) { html += '<tr class="fence-group"><th colspan="3">' + esc(r.group) + '</th></tr>'; return; }
      var shown = '<code>' + esc(defang(r.type, r.value)) + '</code>';
      if (r.type === 'cve' || r.type === 'kve') {
        var vid = r.value.toUpperCase();
        shown = '<a class="vuln" data-vuln="' + esc(vid) + '" href="' + esc(vulnUrl(vid, null)) + '" rel="noopener">' + shown + '</a>';
      }
      html += '<tr><td class="ioc-type">' + esc(IOC_LABEL[r.type] || r.type) + '</td>' +
        '<td class="ioc-val">' + shown + '</td>' +
        '<td>' + inlineMd(r.note) + '</td></tr>';
    });
    fig.insertAdjacentHTML('beforeend', html + '</tbody></table></div>');
    return fig;
  }

  function renderTimeline(src) {
    var ol = document.createElement('ol');
    ol.className = 'timeline';
    var n = 0;
    fenceLines(src).forEach(function (line) {
      var li = document.createElement('li');
      var g = line.match(/^\[(.+)\]$/);
      if (g) { li.className = 'tl-group'; li.textContent = g[1].trim(); ol.appendChild(li); return; }
      if (line.charAt(0) === '*') { li.className = 'key'; line = line.slice(1).trim(); }
      var p = line.split('|').map(function (s) { return s.trim(); });
      var html = '<time>' + esc(p[0] || '') + '</time><div class="tl-body"><p>' + inlineMd(p[1] || '') + '</p>';
      if (p.length > 2) html += '<span class="tl-tag">' + esc(p.slice(2).join(' · ')) + '</span>';
      li.innerHTML = html + '</div>';
      ol.appendChild(li);
      n++;
    });
    if (!n) throw new Error('사건을 한 줄도 찾지 못했습니다.');
    return ol;
  }

  var TECH_ID = /^T\d{4}(\.\d{3})?$/i;

  function attackUrl(id) {
    var m = id.toUpperCase().match(/^T(\d{4})(?:\.(\d{3}))?$/);
    return 'https://attack.mitre.org/techniques/T' + m[1] + (m[2] ? '/' + m[2] : '') + '/';
  }

  function renderAttack(src) {
    var rows = [];
    fenceLines(src).forEach(function (line) {
      var p = line.split('|').map(function (s) { return s.trim(); });
      var at = -1;
      for (var i = 0; i < p.length; i++) { if (TECH_ID.test(p[i])) { at = i; break; } }
      if (at < 0) return;
      rows.push({
        tactic: p.slice(0, at).join(' '),
        id: p[at].toUpperCase(),
        name: p[at + 1] || '',
        why: p.slice(at + 2).join(' | ')
      });
    });
    if (!rows.length) throw new Error('기법 ID(T1234 또는 T1234.001)를 찾지 못했습니다.');

    var withTactic = rows.some(function (r) { return r.tactic; });
    var fig = document.createElement('figure');
    fig.className = 'fence attack';
    fig.appendChild(fenceHead('ATT&CK 매핑', rows.length, '개 기법', 'ID 복사', function () {
      return rows.map(function (r) { return r.id; }).join('\n');
    }));
    var html = '<div class="fence-scroll"><table><thead><tr>' + (withTactic ? '<th>전술</th>' : '') +
      '<th>기법 ID</th><th>기법</th><th>근거</th></tr></thead><tbody>';
    var last = null;
    rows.forEach(function (r) {
      html += '<tr>';
      if (withTactic) {
        html += '<td class="att-tactic">' + (r.tactic !== last ? esc(r.tactic) : '') + '</td>';
        last = r.tactic;
      }
      html += '<td class="att-id"><a class="att" data-attack="' + esc(r.id) + '" href="' + attackUrl(r.id) +
        '" rel="noopener"><code>' + esc(r.id) + '</code></a></td>' +
        '<td class="att-name">' + esc(r.name) + '</td><td>' + inlineMd(r.why) + '</td></tr>';
    });
    fig.insertAdjacentHTML('beforeend', html + '</tbody></table></div>');
    return fig;
  }

  function initFences() {
    [['ioc', renderIoc, '침해 지표를 그리지 못했습니다.'],
     ['timeline', renderTimeline, '타임라인을 그리지 못했습니다.'],
     ['attack', renderAttack, 'ATT&CK 매핑을 그리지 못했습니다.']].forEach(function (spec) {
      collectFences(spec[0]).forEach(function (f) {
        var node;
        try {
          node = spec[1](f.src);
        } catch (e) {
          node = document.createElement('div');
          node.className = 'diagram-error';
          node.textContent = spec[2] + ' ' + String(e && e.message || e) + '\n\n' + f.src;
        }
        f.node.parentNode.replaceChild(node, f.node);
      });
    });
  }

  var ATT_SRC = '(TA\\d{4}|T\\d{4}(?:\\.\\d{3})?|[GSCM]\\d{4})';
  var ATT_ONE = new RegExp('\\b' + ATT_SRC + '\\b');
  var ATT_SECTION = { T: 'techniques', TA: 'tactics', G: 'groups', S: 'software', C: 'campaigns', M: 'mitigations' };

  function attKind(id) { return id.slice(0, 2) === 'TA' ? 'TA' : id.charAt(0); }

  function attUrl(id) {
    var k = attKind(id);
    if (k === 'T') {
      var p = id.split('.');
      return 'https://attack.mitre.org/techniques/' + p[0] + (p[1] ? '/' + p[1] : '') + '/';
    }
    return 'https://attack.mitre.org/' + ATT_SECTION[k] + '/' + id + '/';
  }

  function attName(db, id) {
    if (!db) return '';
    var v = (db[ATT_SECTION[attKind(id)]] || {})[id];
    return v ? (typeof v === 'string' ? v : v.name) : '';
  }

  var VULN_SRC = '((?:[Cc][Vv][Ee]|[Kk][Vv][Ee])-\\d{4}-\\d{4,7})';
  var VULN_ONE = new RegExp('\\b' + VULN_SRC + '\\b');
  var KNVD_LIST = 'https://knvd.krcert.or.kr/info/vuln/public';

  function vulnUrl(id, vulns) {
    if (id.slice(0, 3) === 'CVE') return 'https://nvd.nist.gov/vuln/detail/' + id;
    var v = vulns && vulns[id];
    return v && v.url ? v.url : KNVD_LIST;
  }

  function loadData() {
    var text = $$('.report-body, .abstract').map(function (el) { return el.textContent; }).join('\n');
    var needAtt = !!$('a.att[data-attack]') || ATT_ONE.test(text);
    var needVuln = !!$('a.vuln[data-vuln]') || VULN_ONE.test(text);
    if (!window.fetch || (!needAtt && !needVuln)) return Promise.resolve({ attack: null, vulns: null });
    function get(u) {
      return fetch(u).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
    }
    return Promise.all([needAtt ? get('/assets/data/attack.json' + ASSET_V) : null, needVuln ? get('/assets/data/vulns.json' + ASSET_V) : null])
      .then(function (r) { return { attack: r[0], vulns: r[1] }; });
  }

  function idLink(cls, attr, id, href, text) {
    var a = document.createElement('a');
    a.className = cls;
    a.href = href;
    a.rel = 'noopener';
    a.setAttribute(attr, id);
    a.textContent = text;
    return a;
  }

  function linkIds(data) {
    var skip = 'pre, code, a, cite, .fence-head, .diagram, .chart, script, style';
    $$('.report-body, .abstract').forEach(function (root) {
      var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
      var nodes = [];
      while (walker.nextNode()) {
        var n = walker.currentNode;
        if ((ATT_ONE.test(n.nodeValue) || VULN_ONE.test(n.nodeValue)) &&
            !(n.parentElement && n.parentElement.closest(skip))) nodes.push(n);
      }
      nodes.forEach(function (node) {
        var text = node.nodeValue, frag = document.createDocumentFragment();
        var re = new RegExp('\\b(?:' + ATT_SRC + '|' + VULN_SRC + ')\\b', 'g'), last = 0, hit = false, m;
        while ((m = re.exec(text))) {
          var link;
          if (m[1]) {
            if (!attName(data.attack, m[1])) continue;
            link = idLink('att', 'data-attack', m[1], attUrl(m[1]), m[1]);
          } else {
            var vid = m[2].toUpperCase();
            link = idLink('vuln', 'data-vuln', vid, vulnUrl(vid, data.vulns), m[2]);
          }
          hit = true;
          frag.appendChild(document.createTextNode(text.slice(last, m.index)));
          frag.appendChild(link);
          last = m.index + m[0].length;
        }
        if (!hit) return;
        frag.appendChild(document.createTextNode(text.slice(last)));
        node.parentNode.replaceChild(frag, node);
      });
    });
  }

  function normUrl(u) {
    return String(u || '').toLowerCase().replace(/^https?:\/\//, '').replace(/\/+$/, '');
  }

  function ensureReferences() {
    var section = document.getElementById('references');
    if (!section) {
      var before = document.getElementById('revisions') || $('.provenance');
      if (!before) return null;
      section = document.createElement('section');
      section.id = 'references';
      section.className = 'references';
      section.innerHTML = '<h2 class="no-number">참고자료</h2><ol class="reflist"></ol>';
      before.parentNode.insertBefore(section, before);
    }
    var bar = $('.toolbar');
    if (bar && !$('#ref-toggle')) {
      var b = document.createElement('button');
      b.type = 'button';
      b.id = 'ref-toggle';
      b.setAttribute('aria-expanded', 'false');
      b.textContent = '참고자료 따로 보기';
      bar.insertBefore(b, bar.lastElementChild);
    }
    return $('ol.reflist', section);
  }

  function initAutoRefs(data) {
    var att = data.attack, vulns = data.vulns;
    if (att) {
      $$('.att-id a.att').forEach(function (a) {
        var cell = a.closest('td').nextElementSibling;
        if (cell && cell.classList.contains('att-name') && !cell.textContent.trim()) {
          cell.textContent = attName(att, a.getAttribute('data-attack'));
        }
      });
    }
    linkIds(data);
    var links = $$('a.att[data-attack], a.vuln[data-vuln]');
    if (!links.length) return;
    var ol = ensureReferences();
    if (!ol) return;

    var byUrl = {}, byName = {};
    var idRe = new RegExp('\\b(?:' + ATT_SRC + '|' + VULN_SRC + ')\\b', 'g');
    $$('li', ol).forEach(function (li) {
      var t = $('.t', li);
      if (!li.id || !t) return;
      if (t.getAttribute('href')) byUrl[normUrl(t.getAttribute('href'))] = li.id;
      var m;
      idRe.lastIndex = 0;
      while ((m = idRe.exec(t.textContent))) byName[(m[1] || m[2]).toUpperCase()] = li.id;
    });

    var count = $$('li', ol).length, made = {};
    var ver = att && att.version ? ' · ATT&CK v' + att.version : '';
    links.forEach(function (a) {
      var isAtt = a.hasAttribute('data-attack');
      var id = a.getAttribute(isAtt ? 'data-attack' : 'data-vuln').toUpperCase();
      var cve = !isAtt && id.slice(0, 3) === 'CVE';
      var v = (!isAtt && vulns && vulns[id]) || {};
      var url = isAtt ? attUrl(id) : vulnUrl(id, vulns);
      var exact = isAtt || cve || !!v.url;
      var ref = byName[id] || (exact && byUrl[normUrl(url)]) || made[id];
      if (!ref) {
        var title, meta, source;
        if (isAtt) {
          var name = attName(att, id);
          title = name ? name + ' (' + id + ')' : id;
          source = 'MITRE ATT&CK';
          meta = source + ver;
        } else {
          title = v.title ? v.title + ' (' + id + ')' : id;
          source = cve ? 'NVD' : 'KISA';
          meta = cve ? 'NVD' : 'KISA 사이버 보안 취약점 정보 포털';
          if (v.cvss != null) meta += ' · CVSS ' + Number(v.cvss).toFixed(1) + (v.severity ? ' ' + v.severity : '');
          if (v.published) meta += ' · 공개 ' + v.published;
        }
        count++;
        var li = document.createElement('li');
        li.id = 'ref-' + count;
        li.className = 'auto';
        li.setAttribute('data-source', source);
        li.setAttribute('data-date', '');
        li.innerHTML = '<a class="t" href="' + esc(url) + '" rel="noopener">' + esc(title) +
          '</a><span class="meta">' + esc(meta) + '</span>';
        ol.appendChild(li);
        ref = made[id] = li.id;
      }
      var own = $('#' + ref + ' .t');
      if (byName[id] && own && own.getAttribute('href')) a.href = own.getAttribute('href');
      else if (!isAtt) a.href = url;
      a.setAttribute('data-ref', ref);
    });
  }

  function initKindFilter() {
    var items = $$('.ledger > li[data-kind]');
    if (items.length < 2) return;
    var counts = {}, order = [];
    items.forEach(function (li) {
      var k = li.getAttribute('data-kind');
      if (!counts[k]) { counts[k] = 0; order.push(k); }
      counts[k]++;
    });
    if (order.length < 2) return;
    var anchor = $('.section-rule') || $('.ledger');
    if (!anchor) return;

    var bar = document.createElement('div');
    bar.className = 'kind-filter';
    bar.setAttribute('role', 'toolbar');
    bar.setAttribute('aria-label', '종류별로 보기');
    function button(k, label, n) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('data-k', k);
      b.innerHTML = esc(label) + '<span class="n">' + n + '</span>';
      return b;
    }
    bar.appendChild(button('', '전체', items.length));
    order.forEach(function (k) { bar.appendChild(button(k, k, counts[k])); });
    anchor.parentNode.insertBefore(bar, anchor);

    function apply(k) {
      $$('button', bar).forEach(function (b) {
        b.setAttribute('aria-pressed', String(b.getAttribute('data-k') === k));
      });
      items.forEach(function (li) { li.hidden = !!k && li.getAttribute('data-kind') !== k; });
      $$('.ledger').forEach(function (ul) {
        var any = $$('li', ul).some(function (li) { return !li.hidden; });
        ul.hidden = !any;
        var rule = ul.previousElementSibling;
        if (rule && rule.classList.contains('section-rule')) rule.hidden = !any;
      });
    }
    bar.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      var k = b.getAttribute('data-k');
      history.replaceState(null, '', k ? '#k=' + encodeURIComponent(k) : location.pathname + location.search);
      apply(k);
    });
    var m = location.hash.match(/^#k=(.+)$/);
    var start = m ? decodeURIComponent(m[1]) : '';
    apply(counts[start] ? start : '');
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
      a.innerHTML = '<span class="rn">' + esc(n) + '</span><span class="rs">' + esc(date ? src + ' ' + date : src) + '</span>';
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

  var MARKS = [['==', 'mark'], ['++', 'u'], ['~~', 'del']];
  var MARK_SKIP = 'pre, code, kbd, samp, script, style, textarea, .fence-head, .diagram, .chart';
  var MARK_BLOCK = 'p, li, td, th, dt, dd, h1, h2, h3, h4, h5, h6, figcaption, caption, blockquote, summary, div, section';

  function markRe(d) {
    var c = '\\' + d.charAt(0);
    return new RegExp('(^|[^\\w' + c + '])' + c + c + '(?=[^\\s' + c + '])([\\s\\S]*?[^\\s' + c + '])' +
                      c + c + '(?![\\w' + c + '])', 'g');
  }

  function blockText(block) {
    var nodes = [], walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT, null), n;
    while ((n = walker.nextNode())) {
      var pe = n.parentElement;
      if (!n.data || !pe || pe.closest(MARK_SKIP)) continue;
      if ((pe.closest(MARK_BLOCK) || block) !== block) continue;
      nodes.push(n);
    }
    return nodes;
  }

  function textAt(nodes, starts, pos) {
    for (var i = nodes.length - 1; i >= 0; i--) {
      if (starts[i] <= pos) return { n: nodes[i], o: pos - starts[i] };
    }
    return null;
  }

  function wrapMark(nodes, starts, open, close, tag) {
    var a = textAt(nodes, starts, open), b = textAt(nodes, starts, close);
    if (!a || !b || a.o + 2 > a.n.data.length || b.o + 2 > b.n.data.length) return;
    b.n.deleteData(b.o, 2);
    a.n.deleteData(a.o, 2);
    var r = document.createRange();
    r.setStart(a.n, a.o);
    r.setEnd(b.n, b.n === a.n ? b.o - 2 : b.o);
    var el = document.createElement(tag);
    el.appendChild(r.extractContents());
    r.insertNode(el);
  }

  function markBlock(block) {
    MARKS.forEach(function (m) {
      var nodes = blockText(block), starts = [], text = '';
      nodes.forEach(function (n) { starts.push(text.length); text += n.data; });
      if (text.indexOf(m[0]) < 0) return;
      var re = markRe(m[0]), hits = [], x;
      while ((x = re.exec(text))) {
        if (x[2].length > 600) continue;
        var open = x.index + x[1].length;
        hits.push([open, open + 2 + x[2].length]);
      }
      for (var i = hits.length - 1; i >= 0; i--) wrapMark(nodes, starts, hits[i][0], hits[i][1], m[1]);
    });
  }

  function initMarks() {
    $$('.report-body, .abstract').forEach(function (root) {
      if (!/==|\+\+|~~/.test(root.textContent)) return;
      [root].concat($$(MARK_BLOCK, root)).forEach(function (block) {
        if (!block.closest(MARK_SKIP)) markBlock(block);
      });
    });
  }

  function initFigures() {
    $$('.report-body p').forEach(function (p) {
      var kids = Array.prototype.filter.call(p.childNodes, function (n) {
        return n.nodeType === 1 || (n.nodeType === 3 && n.data.trim());
      });
      if (kids.length !== 1 || kids[0].nodeType !== 1) return;
      var k = kids[0], img = null;
      if (k.tagName === 'IMG') img = k;
      else if (k.tagName === 'A' && k.children.length === 1 && k.firstElementChild.tagName === 'IMG' &&
               !k.textContent.trim()) img = k.firstElementChild;
      if (!img) return;
      var cap = (img.getAttribute('title') || img.getAttribute('alt') || '').trim();
      if (/^(alt text|image|이미지)$/i.test(cap)) cap = '';
      var fig = document.createElement('figure');
      fig.className = 'shot';
      p.parentNode.insertBefore(fig, p);
      fig.appendChild(k);
      p.parentNode.removeChild(p);
      img.removeAttribute('title');
      if (!img.hasAttribute('loading')) img.setAttribute('loading', 'lazy');
      if (cap) {
        var fc = document.createElement('figcaption');
        fc.innerHTML = inlineMd(cap);
        fig.appendChild(fc);
      }
    });
  }

  function initZoom() {
    var imgs = $$('.report-body img').filter(function (img) {
      return !img.closest('a, .chart, .diagram');
    });
    if (!imgs.length) return;
    var box = document.createElement('div');
    box.className = 'zoom';
    box.hidden = true;
    box.tabIndex = -1;
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', '그림 크게 보기');
    box.innerHTML = '<img alt=""><p class="zoom-cap"></p>';
    document.body.appendChild(box);
    var big = $('img', box), cap = $('.zoom-cap', box), last = null;

    function close() {
      box.hidden = true;
      big.removeAttribute('src');
      document.documentElement.classList.remove('is-zoomed');
      if (last) last.focus();
    }
    function open(img) {
      last = img;
      big.src = img.currentSrc || img.src;
      big.alt = img.alt || '';
      var fig = img.closest('figure'), fc = fig && $('figcaption', fig);
      var n = fc ? $$('.report-body figcaption').indexOf(fc) + 1 : 0;
      cap.textContent = fc ? '그림 ' + n + ' · ' + fc.textContent : (img.alt || '');
      box.hidden = false;
      document.documentElement.classList.add('is-zoomed');
      box.focus();
    }
    imgs.forEach(function (img) {
      img.classList.add('zoomable');
      img.tabIndex = 0;
      img.addEventListener('click', function () { open(img); });
      img.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(img); }
      });
    });
    box.addEventListener('click', close);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !box.hidden) close();
    });
  }

  function initToTop() {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'to-top';
    btn.title = '맨 위로';
    btn.setAttribute('aria-label', '맨 위로');
    btn.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 2.5h10M8 14V6M4.5 9.5 8 6l3.5 3.5"/></svg>';
    document.body.appendChild(btn);
    var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var ticking = false;
    function update() {
      ticking = false;
      btn.classList.toggle('on', window.scrollY > window.innerHeight * 0.9);
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: still ? 'auto' : 'smooth' });
      var h = $('.report-head h1') || $('#main');
      if (h) {
        if (!h.hasAttribute('tabindex')) h.setAttribute('tabindex', '-1');
        h.focus({ preventScroll: true });
      }
    });
    update();
  }

  function initProgress() {
    if (!$('.report-body') || !$('.report-head')) return;
    var bar = document.createElement('div');
    bar.className = 'read-progress';
    bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);
    var ticking = false;
    function update() {
      ticking = false;
      var max = document.documentElement.scrollHeight - window.innerHeight;
      var p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update);
    update();
  }

  function noDrag() {
    document.addEventListener('dragstart', function (e) {
      var t = e.target;
      if (!(t && t.closest && t.closest('[draggable="true"]'))) e.preventDefault();
    });
  }

  function busy(on) {
    if (on) document.documentElement.setAttribute('aria-busy', 'true');
    else document.documentElement.removeAttribute('aria-busy');
  }

  function boot() {
    busy(true);
    setTimeout(function () { busy(false); }, 4000);
    initTheme();
    noDrag();
    initProgress();
    initToTop();
    initMermaid();
    initCharts();
    initFences();
    initFigures();
    initMarks();

    loadData()
      .then(function (data) { initAutoRefs(data); })
      .catch(function () {})
      .then(function () {
        initCitations();
        headingAnchors();
        buildToc();
        buildRevisions();
        wrapTables();
        footnotePopovers();
        initRefPanel();
        initKindFilter();
        initZoom();

        $$('[data-print]').forEach(function (el) {
          el.addEventListener('click', function () { window.print(); });
        });
        busy(false);
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else { boot(); }
})();
