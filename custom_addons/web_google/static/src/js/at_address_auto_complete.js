/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { CharField, charField } from "@web/views/fields/char/char_field";
import { useInputField } from "@web/views/fields/input_field_hook";
const { useRef } = owl;
import { useService } from "@web/core/utils/hooks";
import { renderToElement } from "@web/core/utils/render";
import { debounce } from"@web/core/utils/timing";

export class AtAddressAutoComplete extends CharField {

    /**
    * The purpose of this extension
    * is to allow initialize component
    * @override
    */
    setup() {
        super.setup();
        this.inputRef = useRef("input");
        this.rpc = useService("rpc");
        useInputField({ getValue: () => this.props.record.data[this.props.name] || "", parse: (v) => this.parse(v), ref: this.inputRef });
        this.onInputEventAddress = debounce(this.onInputEventAddress, 200);
    }

    _hideAddressesDropdown($container) {
        const addressDropdown = $container.find('.js_cls_address_dropdown');
        if (addressDropdown) {
            addressDropdown.remove();
        }
    }

    async _renderAddressDropdown() {
        var self = this;
        if (self.inputRef.el.value) {
            const results = await self.rpc("/web_google/partial_address", { partial_address: self.inputRef.el.value });
            if (results.length) {
                var data = renderToElement("web_google.AddressDropDown", {
                    results: results
                })
                if (data) {
                    self.addressDropdown = $(data).length ? $(data)[0] : false;
                    return self.addressDropdown;
                }
            }
        }
        if (self.inputRef.el.parentNode) {
            self._hideAddressesDropdown($(self.inputRef.el.parentNode));
        }
    }

    async onInputEventAddress() {
        var self = this;
        await self._renderAddressDropdown().then(async function (response) {
            if (response) {
                const inputC = self.inputRef.el.parentNode;
                if (inputC) {
                    self._hideAddressesDropdown($(inputC));
                    await inputC.appendChild(response);
                    const addressDropdownItem = $(inputC).find('.js_cls_address_dropdown > .js_cls_address_result_item');
                    if (addressDropdownItem.length) {
                        addressDropdownItem.on('click', self.onClickDropdownItem.bind(self))
                    }
                }
            }
        });
    }

    async onClickDropdownItem(ev) {
        var self = this;
        self.inputRef.el.value = ev.currentTarget.innerText;
        const addressDropdownItem = self.inputRef.el.parentNode;
        const $addressContainer = $(addressDropdownItem.parentNode);
        self._hideAddressesDropdown($addressContainer);
        const results = await self.rpc("/web_google/fill_address", { address: self.inputRef.el.value || ev.currentTarget.innerText, place_id: ev.currentTarget.dataset.placeId });
        if (results) {
            var address = "object" == typeof results ? results : JSON.parse(results);
            // -------------------------------------
            // Write value in input and Trigger Input Change
            // -------------------------------------
            var el = document.querySelector('div[name="at_contact_place_text"] input');
            if (el) {
                el.value = ''
                el.value = JSON.stringify(address);
                el.dispatchEvent(new InputEvent("input", { bubbles: true }));
                el.dispatchEvent(new InputEvent("enter", { bubbles: true }));
                el.dispatchEvent(new InputEvent("change", { bubbles: true }));
            }
            // -------------------------------------
            // Write value in input and Trigger Input Change
            // -------------------------------------

            // -------------------------------------
            // Write value in input and Trigger Input Change
            // -------------------------------------
            // var el = document.getElementById("at_contact_place_text_main_string");
            var el = document.querySelector('div[name="at_contact_place_text_main_string"] input');
            if (el) {
                el.value = self.inputRef.el.value.trim();
                el.dispatchEvent(new InputEvent("input", { bubbles: true }));
                el.dispatchEvent(new InputEvent("enter", { bubbles: true }));
                el.dispatchEvent(new InputEvent("change", { bubbles: true }));
            }
            // -------------------------------------
            // Write value in input and Trigger Input Change
            // -------------------------------------
        }
    }
}

AtAddressAutoComplete.template = "web_google.CharField";
export const AddressAutoComplete = {
    ...charField,
    component: AtAddressAutoComplete,
};
registry.category("fields").add("at_address_auto_complete", AddressAutoComplete);
