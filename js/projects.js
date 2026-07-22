/* Projects filter — leaner sibling of the publications filter.
   Three facets (year / funder / status), no search box. Year is a
   multi-value membership test against each row's data-active-years blob
   (",2024,2025,") — a project spanning 2024–26 surfaces under 2024, 25
   and 26 chips. Funder + status are exact-match single-value sets per
   row. The dropdown plumbing (open/close, outside-click, Escape,
   in-panel Clear, cross-faceted option counts, URL hash sync) mirrors
   publications.js so the two filters read as one family.

   Layout coupling — when no filter is active, the page shows two H2
   sections (Ongoing / Concluded) with cap-6 + show-more under each.
   The moment any chip is selected, isFiltering() adds .is-filtered to
   #projects which folds both groups into one combined list (CSS hides
   both H2 titles + both show-more buttons + the gap). The Status chip
   then becomes the way to re-separate the two within the filter. */
(function () {
    var bar = document.querySelector('.proj-filter-bar');
    if (!bar) return;

    var section = document.getElementById('projects');
    var state = {
        year:   new Set(),
        funder: new Set(),
        status: new Set()
    };
    var rows        = Array.prototype.slice.call(
                        document.querySelectorAll('.proj-status-group .news-row'));
    var groups      = Array.prototype.slice.call(
                        document.querySelectorAll('.proj-status-group'));
    var showMores   = Array.prototype.slice.call(
                        document.querySelectorAll('.proj-show-more'));
    var emptyEl     = document.querySelector('.proj-filter-empty');
    var clearIn     = emptyEl && emptyEl.querySelector('.pub-filter-clear-inline');
    var clearAllBtn = bar.querySelector('.pub-filter-clear');
    var countEl     = bar.querySelector('.pub-filter-count');
    var totalRows   = rows.length;

    /* Collapse extras back to hidden + reset the show-more button label.
       Mirrors the helper in publications.js. */
    function resetShowMore(btn) {
        var group  = btn.closest('.proj-status-group');
        var extras = group ? group.querySelectorAll('.proj-extra-item') : [];
        Array.prototype.forEach.call(extras, function (el) { el.hidden = true; });
        btn.dataset.expanded = 'false';
        btn.setAttribute('aria-expanded', 'false');
        var txt = btn.querySelector('.btn-text');
        if (txt) txt.textContent = 'See ' + extras.length + ' more';
        var svg = btn.querySelector('svg');
        if (svg) svg.style.transform = '';
    }

    /* ── Dropdown wiring (one helper per panel) ─────────────────────── */
    var dropdowns = [];
    function wireDropdown(name, labelText) {
        var dd = bar.querySelector('[data-dropdown="' + name + '"]');
        if (!dd) return null;
        var trigger  = dd.querySelector('.pub-filter-trigger');
        var panel    = dd.querySelector('.pub-filter-panel');
        var label    = dd.querySelector('.pub-filter-trigger-label');
        var countTag = dd.querySelector('.pub-filter-trigger-count');
        var clearBtn = dd.querySelector('.pub-filter-panel-clear');
        var checks   = Array.prototype.slice.call(
                            panel.querySelectorAll('input[type="checkbox"]'));

        function open()   { panel.hidden = false; trigger.setAttribute('aria-expanded', 'true');  dd.classList.add('is-open'); }
        function close()  { panel.hidden = true;  trigger.setAttribute('aria-expanded', 'false'); dd.classList.remove('is-open'); }
        function toggle() { if (panel.hidden) open(); else close(); }

        trigger.addEventListener('click', function (e) {
            e.stopPropagation();
            dropdowns.forEach(function (d) { if (d && d.name !== name) d.close(); });
            toggle();
        });

        checks.forEach(function (cb) {
            cb.addEventListener('change', function () {
                var v = cb.dataset[name];
                if (cb.checked) state[name].add(v);
                else            state[name].delete(v);
                apply();
                syncHash();
            });
        });

        if (clearBtn) {
            clearBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                state[name].clear();
                checks.forEach(function (cb) { cb.checked = false; });
                close();
                trigger.focus();
                apply();
                syncHash();
            });
        }

        function update() {
            var n = state[name].size;
            trigger.classList.toggle('is-active', n > 0);
            if (clearBtn) clearBtn.hidden = n === 0;
            if (n === 0) {
                label.textContent = labelText;
                countTag.hidden = true;
                countTag.textContent = '';
            } else if (n === 1) {
                var only = Array.from(state[name])[0];
                if (name === 'status') {
                    label.textContent = STATUS_LABELS[only] || only;
                } else if (name === 'funder') {
                    label.textContent = FUNDER_LABELS[only] || only;
                } else {
                    label.textContent = only;
                }
                countTag.hidden = true;
            } else {
                label.textContent = labelText;
                countTag.hidden = false;
                countTag.textContent = String(n);
            }
        }

        var api = { name: name, close: close, checks: checks, update: update };
        dropdowns.push(api);
        return api;
    }

    var STATUS_LABELS = { 'ongoing': 'Ongoing', 'concluded': 'Concluded' };
    /* Display labels for funder buckets — internal keys stay short for the
       dataset (data-funder="Ministry"), but the trigger label needs to
       mirror the chip text when a single bucket is selected. */
    var FUNDER_LABELS = { 'NSTC': 'NSTC', 'Intl': 'International', 'Gov': 'Ministry / Gov', 'NTU': 'NTU', 'Industry': 'Industry', 'Foundation': 'Foundations' };

    wireDropdown('year',   'Year');
    wireDropdown('funder', 'Funder');
    wireDropdown('status', 'Status');

    /* Outside click + Escape close every panel uniformly. */
    document.addEventListener('click', function (e) {
        if (!bar.contains(e.target)) {
            dropdowns.forEach(function (d) { d && d.close(); });
        }
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            dropdowns.forEach(function (d) { d && d.close(); });
        }
    });

    /* ── Clear-all ──────────────────────────────────────────────────── */
    function clearAll() {
        state.year.clear();
        state.funder.clear();
        state.status.clear();
        dropdowns.forEach(function (d) {
            if (!d) return;
            d.checks.forEach(function (cb) { cb.checked = false; });
            d.close();
        });
        apply();
        syncHash();
    }
    if (clearAllBtn) clearAllBtn.addEventListener('click', clearAll);
    if (clearIn)     clearIn.addEventListener('click',     clearAll);

    /* ── Apply ──────────────────────────────────────────────────────── */
    function isFiltering() {
        return state.year.size   > 0
            || state.funder.size > 0
            || state.status.size > 0;
    }

    /* Year membership: row carries ",2024,2025,2026," — OR semantics. */
    function yearMatches(blob) {
        if (state.year.size === 0) return true;
        if (!blob) return false;
        var match = false;
        state.year.forEach(function (y) {
            if (blob.indexOf(',' + y + ',') !== -1) match = true;
        });
        return match;
    }

    function rowMatchesExcept(row, excludeDim) {
        var d = row.dataset;
        if (excludeDim !== 'year'   && !yearMatches(d.activeYears))                                  return false;
        if (excludeDim !== 'funder' && state.funder.size > 0 && !state.funder.has(d.funder))         return false;
        if (excludeDim !== 'status' && state.status.size > 0 && !state.status.has(d.status))         return false;
        return true;
    }

    function recomputeOptionCounts() {
        dropdowns.forEach(function (api) {
            if (!api) return;
            var dim = api.name;
            var counts = {};
            rows.forEach(function (row) {
                if (!rowMatchesExcept(row, dim)) return;
                var d = row.dataset;
                if (dim === 'year') {
                    var blob = d.activeYears;
                    if (blob && blob.length > 2) {
                        blob.slice(1, -1).split(',').forEach(function (v) {
                            if (v) counts[v] = (counts[v] || 0) + 1;
                        });
                    }
                } else {
                    var v = d[dim];
                    if (v) counts[v] = (counts[v] || 0) + 1;
                }
            });
            api.checks.forEach(function (input) {
                var val = input.dataset[dim];
                var n = counts[val] || 0;
                var labelEl = input.closest('.pub-filter-check');
                if (!labelEl) return;
                var countSpan = labelEl.querySelector('.pub-filter-check-count');
                if (countSpan) countSpan.textContent = String(n);
                if (n === 0 && !input.checked) labelEl.classList.add('is-empty');
                else                            labelEl.classList.remove('is-empty');
            });
        });
    }

    function apply() {
        var filtering = isFiltering();
        var visibleTotal = 0;

        rows.forEach(function (row) {
            var d = row.dataset;
            var ok = yearMatches(d.activeYears)
                  && (state.funder.size === 0 || state.funder.has(d.funder))
                  && (state.status.size === 0 || state.status.has(d.status));
            row.hidden = !ok;
            /* When filtering, surface matching rows that live inside an
               .proj-extra-item wrapper too. When clear, the wrapper goes
               back to hidden so the collapsed view returns. */
            var wrap = row.closest('.proj-extra-item');
            if (wrap) wrap.hidden = filtering ? !ok : true;
            if (ok) visibleTotal++;
        });

        groups.forEach(function (g) {
            var visible = g.querySelectorAll('.news-row:not([hidden])').length;
            g.hidden = visible === 0;
        });

        showMores.forEach(function (btn) {
            if (filtering) {
                btn.hidden = true;
            } else {
                btn.hidden = false;
                resetShowMore(btn);
            }
        });

        recomputeOptionCounts();
        dropdowns.forEach(function (d) { d && d.update(); });

        /* The CSS class flip is what folds the two H2 groups into one
           combined list (and back). Kept on the section root so any new
           per-group styling stays scoped. */
        if (section) section.classList.toggle('is-filtered', filtering);

        if (clearAllBtn) clearAllBtn.hidden = !filtering;

        if (filtering) {
            countEl.textContent = 'Showing ' + visibleTotal + ' of ' + totalRows;
            countEl.hidden = false;
        } else {
            countEl.textContent = '';
            countEl.hidden = true;
        }

        if (emptyEl) emptyEl.hidden = visibleTotal !== 0;
    }

    /* ── URL hash sync ───────────────────────────────────────────────
       Format: #year=2024,2025&funder=NSTC,NTU&status=ongoing
       Year values are plain 4-digit; funder values are the short bucket
       keys (NSTC, Ministry, NTU, Industry); status uses the slug pair
       (ongoing, concluded). Mirrors the publications.js hash shape so
       the two pages encode state the same way. */
    function syncHash() {
        var parts = [];
        if (state.year.size > 0)   parts.push('year='   + Array.from(state.year).join(','));
        if (state.funder.size > 0) parts.push('funder=' + Array.from(state.funder).map(encodeURIComponent).join(','));
        if (state.status.size > 0) parts.push('status=' + Array.from(state.status).join(','));
        var hash = parts.length ? '#' + parts.join('&') : '';
        try {
            history.replaceState(null, '', hash || window.location.pathname + window.location.search);
        } catch (e) { /* file:// or sandbox — ignore */ }
    }

    /* Restore from URL hash on load. Ticks the matching checkbox in each
       panel so the trigger label and panel state stay in sync with the
       chip dataset, then runs apply() once below. */
    var hash = window.location.hash.slice(1);
    if (hash) {
        hash.split('&').forEach(function (pair) {
            var eq = pair.indexOf('=');
            if (eq < 0) return;
            var k = pair.slice(0, eq);
            var v = pair.slice(eq + 1);
            if (k === 'year') {
                v.split(',').forEach(function (yr) {
                    var dec = decodeURIComponent(yr);
                    state.year.add(dec);
                    var cb = bar.querySelector('.proj-filter-year-input[data-year="' + dec + '"]');
                    if (cb) cb.checked = true;
                });
            } else if (k === 'funder') {
                v.split(',').forEach(function (f) {
                    var dec = decodeURIComponent(f);
                    state.funder.add(dec);
                    var cb = bar.querySelector('.proj-filter-funder-input[data-funder="' + dec + '"]');
                    if (cb) cb.checked = true;
                });
            } else if (k === 'status') {
                v.split(',').forEach(function (s) {
                    state.status.add(s);
                    var cb = bar.querySelector('.proj-filter-status-input[data-status="' + s + '"]');
                    if (cb) cb.checked = true;
                });
            }
        });
    }

    apply();
})();
