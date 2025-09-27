/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    // Override
    get deleteConfirmationDialogProps() {
        let deleteConfirmationDialogProps = super.deleteConfirmationDialogProps;
        deleteConfirmationDialogProps = {
            ...deleteConfirmationDialogProps,
            confirm: async () => {
                await this.model.root.delete();
                this.env.config.historyBack();
            },
        }
        return deleteConfirmationDialogProps;
    }
});
