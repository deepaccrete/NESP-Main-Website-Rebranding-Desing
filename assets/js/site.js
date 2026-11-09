/* Nigeria SE4ALL — shared script for inner pages
   (homepage keeps its own inline script for the hero map). */
(function () {
    'use strict';
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    var $ = function (s, r) { return (r || document).querySelector(s); };
    var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

    var yr = $('#yr'); if (yr) yr.textContent = new Date().getFullYear();

    /* ---------- header ---------- */
    var hdr = $('#hdr');
    if (hdr) {
        var onScroll = function () { hdr.classList.toggle('solid', scrollY > 40 || hdr.classList.contains('menu-open') || document.body.classList.contains('hdr-solid')); };
        addEventListener('scroll', onScroll, { passive: true }); onScroll();
    }

    /* ---------- dropdown & mobile menu ---------- */
    var dd = $('#dd');
    var mnav = $('#mnav'), burger = $('.burger');
    var setM = function (o) { if (!mnav) return; mnav.hidden = !o; hdr.classList.toggle('menu-open', o); burger.setAttribute('aria-expanded', o); if (o) hdr.classList.add('solid'); else onScroll && onScroll(); };
    if (dd) {
        var ddBtn = dd.querySelector('.dd-btn');
        var setDD = function (o) { dd.classList.toggle('open', o); ddBtn.setAttribute('aria-expanded', o); };
        ddBtn.addEventListener('click', function (e) { e.stopPropagation(); setDD(!dd.classList.contains('open')); });
        dd.addEventListener('mouseenter', function () { setDD(true); });
        dd.addEventListener('mouseleave', function () { setDD(false); });
        document.addEventListener('click', function (e) { if (!dd.contains(e.target)) setDD(false); });
        document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { setDD(false); setM(false); } });
    }
    if (burger && mnav) {
        burger.setAttribute('aria-expanded', 'false'); burger.setAttribute('aria-controls', 'mnav');
        burger.addEventListener('click', function () { setM(mnav.hidden); });
        $$('a', mnav).forEach(function (a) { a.addEventListener('click', function () { setM(false); }); });
    }

    /* ---------- scroll reveal (content stays visible if JS or IO is missing) ---------- */
    if ('IntersectionObserver' in window && !reduce) {
        var rio = new IntersectionObserver(function (es) {
            es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); rio.unobserve(e.target); } });
        }, { threshold: 0.1, rootMargin: '0px 0px -6% 0px' });
        $$('[data-reveal]').forEach(function (group) {
            var kids = group.dataset.reveal === 'self' ? [group] : Array.prototype.slice.call(group.children);
            kids.forEach(function (el, i) {
                el.classList.add('reveal');
                el.style.setProperty('--d', Math.min(i * 0.07, 0.42).toFixed(2) + 's');
                rio.observe(el);
            });
        });
    }

    /* ---------- scroll-spy for sub-navs ---------- */
    $$('[data-spy]').forEach(function (nav) {
        var links = $$('a[href^="#"]', nav);
        var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); }).filter(Boolean);
        var spy = function () {
            var y = scrollY + 160, cur = null;
            targets.forEach(function (t) { if (t.offsetTop <= y) cur = t.id; });
            links.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + cur); });
            var on = links.filter(function (a) { return a.classList.contains('on'); })[0];
            if (on && nav.classList.contains('subnav-scroll') && on.scrollIntoView && nav.dataset.last !== cur) {
                nav.dataset.last = cur;
                var box = on.parentNode; box.scrollTo({ left: on.offsetLeft - 20, behavior: reduce ? 'auto' : 'smooth' });
            }
        };
        addEventListener('scroll', spy, { passive: true }); spy();
    });

    /* ---------- blog filters ---------- */
    var filt = $('.filters');
    if (filt) {
        var btns = $$('button', filt), cards = $$('[data-cat]'), cnt = $('.count', filt);
        var apply = function (cat) {
            var n = 0;
            cards.forEach(function (c) { var show = cat === 'all' || c.dataset.cat.split(' ').indexOf(cat) > -1; c.classList.toggle('hide', !show); if (show) n++; });
            btns.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.f === cat); });
            if (cnt) cnt.textContent = n + (n === 1 ? ' post' : ' posts');
        };
        btns.forEach(function (b) { b.addEventListener('click', function () { apply(b.dataset.f); }); });
        var q = (location.hash || '').replace('#', '');
        apply(['mg', 'ps', 'shs'].indexOf(q) > -1 ? q : 'all');
    }

    /* ---------- share: copy link ---------- */
    $$('[data-copy]').forEach(function (b) {
        b.addEventListener('click', function () {
            var done = function () { var t = b.parentNode.querySelector('.copied'); if (t) { t.classList.add('show'); setTimeout(function () { t.classList.remove('show'); }, 1800); } };
            try { navigator.clipboard.writeText(location.href).then(done, done); } catch (e) { done(); }
        });
    });

    /* ---------- charts (power sector) ---------- */
    var NS = 'http://www.w3.org/2000/svg';
    function el(tag, attrs, parent) { var n = document.createElementNS(NS, tag); for (var k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; }
    var fmt = function (v) { return Math.round(v).toLocaleString('en-NG'); };
    function niceStep(raw) { var p = Math.pow(10, Math.floor(Math.log10(raw))); return [1, 2, 2.5, 5, 10].map(function (x) { return x * p; }).filter(function (x) { return x >= raw; })[0]; }

    function barChart(host, cfg) {
        var W = Math.max(300, Math.round(host.clientWidth || 640)), H = W < 480 ? 240 : 280, L = 50, R = 8, T = 18, B = 30;
        var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': cfg.label });
        var n = cfg.years.length;
        var totals = cfg.years.map(function (_, i) { return cfg.series.reduce(function (a, s) { return a + (s.values[i] || 0); }, 0); });
        var peak = Math.max(cfg.target || 0, Math.max.apply(null, totals)), step = niceStep(peak / 4), ticks = Math.ceil(peak / step), max = step * ticks;
        var y = function (v) { return T + (H - T - B) * (1 - v / max); };
        var g = el('g', { 'class': 'grid' }, svg);
        for (var i = 0; i <= ticks; i++) {
            var v = step * i, yy = y(v);
            el('line', { x1: L, x2: W - R, y1: yy, y2: yy }, g);
            var t = el('text', { x: L - 8, y: yy + 4, 'text-anchor': 'end' }, svg); t.textContent = fmt(v) + (cfg.suffix || '');
        }
        var bw = (W - L - R) / n, pad = bw * 0.22;
        var tip = host.parentNode.querySelector('.chart-tip');
        cfg.years.forEach(function (yr, i) {
            var col = el('g', { 'class': 'col' }, svg), acc = 0;
            cfg.series.forEach(function (s) {
                var v = s.values[i] || 0; if (!v) return;
                var y0 = y(acc), y1 = y(acc + v); acc += v;
                el('rect', { x: L + i * bw + pad / 2, y: y1, width: bw - pad, height: Math.max(0, y0 - y1 - (cfg.series.length > 1 ? 1 : 0)), rx: 3, fill: s.color }, col);
            });
            var lab = el('text', { x: L + i * bw + bw / 2, y: H - B + 18, 'text-anchor': 'middle', opacity: (bw < 26 && i % 2) ? 0 : 1 }, svg); lab.textContent = (bw < 44 ? "'" + String(yr).slice(2) : yr);
            var hit = el('rect', { x: L + i * bw, y: T, width: bw, height: H - T - B, fill: 'transparent' }, col);
            if (tip) {
                var show = function () {
                    var rows = cfg.series.filter(function (s) { return s.values[i]; }).map(function (s) { return '<div><i style="background:' + s.color + '"></i>' + s.name + ': ' + fmt(s.values[i]) + (cfg.suffix || '') + '</div>'; }).join('');
                    tip.innerHTML = '<b>' + yr + '</b>' + (rows || '<div>No data</div>');
                    var r = host.getBoundingClientRect(), pr = host.parentNode.getBoundingClientRect();
                    var sc = r.width / W;
                    tip.style.left = (r.left - pr.left + (L + i * bw + bw / 2) * sc) + 'px';
                    tip.style.top = (r.top - pr.top + y(totals[i]) * sc) + 'px';
                    tip.classList.add('show');
                };
                hit.addEventListener('mouseenter', show); hit.addEventListener('focus', show);
                hit.addEventListener('mouseleave', function () { tip.classList.remove('show'); });
            }
        });
        if (cfg.target) {
            var ty = y(cfg.target);
            el('line', { 'class': 'tgt', x1: L, x2: W - R, y1: ty, y2: ty }, svg);
            var tl = el('text', { 'class': 'tgt-l', x: W - R, y: ty - 7, 'text-anchor': 'end' }, svg); tl.textContent = cfg.targetLabel;
        }
        host.appendChild(svg);
    }

    function gauge(host, value, target, max) {
        var W = 200, H = 120, cx = 100, cy = 104, r = 82;
        var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': host.dataset.label });
        var pt = function (f) { var a = Math.PI * (1 - f); return [cx + r * Math.cos(a), cy - r * Math.sin(a)]; };
        var arc = function (f0, f1) { var a = pt(f0), b = pt(f1); return 'M' + a[0] + ' ' + a[1] + ' A' + r + ' ' + r + ' 0 ' + ((f1 - f0) > .5 ? 1 : 0) + ' 1 ' + b[0] + ' ' + b[1]; };
        el('path', { d: arc(0, 1), stroke: '#E6EDE8', 'stroke-width': 16, fill: 'none', 'stroke-linecap': 'round' }, svg);
        var f = Math.min(1, value / max);
        var p = el('path', { d: arc(0, Math.max(f, 0.001)), stroke: '#065F46', 'stroke-width': 16, fill: 'none', 'stroke-linecap': 'round' }, svg);
        var tf = target / max, tp1 = pt(tf), tp2 = [cx + (r + 14) * Math.cos(Math.PI * (1 - tf)), cy - (r + 14) * Math.sin(Math.PI * (1 - tf))], tp0 = [cx + (r - 14) * Math.cos(Math.PI * (1 - tf)), cy - (r - 14) * Math.sin(Math.PI * (1 - tf))];
        el('line', { x1: tp0[0], y1: tp0[1], x2: tp2[0], y2: tp2[1], stroke: '#0F172A', 'stroke-width': 2.5, 'stroke-linecap': 'round' }, svg);
        var t = el('text', { x: cx, y: cy - 18, 'text-anchor': 'middle', 'font-size': 26, 'font-weight': 600, fill: '#0F172A', 'font-family': 'Inter,sans-serif' }, svg);
        t.textContent = host.dataset.display;
        var s = el('text', { x: cx, y: cy + 2, 'text-anchor': 'middle', 'font-size': 11, fill: '#475569', 'font-family': 'Inter,sans-serif' }, svg);
        s.textContent = host.dataset.sub;
        if (!reduce) {
            var len = p.getTotalLength ? p.getTotalLength() : 0;
            if (len) { p.style.strokeDasharray = len; p.style.strokeDashoffset = len; p.getBoundingClientRect(); p.style.transition = 'stroke-dashoffset 1.4s cubic-bezier(.2,.7,.2,1)'; setTimeout(function () { p.style.strokeDashoffset = 0; }, 150); }
        }
        host.appendChild(svg);
    }

    var D = window.SE4ALL_TARGETS;
    if (D) {
        $$('[data-gauge]').forEach(function (h) { var k = D.gauges[h.dataset.gauge]; gauge(h, k.value, k.target, k.max); });
        var draw = function () { $$('[data-chart]').forEach(function (h) { h.innerHTML = ''; barChart(h, D.charts[h.dataset.chart]); }); };
        draw(); var lastW = innerWidth, rt; addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { if (innerWidth !== lastW) { lastW = innerWidth; draw(); } }, 200); });
    }
})();
