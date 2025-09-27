/** @odoo-module **/

import { fieldVisualFeedback } from "@web/views/fields/field";
import { patch } from "@web/core/utils/patch";
import { FormLabel } from "@web/views/form/form_label";

patch(FormLabel.prototype, {
    // Override
    get className() {
        let classes = super.className;
        const { required } = fieldVisualFeedback(
            this.props.fieldInfo.field,
            this.props.record,
            this.props.fieldName,
            this.props.fieldInfo
        );
        let requiredClass = ""
        if (required) {
            requiredClass = " o_custom_required";
        }
        return classes.concat(requiredClass);
    }
});
