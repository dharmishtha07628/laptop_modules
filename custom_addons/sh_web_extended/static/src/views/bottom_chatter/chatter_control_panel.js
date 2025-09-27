/* @odoo-module */

// ===========================================
//  Chatter Controll Panel
// ===========================================

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { ControlPanel } from "@web/search/control_panel/control_panel";

export class ChatterControlPanel extends Component {
    setup() {
        this.orm = useService('orm');
        this.has_chatter();
    }
 
    has_chatter() {
        const { viewSwitcherEntries, viewType } = this.env.config;
        if (viewType == 'form') {
            this.sh_has_chatter = true;
        } else {
            this.sh_has_chatter = false;
        }
    }

    async onClickChatter() {
        const res = document.querySelector('.o_form_renderer');
        if (res) {
            const formView = res.getElementsByClassName('o_form_sheet_bg')[0]
            const o_attachment_preview = res.querySelector('.o_attachment_preview');

            if (formView.classList.contains('customBottom')) {
                $(formView).removeClass('customBottom')
                $($(formView).parent()).find('.o-mail-Form-chatter').removeClass('customBottom d-none');
                // if (o_attachment_preview) {
                //     o_attachment_preview.classList.remove('d-none');
                // }

            } else {
                $(formView).addClass('customBottom')
                $($(formView).parent()).find('.o-mail-Form-chatter').addClass('customBottom d-none');
                // if (o_attachment_preview) {
                //     o_attachment_preview.classList.add('d-none');
                // }
            }
        }
    };
}

ChatterControlPanel.template = "sh_web_extended.ChatterTemplate";

ControlPanel.components = {
    ...ControlPanel.components,
    ChatterControlPanel,
}
