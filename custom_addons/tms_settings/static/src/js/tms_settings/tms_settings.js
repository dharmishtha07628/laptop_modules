/** @odoo-module **/

import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';

const { Component, useState, onWillStart, onMounted } = owl;

export class TmsSettings extends Component {
    setup() {
        super.setup();
        this.action = useService("action");
        this.orm = useService('orm');

        this.state = useState({
            infos: {},
        });

        onWillStart(async () => {
            await this._fetchSettingInfos();
        });
    }

    async _fetchSettingInfos(parent_id) {
        this.state.infos = await this.orm.call(
            'tms.setting', 'get_setting_data', [this.props.action.context['tag']],
            { context: this.context },
        );
    }

    call_action(ev) {
        const action_id = ev.currentTarget.getAttribute('data-action-id');
        this.action.doAction(action_id);
    }

}

TmsSettings.template = 'tms_settings.template_tms_settings';
registry.category('actions').add('tms_settings', TmsSettings);
