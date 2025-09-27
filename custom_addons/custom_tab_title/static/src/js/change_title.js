/** @odoo-module **/

import { registry } from "@web/core/registry";
import { WebClient } from "@web/webclient/webclient"
import {patch} from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

// Changes Odoo to My Title in window title
patch(WebClient.prototype,  {
    setup() {
        super.setup();

        const titleService = useService("title");

        let current_company_id;
        if (session.user_context.allowed_company_ids) {
            current_company_id = session.user_context.allowed_company_ids[0];
        } else {
            current_company_id = session.user_companies ?
                session.user_companies.current_company :
                false;
        }

        this.orm.read('res.company', [current_company_id], ['name'])
        .then((record) => {
            if (record.length > 0) {
                console.log("Company Name:", record[0].name);
                titleService.setParts({ zopenerp: record[0].name }); // Access the name
            } else {
                console.log("No company found for the given ID.");
                titleService.setParts({ zopenerp: "My Company" });
            }
        })
        .catch((error) => {
            console.error("Error fetching company name:", error);
        });
    },
});
