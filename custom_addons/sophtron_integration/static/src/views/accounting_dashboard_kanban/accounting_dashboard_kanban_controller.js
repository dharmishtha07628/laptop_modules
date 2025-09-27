/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from '@web/core/registry';
import { kanbanView } from "@web/views/kanban/kanban_view";
import { useService } from "@web/core/utils/hooks";
import { useRef } from "@odoo/owl";

export class AccountingDashboardKanbanController extends KanbanController {
    setup() {
        super.setup();
        this.orm = useService("orm");
    }

    async OnFetchClick() {
        await this.orm.call('sophtron.api.member', 'find_transactions_records', []);
        await this.model.root.load();
		this.model.notify();
    }
}

registry.category("views").add("accounting_dashboard_kanban", {
    ...kanbanView,
    Controller: AccountingDashboardKanbanController,
    buttonTemplate: "account.AccountingDashboardKanbanView.Buttons",
});