/* eslint-env es11 */
/* jshint esversion: 11 */
/* global document django */

document.addEventListener('DOMContentLoaded' , () => {
    'use strict';

    const updateSelection = (el) => {
        const widget = el.closest('.link-widget');
        const help = widget.closest('.form-row')?.querySelector('div.help');
        widget.dataset.type = el.value;

        if (help) {
            if (el.value === 'empty') {
                help.textContent = el.dataset.help || '';
            } else {
                help.textContent = widget.querySelector(`[widget="${el.value}"]`)?.dataset.help || '';
            }
        }
    };
    for (let item of document.querySelectorAll('.js-link-widget-selector')) {
        updateSelection(item);
        item.addEventListener("change", (e) => {
            updateSelection(e.target);
            e.target.closest('.link-widget').querySelector('input[widget="anchor"]').value = '';
        });
    }

    // If site widget changes, clear internal link widget
    for (let item of document.querySelectorAll('.js-link-site-widget')) {
        console.warn(item);
        django.jQuery(item).on('change', e => {
            const site_select2 = django.jQuery(e.target);
            const internal_link_select2 = site_select2.closest('.link-widget').find('[widget="internal_link"]');
            internal_link_select2.attr('data-app-label', site_select2.val());
            internal_link_select2.val(null).trigger('change');
        });
        item.addEventListener("change", (e) => {
            console.warn(e.target.closest('.link-widget').querySelector('[widget="internal_link"]'));
        });
    }
});
