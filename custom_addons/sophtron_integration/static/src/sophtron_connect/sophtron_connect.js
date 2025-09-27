/** @odoo-module **/

import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';

const { Component, useState, useEffect, onWillStart, onMounted } = owl;

export class TmsSophtronSettings extends Component {
    async setup() {
        super.setup();
        this.action = useService("action");
        this.orm = useService('orm');
        this.rpc = useService('rpc');
        this.account_info = []

        useEffect(
            () => {
                // TODO-MUB: Fix me ; this is not proper solution for remove footer
                const modalFooters = document.querySelectorAll('.modal-footer');
                if (modalFooters.length > 0) {
                    modalFooters[modalFooters.length - 1].style.display = 'none';
                }
            },
            () => []
        );

        onMounted(() => {
            this.loadIframe();
            // props.actionProps.action.tag
        });

        this.state = useState({
            infos: {},
        });
        console.log("=-=-this",this)
        onWillStart(async () => {
            await this._fetchSettingInfos();
        });
        this.messageHandler = this.messageHandler.bind(this);
        window.addEventListener('message', this.messageHandler, false);
//        this.onMessage({ type: 'action', action: 'init'});
      
        var testData = {
            "session_guid": "",
            "user_guid": "277c43ed-3c94-47e1-ab9c-c6e9dc9f190a",
            "member_guid": "5595968b-1562-4bb1-982b-036909a164d8",
            "aggregator": "sophtron"
        }

//        await this.onMessage(testData)

    }

    async loadIframe() {
        try {
            const response = await this.rpc('/get/system_parameter',{param_key: 'sophtron_integration'});

            console.log(response)

            if (response && response.value) {
                const iframeContainer = document.getElementById('iframe-container');
                if (iframeContainer) {
                    iframeContainer.innerHTML = `
                        <iframe
                            src="${response.value}"
                            title="Sophtron Integration"
                            style="height: 500px; width: 100%; border: none;"
                        ></iframe>
                    `;
                }
                document.getElementById('createJournal').style.display = 'none';
            } else {
                console.error('Error: Unable to fetch configuration parameters.');
            }
        } catch (error) {
            console.error('Error fetching system parameters:', error);
        }
    }

    async onMessage(message) {
        console.log("---message",message)
        var result = await this.orm.call(
                'sophtron.api.client', 'create_sophtron_object', [this.props.action.params.journal_id,message.user_guid,message.member_guid,this.props.action.params.sophtron_id]
            );
        console.log("Account Data-----------", result)

        console.log("sophtron id ------", this)

         if (result.length === 0) {
                alert('No data available.');
                return; // Exit the function if there's no data
            } else if(result.length >= 1){
                    const iframeContainer = document.getElementById('iframe-container');
                    if (iframeContainer) {
                        iframeContainer.style.display = 'none';
                    }

                    const container = document.getElementById('radiobtnContainer');
                    if (!container) {
                        console.error("Radio Button container not found.");
                        return;
                    }
                    container.innerHTML = ''; // Clear previous content

                    result.forEach((account, index) => {
                        if (account.AccountNumber && account.AccountID) {
                            const radioWrapper = document.createElement('div');
                            radioWrapper.className = 'radio-wrapper'; // Apply CSS class for styling

                            const radio = document.createElement('input');
                            radio.type = 'radio';
                            radio.id = `account-${index}`;
                            radio.name = account.AccountNumber.slice(-4); // Same name for all to group them
                            radio.value = account.AccountID;

                            const label = document.createElement('label');
                            label.htmlFor = `account-${index}`;
                            label.appendChild(document.createTextNode(account.AccountNumber.slice(-4)));

                            radioWrapper.appendChild(radio);
                            radioWrapper.appendChild(label);
                            container.appendChild(radioWrapper);
                        } else {
                            console.warn("Account data is missing expected properties:", account);
                        }
                    });

                    this.account_info = result;

                    document.getElementById('createJournal').style.display = 'block';
            }

      }

    async messageHandler(msg){
        console.log("--msg--",msg)
        if (msg.data.type == "vcs/connect/memberConnected"){
            var result = await this.orm.call(
                'sophtron.api.client', 'create_sophtron_object', [this.props.action.params.journal_id,msg.data.metadata.user_guid,msg.data.metadata.member_guid,this.props.action.params.sophtron_id]
            );

            console.log("Account Data-----------", result)
            console.log("sophtron id ------", this)

            if (result.length === 0) {
                alert('No data available.');
                return; // Exit the function if there's no data
            } else if(result.length >= 1){
                    const iframeContainer = document.getElementById('iframe-container');
                    if (iframeContainer) {
                        iframeContainer.style.display = 'none';
                    }

                    const container = document.getElementById('radiobtnContainer');
                    if (!container) {
                        console.error("Radio Button container not found.");
                        return;
                    }
                    container.innerHTML = ''; // Clear previous content

                    result.forEach((account, index) => {
                        if (account.AccountNumber && account.AccountID) {
                            const radioWrapper = document.createElement('div');
                            radioWrapper.className = 'radio-wrapper'; // Apply CSS class for styling

                            const radio = document.createElement('input');
                            radio.type = 'radio';
                            radio.id = `account-${index}`;
                            radio.name = account.AccountNumber.slice(-6); // Same name for all to group them
                            radio.value = account.AccountID;

                            const label = document.createElement('label');
                            label.htmlFor = `account-${index}`;
                            label.appendChild(document.createTextNode(account.AccountNumber.slice(-6)));

                            radioWrapper.appendChild(radio);
                            radioWrapper.appendChild(label);
                            container.appendChild(radioWrapper);
                        } else {
                            console.warn("Account data is missing expected properties:", account);
                        }
                    });
                    debugger;
                    this.account_info = result;

                    document.getElementById('createJournal').style.display = 'block';
            }
        }
    }

    async _fetchSettingInfos(parent_id) {
        this.state.infos = await this.orm.call(
            'tms.setting', 'get_setting_data', [this.props.action.context['tag']],
            { context: this.context },
        );
    }

    async onCreateJournalClick(ev) {
        console.log("this ------", this);
        // Collect the selected account from the radio button
        const selectedRadio = document.querySelector('#radiobtnContainer input[type="radio"]:checked');

        if (!selectedRadio) {
            alert('No account selected.');
            return;
        }

        const selectedAccount = {
            name: selectedRadio.name,
            id: selectedRadio.value
        };
        debugger;
        var msg = await this.orm.call('sophtron.api.client', 'create_journal', [[selectedAccount], this.account_info, this.props.action.params.journal_id, this.props.action.params.sophtron_id]);
        alert(msg);
        return;
    }

    call_action(ev) {
        const action_id = ev.currentTarget.getAttribute('data-action-id');
        this.action.doAction(action_id);
    }


}

TmsSophtronSettings.template = 'sophtron_integration.template_tms_settings';
registry.category('actions').add('tms_sophtron_settings', TmsSophtronSettings);
