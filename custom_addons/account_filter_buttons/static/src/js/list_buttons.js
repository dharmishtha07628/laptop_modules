/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from '@web/core/utils/hooks';
import { AccountMoveUploadListRenderer } from "@account/components/bills_upload/bills_upload";


export class ApplyFilterController extends Component {
    setup() {
        super.setup();
        this.action = useService("action");
        const display_name = this.env.config.getDisplayName();
        if (display_name == 'Vendor Bills') {
            this.label = "Bills";
        } else {
            this.label = "Invoices";
        }
    }

    setSearchContext(ev) {
        const filter_name = ev.currentTarget.getAttribute("filter_name");
        const filters = filter_name.split(",");
        const searchItems = this.env.searchModel.getSearchItems((item) =>
            filters.includes(item.name)
        );
        this.env.searchModel.query = [];
        for (const item of searchItems) {
            this.env.searchModel.toggleSearchItem(item.id);
        }
    }
}    

ApplyFilterController.template = "account_filter_buttons.filterbutton";

AccountMoveUploadListRenderer.components = {
    ...AccountMoveUploadListRenderer.components,
    ApplyFilterController,
};
