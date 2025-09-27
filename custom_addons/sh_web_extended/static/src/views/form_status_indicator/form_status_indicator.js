/** @odoo-module **/

import { FormStatusIndicator } from "@web/views/form/form_status_indicator/form_status_indicator";
import { patch } from "@web/core/utils/patch";

patch(FormStatusIndicator.prototype, {
    // Override
    async save_close() {
        await this.props.save();
        this.env.config.historyBack();
    }
});
