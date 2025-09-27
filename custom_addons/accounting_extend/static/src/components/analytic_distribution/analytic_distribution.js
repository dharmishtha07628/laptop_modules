/** @odoo-module */

import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";
import { patch } from "@web/core/utils/patch";


patch(AnalyticDistribution.prototype, {
    get valueColumnEnabled() {
        return true;
    },
});
