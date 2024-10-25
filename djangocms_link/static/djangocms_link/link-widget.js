/* eslint-env es11 */
/* jshint esversion: 11 */
/* global document */

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
});
