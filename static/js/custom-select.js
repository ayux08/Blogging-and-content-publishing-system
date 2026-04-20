/**
 * Custom Select Dropdown — Blogverse
 * Replaces all native <select> elements with fully stylable custom dropdowns.
 * The hidden native <select> is kept in the DOM for form submissions.
 * Uses portal approach: options panel is appended to document.body to avoid
 * stacking context / backdrop-filter clipping issues.
 */
(function () {
    'use strict';

    // Portal container for all dropdown panels
    var portal = document.createElement('div');
    portal.id = 'custom-select-portal';
    portal.style.position = 'fixed';
    portal.style.top = '0';
    portal.style.left = '0';
    portal.style.width = '0';
    portal.style.height = '0';
    portal.style.overflow = 'visible';
    portal.style.zIndex = '99999';
    portal.style.pointerEvents = 'none';
    document.body.appendChild(portal);

    function initCustomSelects() {
        document.querySelectorAll('select').forEach(function (nativeSelect) {
            // Skip if already transformed
            if (nativeSelect.dataset.customized) return;
            nativeSelect.dataset.customized = 'true';

            // Hide native select
            nativeSelect.style.display = 'none';

            // Get classes from native select for sizing context
            var isAdminFilter = nativeSelect.classList.contains('admin-filter-select');
            var isFormControl = nativeSelect.classList.contains('form-control');

            // Create wrapper
            var wrapper = document.createElement('div');
            wrapper.className = 'custom-select-wrapper';
            if (isAdminFilter) wrapper.classList.add('custom-select--admin');
            if (isFormControl) wrapper.classList.add('custom-select--form');

            // Copy inline styles that affect layout (width, etc)
            if (nativeSelect.style.width) wrapper.style.width = nativeSelect.style.width;
            var cssText = nativeSelect.style.cssText || '';
            if (cssText.indexOf('width:auto') !== -1 || cssText.indexOf('width: auto') !== -1) {
                wrapper.style.width = 'auto';
                wrapper.style.display = 'inline-block';
            }

            // Create the display button
            var trigger = document.createElement('div');
            trigger.className = 'custom-select-trigger';
            trigger.setAttribute('tabindex', '0');
            trigger.setAttribute('role', 'combobox');
            trigger.setAttribute('aria-expanded', 'false');

            var triggerText = document.createElement('span');
            triggerText.className = 'custom-select-text';

            var triggerArrow = document.createElement('span');
            triggerArrow.className = 'custom-select-arrow';
            triggerArrow.innerHTML = '<svg width="12" height="12" viewBox="0 0 12 12"><path fill="currentColor" d="M6 8L1 3h10z"/></svg>';

            trigger.appendChild(triggerText);
            trigger.appendChild(triggerArrow);

            // Create options panel (will be appended to portal)
            var optionsPanel = document.createElement('div');
            optionsPanel.className = 'custom-select-options';
            if (isAdminFilter) optionsPanel.classList.add('custom-select-options--admin');
            optionsPanel.style.pointerEvents = 'auto';
            portal.appendChild(optionsPanel);

            // Populate options
            function buildOptions() {
                optionsPanel.innerHTML = '';
                var options = nativeSelect.options;
                for (var i = 0; i < options.length; i++) {
                    var opt = options[i];
                    var item = document.createElement('div');
                    item.className = 'custom-select-option';
                    if (isAdminFilter) item.classList.add('custom-select-option--admin');
                    item.dataset.value = opt.value;
                    item.textContent = opt.textContent;

                    if (opt.disabled) {
                        item.classList.add('disabled');
                    }
                    if (opt.selected) {
                        item.classList.add('selected');
                        triggerText.textContent = opt.textContent;
                    }

                    (function (clickItem) {
                        clickItem.addEventListener('click', function (e) {
                            e.stopPropagation();
                            var val = this.dataset.value;
                            if (this.classList.contains('disabled')) return;

                            // Update native select
                            nativeSelect.value = val;
                            triggerText.textContent = this.textContent;

                            // Update selected class
                            optionsPanel.querySelectorAll('.custom-select-option').forEach(function (o) {
                                o.classList.remove('selected');
                            });
                            this.classList.add('selected');

                            // Close dropdown
                            closeDropdown(wrapper, optionsPanel);

                            // Fire change event on native select
                            var event = new Event('change', { bubbles: true });
                            nativeSelect.dispatchEvent(event);

                            // Handle onchange attribute (e.g. this.form.submit())
                            var onchangeAttr = nativeSelect.getAttribute('onchange');
                            if (onchangeAttr) {
                                try {
                                    var fn = new Function('event', onchangeAttr);
                                    fn.call(nativeSelect, event);
                                } catch (err) {
                                    console.warn('Custom select onchange error:', err);
                                }
                            }
                        });
                    })(item);

                    optionsPanel.appendChild(item);
                }

                // If no option was selected, pick the first
                if (!triggerText.textContent && options.length > 0) {
                    triggerText.textContent = options[0].textContent;
                }
            }

            buildOptions();

            // Store reference from wrapper to panel and vice versa
            wrapper._optionsPanel = optionsPanel;
            optionsPanel._wrapper = wrapper;

            // Toggle dropdown on click
            trigger.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                var isOpen = wrapper.classList.contains('open');
                // Close all other dropdowns first
                closeAllDropdowns();
                if (!isOpen) {
                    openDropdown(wrapper, optionsPanel);
                }
            });

            // Keyboard navigation
            trigger.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    trigger.click();
                } else if (e.key === 'Escape') {
                    closeDropdown(wrapper, optionsPanel);
                } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                    e.preventDefault();
                    if (!wrapper.classList.contains('open')) {
                        openDropdown(wrapper, optionsPanel);
                        return;
                    }
                    var opts = optionsPanel.querySelectorAll('.custom-select-option:not(.disabled)');
                    var currentIdx = -1;
                    opts.forEach(function (o, idx) {
                        if (o.classList.contains('highlighted')) currentIdx = idx;
                    });
                    opts.forEach(function (o) { o.classList.remove('highlighted'); });

                    if (e.key === 'ArrowDown') {
                        currentIdx = (currentIdx + 1) % opts.length;
                    } else {
                        currentIdx = currentIdx <= 0 ? opts.length - 1 : currentIdx - 1;
                    }
                    opts[currentIdx].classList.add('highlighted');
                    opts[currentIdx].scrollIntoView({ block: 'nearest' });
                }
            });

            // Assemble
            wrapper.appendChild(trigger);
            nativeSelect.parentNode.insertBefore(wrapper, nativeSelect.nextSibling);

            // Observe native select for dynamic changes
            var observer = new MutationObserver(function () {
                buildOptions();
            });
            observer.observe(nativeSelect, { childList: true, subtree: true, attributes: true });
        });
    }

    function positionPanel(wrapper, panel) {
        var rect = wrapper.getBoundingClientRect();
        var panelHeight = panel.scrollHeight || 200;
        var spaceBelow = window.innerHeight - rect.bottom;
        var dropUp = spaceBelow < panelHeight + 20 && rect.top > panelHeight;

        panel.style.position = 'fixed';
        panel.style.left = rect.left + 'px';
        panel.style.width = rect.width + 'px';
        panel.style.minWidth = Math.max(rect.width, 160) + 'px';

        if (dropUp) {
            panel.style.top = 'auto';
            panel.style.bottom = (window.innerHeight - rect.top + 6) + 'px';
            panel.classList.add('drop-up');
        } else {
            panel.style.top = (rect.bottom + 6) + 'px';
            panel.style.bottom = 'auto';
            panel.classList.remove('drop-up');
        }
    }

    function openDropdown(wrapper, panel) {
        wrapper.classList.add('open');
        wrapper.querySelector('.custom-select-trigger').setAttribute('aria-expanded', 'true');
        positionPanel(wrapper, panel);
        panel.classList.add('show');
    }

    function closeDropdown(wrapper, panel) {
        wrapper.classList.remove('open');
        wrapper.querySelector('.custom-select-trigger').setAttribute('aria-expanded', 'false');
        panel.classList.remove('show', 'drop-up');
        panel.querySelectorAll('.custom-select-option').forEach(function (o) {
            o.classList.remove('highlighted');
        });
    }

    function closeAllDropdowns() {
        document.querySelectorAll('.custom-select-wrapper.open').forEach(function (w) {
            if (w._optionsPanel) {
                closeDropdown(w, w._optionsPanel);
            }
        });
    }

    // Close on outside click
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.custom-select-wrapper') && !e.target.closest('.custom-select-options')) {
            closeAllDropdowns();
        }
    });

    // Close on ESC
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeAllDropdowns();
    });

    // Reposition on scroll/resize
    window.addEventListener('scroll', function () {
        document.querySelectorAll('.custom-select-wrapper.open').forEach(function (w) {
            if (w._optionsPanel) positionPanel(w, w._optionsPanel);
        });
    }, true);

    window.addEventListener('resize', function () {
        document.querySelectorAll('.custom-select-wrapper.open').forEach(function (w) {
            if (w._optionsPanel) positionPanel(w, w._optionsPanel);
        });
    });

    // Initialise on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCustomSelects);
    } else {
        initCustomSelects();
    }

    // Re-export for dynamic usage
    window.initCustomSelects = initCustomSelects;
})();
