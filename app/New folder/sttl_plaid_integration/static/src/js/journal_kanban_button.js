/** @odoo-module **/

import {
   KanbanController
} from "@web/views/kanban/kanban_controller";
import {
   registry
} from '@web/core/registry';
import {
   kanbanView
} from "@web/views/kanban/kanban_view";
import {
   useService
} from "@web/core/utils/hooks";
import {
   useRef
} from "@odoo/owl";
import {
   _t
} from "@web/core/l10n/translation";

export class AccountingDashboardKanbanController extends KanbanController {
   setup() {
      super.setup();
      this.orm = useService("orm");
      this.action = useService("action");

   }

   async OnFetchClick() {
      console.log("file load")
      this.action.doAction({
         type: 'ir.actions.act_window',
         name: 'Fetch Transaction',
         res_model: 'plaid.transaction.wizard',
         view_mode: 'form',
         target: 'new', // Opens as modal
         views: [
            [false, 'form']
         ],
      });
   }
}

registry.category("views").add("accounting_dashboard_kanban", {
   ...kanbanView,
   Controller: AccountingDashboardKanbanController,
   buttonTemplate: "account.AccountingDashboardKanbanView.Buttons",
});