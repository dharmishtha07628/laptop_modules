/** @odoo-module */
import { xml } from "@odoo/owl";
import {registry} from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
import { ListRenderer } from "@web/views/list/list_renderer";

export class ClosingEntry extends ListRenderer {
    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    OnClickJournalEntry() {
        this.actionService.doAction('auto_retained_earnings_closing.action_retained_earnings_wizard');
    }
}

ClosingEntry.template = "module.stock.ListView.Buttons";

registry.category("views").add("button_in_list", {
    ...registry.category("views").get("list"),
    Renderer: ClosingEntry,
});
