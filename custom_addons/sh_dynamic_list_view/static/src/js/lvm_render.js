/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { session } from "@web/session";
import { renderToElement } from "@web/core/utils/render";
import { browser } from "@web/core/browser/browser";
import { useService } from "@web/core/utils/hooks";
// import { SearchView } from "@sh_dynamic_list_view/component/search_view";
import { jsonrpc } from "@web/core/network/rpc_service";
import { getCurrency } from "@web/core/currency";
import { _t } from "@web/core/l10n/translation";
import { formatFloat,formatInteger } from "@web/views/fields/formatters";




const { useRef, onMounted , onWillStart , useExternalListener , onWillUpdateProps , Component } = owl;

patch(ListRenderer.prototype,  {
    setup() {
        var self = this;
         this.sh_serial_number = session.sh_serial_number;
         this.sh_allow_search = true;
         this.ShDomain = [];
         this.datepicker;
         this.rpc = useService("rpc");
         this.sh_datepicker_flag = 0
         this.mydomain = null;
        this.sh_autocomplete_data = {};
        this.sh_autocomplete_data_result = {};
        this.sh_lvm_mode = true;
        this.sh_remove_popup_flag = false;
        this.sh_key_fields = [];
        this.sh_field_domain_list = [];
        this.sh_field_domain_dict = {};
        this.ShBaseDomain = [];
        this.sh_advance_search_refresh = false;
        this.sh_start_date = undefined;
        this.sh_end_date = undefined;
        this.sh_start_date_id = undefined;
        this.sh_end_date_id = undefined;
        this.sh_editable = false;
        if (this.props.list.domain){
        this.default_domain = [...this.props.list.domain]
        this.sh_search_domain = [...this.props.list.domain]
        };
        if(this.env.searchModel && this.env.searchModel.globalDomain){
        this.search_default=[...this.env.searchModel.globalDomain]
        };
        this.sh_list_data = this.props.list_data ? this.props.list_data : session.list_data
        var sh_is_list_renderer = true ? this.props.list_data : false;

        this.tableRef = useRef("table");
        this.sh_is_lines = true;
        if (this.props.activeActions.type == 'view' &&  sh_is_list_renderer) {
            this.sh_is_lines = false;
        }
        onMounted(this._mounted);
            $('.o_web_client').addClass('sh_list_view_manager')
            // debugger;
            this.sh_enable_list_view_manager = session.sh_enable_list_view_manager
            onWillUpdateProps((next_prop) => {
                this.keepColumnWidths = true;
                this.allColumns = next_prop.archInfo.columns;
                this.getOptionalActiveFields();
                this.state.columns = this.getActiveColumns(next_prop.list);
            });


        return super.setup();
    },

    async _mounted() {
        if (this.isX2Many== false){
            var self = this
            var table = this.tableRef
            this.sh_allow_search = true;
            self.sh_call_flag = 1;
            $($(table.el.querySelectorAll("thead tr"))[0]).addClass("sh-primary");

            if(document.querySelector(".o_list_controller.o_list_actions_header")){
                $(document.querySelector(".o_list_controller.o_list_actions_header")).addClass('d-none');
                // $(document.querySelector(".o_list_controller.o_list_actions_header")).css('visibility', 'hidden')
            }
        }
    },

        get sh_field_popup(){
            var self = this;
            var sh_field_popup = {};
            if (self.ShDomain != []) {
                for (var i = 0; i < self.ShDomain.length; i++) {
                    if (!(self.ShDomain[i] === '|')) {
                        if (sh_field_popup[self.ShDomain[i][0]] === undefined) {
                            sh_field_popup[self.ShDomain[i][0]] = [self.ShDomain[i][2]]
                        } else {
                            sh_field_popup[self.ShDomain[i][0]].push(self.ShDomain[i][2])
                        }
                    }
                }
            }
            return sh_field_popup

        },

        sh_update_advance_search_controller(sh_options) {
             var self = this;
             if (sh_options !=false){
            let rec_ids = [];
                for (let i = 0; i < this.props.list.records.length; i++) {
                    rec_ids.push(this.props.list.records[i].resId);
                }
            sh_options['rec_ids'] = [...rec_ids]
            }

        if (this.sh_lvm_mode) {
            var self = this;
            if (self.sh_remove_popup_flag === true) {
                var sh_advance_search_params = {};
                sh_advance_search_params["modelName"] = self.props.resModel;
                sh_advance_search_params["context"] = self.props.context;
                sh_advance_search_params["ids"] = sh_options.res_ids;
                sh_advance_search_params["offset"] = self.props.list.model.root.offset;
                sh_advance_search_params["selectRecords"] = self.props.list.model.root.selection;
                sh_advance_search_params["groupBy"] = self.props.list.model.root.groupBy;
                self.sh_field_domain_list = [];

                for (var j = 0; j < self.sh_key_fields.length; j++) {
                    self.sh_field_domain_list = self.sh_field_domain_list.concat(self.sh_field_domain_dict[self.sh_key_fields[j]]);
                }
                self.sh_remove_popup_flag = false;
                sh_advance_search_params["ShDomain"] = self.sh_field_domain_list;
                if (self.sh_search_domain.length === 0) {
                    self.ShBaseDomain = []
                }
                if (self.ShBaseDomain === null && (self.ShDomain === null || self.ShDomain.length === 0) && self.sh_search_domain.length) {
                    self.ShBaseDomain = self.sh_search_domain
                }
                if (self.ShBaseDomain.length !== 0 || self.sh_field_domain_list.length !== 0) {
                    sh_advance_search_params["domain"] = self.ShBaseDomain.concat(self.sh_field_domain_list)
                } else {
                    sh_advance_search_params["domain"] = []
                }
                self.ShDomain = sh_advance_search_params["ShDomain"]
                self.mydomain = sh_advance_search_params["ShDomain"]
                self.sh_update(self.mydomain);

            } else {
                var sh_val_flag = false;
                if (sh_options.sh_val) {
                    sh_val_flag = sh_options.sh_val.trim() !== 0
                } else {
                    if (sh_options.Shfieldtype == "selection" || sh_options.Shfieldtype == "boolean") {
                        sh_val_flag = $(".custom-control-searchbar-change[data-name=" + sh_options.ShSearchId + "]").val().trim() !== 0
                    } else {
                        sh_val_flag = $(".custom-control-searchbar-advance[data-name=" + sh_options.ShSearchId + "]").val() !== 0
                    }
                }

                if (Number(sh_val_flag)) {
                    self.sh_advance_search_refresh = true;
                    if (sh_options.Shfieldtype == "selection" || sh_options.Shfieldtype == "boolean") {
                        var sh_search_value = sh_options.sh_val || $(".custom-control-searchbar-change[data-name=" + sh_options.ShSearchId + "]").val();
                    } else {
                        if(sh_options.ShSearchId === "level_progress"){
                            var sh_search_value = (sh_options.sh_val || $(".custom-control-searchbar-advance[data-name=" + sh_options.ShSearchId + "]").val())/100;
                        }else{
                        var sh_search_value = sh_options.sh_val || $(".custom-control-searchbar-advance[data-name=" + sh_options.ShSearchId + "]").val();
                        }
                    }
                    var sh_advance_search_type = sh_options.Shfieldtype;
                    var sh_selection_values = [];
                    var sh_advance_search_params = {};
                    self.sh_field_domain_list = [];
                    self.sh_key_insert_flag = false;
                    var sh_data_insert_flag = false;
                    var sh_value = sh_options.ShSearchId.split("_lvm_start_date")
                    sh_advance_search_params["groupBy"] = self.props.list.model.root.groupBy
                    sh_advance_search_params["modelName"] = self.props.resModel;
                    sh_advance_search_params["context"] = self.props.context;
                    sh_advance_search_params["ids"] = sh_options.res_ids;
                    sh_advance_search_params["offset"] = self.props.list.model.root.offset;
                    sh_advance_search_params["selectRecords"] = self.props.list.model.root.selection

                    if (sh_value.length === 1) {
                        sh_value = sh_options.ShSearchId.split("_lvm_end_date")
                        if (sh_value.length === 2)
                            sh_options.ShSearchId = sh_value[0];
                    } else {
                        sh_options.ShSearchId = sh_value[0];
                    }

                    for (var sh_sel_check = 0; sh_sel_check < self.sh_key_fields.length; sh_sel_check++) {
                        if (sh_options.ShSearchId === self.sh_key_fields[sh_sel_check]) {
                            sh_data_insert_flag = true;
                        }
                    }

                    if ((sh_data_insert_flag === false) || (sh_data_insert_flag === true && (sh_advance_search_type === "many2one" || sh_advance_search_type === "many2many" || sh_advance_search_type === "char"))) {
                        if (!(sh_advance_search_type === "datetime" || sh_advance_search_type === "date")) {
                            if (this.sh_key_fields.length === 0) {
                                if (sh_advance_search_type === 'monetary' || sh_advance_search_type === 'integer' || sh_advance_search_type === 'float') {
                                    try {
                                        //Fixme currency
                                        var currency = getCurrency(self.props.list_data.currency);
                                        var parsed_value = parseFloat(sh_search_value);
                                        if (isNaN(parsed_value)) {
                                            throw new Error('Invalid number');
                                        }
                                        self.sh_key_fields.push(sh_options.ShSearchId);
                                    } catch {
                                        this.env.services.notification.add(_t("Please enter a valid number"), {
                                            title: _t("Notification"),
                                            sticky: false,
                                            type: "info",
                                        });
                                    }
                                } else {
                                    self.sh_key_fields.push(sh_options.ShSearchId);
                                }
                            } else {
                                for (var key_length = 0; key_length < self.sh_key_fields.length; key_length++) {
                                    if ((self.sh_key_fields[key_length] === sh_options.ShSearchId)) {
                                        self.sh_key_insert_flag = true;
                                        break;
                                    }
                                }
                                if (!(self.sh_key_insert_flag)) {
                                    if (sh_advance_search_type === 'monetary' || sh_advance_search_type === 'integer' || sh_advance_search_type === 'float') {
                                        try {
                                            // Fixme currency
                                             var currency = getCurrency(self.props.list_data.currency);
                                             var parsed_value = parseFloat(sh_search_value);
                                             if (isNaN(parsed_value)) {
                                                throw new Error('Invalid number');
                                             }
                                             var formatted_value = formatFloat(parsed_value || 0, {
                                                digits: currency && currency.digits
                                             });
                                             sh_search_value = formatted_value
                                             self.sh_key_fields.push(sh_options.ShSearchId);
                                        } catch {
                                            this.env.services.notification.add(_t("Please enter a valid number"), {
                                                title: _t("Notification"),
                                                sticky: false,
                                                type: "info",
                                            });
                                        }
                                    } else {
                                        self.sh_key_fields.push(sh_options.ShSearchId);
                                    }
                                }
                            }
                        }

                        if (sh_advance_search_type === "datetime" || sh_advance_search_type === "date") {
                            if (sh_options.ShFieldIdentity === sh_options.ShSearchId + '_lvm_start_date lvm_start_date') {
                                self.sh_start_date = sh_search_value;
                                self.sh_start_date_id = sh_options.ShSearchId;
                            } else {
                                self.sh_end_date = sh_search_value;
                                self.sh_end_date_id = sh_options.ShSearchId
                            }

                            if (sh_advance_search_type === "datetime" || sh_advance_search_type === "date") {
                                if (sh_options.ShFieldIdentity === sh_options.ShSearchId + '_lvm_end_date lvm_end_date') {
                                    if (self.sh_start_date_id === self.sh_end_date_id) {
                                        self.sh_field_domain_dict[self.sh_start_date_id] = [
                                            [self.sh_start_date_id, '>=', self.sh_start_date],
                                            [self.sh_end_date_id, '<=', self.sh_end_date]
                                        ]
                                        if (self.sh_key_fields.length === 0) {
                                            self.sh_key_fields.push(self.sh_start_date_id);
                                        } else {
                                            for (var key_length = 0; key_length < self.sh_key_fields.length; key_length++) {
                                                if (!(self.sh_key_fields[key_length] === sh_options.ShSearchId)) {
                                                    self.sh_key_fields.push(self.sh_start_date_id);
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        } else if (sh_advance_search_type === 'selection' || sh_advance_search_type === 'boolean') {
                            if (sh_search_value === "Select a Selection") {
                                for (var j = 0; j < self.sh_key_fields.length; j++) {
                                    self.sh_field_domain_list = self.sh_field_domain_list.concat(self.sh_field_domain_dict[self.sh_key_fields[j]]);
                                }
                                sh_advance_search_params["ShDomain"] = self.sh_field_domain_list;
                                if (self.sh_search_domain.length === 0) {
                                    self.ShBaseDomain = []
                                }
                                sh_advance_search_params["domain"] = self.ShBaseDomain.concat(self.sh_field_domain_list)
                                self.ShDomain = sh_advance_search_params["ShDomain"]
                                self.mydomain = sh_advance_search_params["ShDomain"]
                                self.sh_update(self.mydomain);
                            } else {

                                // obtaining values of selection
                                // alert(sh_selection_values)
                                // debugger

                                if (sh_advance_search_type === 'boolean') {
                                    sh_selection_values = [['true', 'True'], ['false', 'False']]
                                } else {
                                    sh_selection_values = self.props.list.fields[sh_options.ShSearchId].selection;
                                }


                                //setting values for selection
                                for (var i = 0; i < sh_selection_values.length; i++) {
                                    if (sh_selection_values[i][1] === sh_search_value) {
                                        sh_search_value = sh_selection_values[i][0];
                                    }
                                }
                                if (sh_advance_search_type === 'boolean') {
                                    if (sh_search_value == 'true') {
                                        sh_search_value = true;
                                    } else {
                                        sh_search_value = false;
                                    }
                                    self.sh_field_domain_dict[sh_options.ShSearchId] = [
                                        [sh_options.ShSearchId, '=', sh_search_value]
                                    ]    
                                } else {
                                    self.sh_field_domain_dict[sh_options.ShSearchId] = [
                                        [sh_options.ShSearchId, '=', sh_search_value]
                                    ]
                                }

                            }
                        } else if (sh_advance_search_type === "many2one" || sh_advance_search_type === "many2many") {
                            if (self.sh_field_domain_dict[sh_options.ShSearchId] === undefined)
                                self.sh_field_domain_dict[sh_options.ShSearchId] = [
                                    [sh_options.ShSearchId, "ilike", sh_search_value]
                                ]
                            else
                                self.sh_field_domain_dict[sh_options.ShSearchId].push([sh_options.ShSearchId, "ilike", sh_search_value])

                            if (self.sh_field_domain_dict[sh_options.ShSearchId].length > 1) {
                                self.sh_field_domain_dict[sh_options.ShSearchId].unshift("|")
                            }
                            //                                sh_advance_search_params["ids"] = self.initialState.res_id;
                        } else if (sh_advance_search_type === 'monetary' || sh_advance_search_type === 'integer' || sh_advance_search_type === 'float') {
                            self.sh_field_domain_dict[sh_options.ShSearchId] = [
                                [sh_options.ShSearchId, '=', sh_search_value]
                            ]

                        }
                        else if (sh_advance_search_type === 'char') {
                            if (self.sh_field_domain_dict[sh_options.ShSearchId] === undefined) {
                                self.sh_field_domain_dict[sh_options.ShSearchId] = [
                                    [sh_options.ShSearchId, 'ilike', sh_search_value]
                                ]
                            }
                            else { self.sh_field_domain_dict[sh_options.ShSearchId].push([sh_options.ShSearchId, 'ilike', sh_search_value]) }
                            if (self.sh_field_domain_dict[sh_options.ShSearchId].length > 1) {
                                self.sh_field_domain_dict[sh_options.ShSearchId].unshift("|")
                            }
                        }

                        else {
                            self.sh_field_domain_dict[sh_options.ShSearchId] = [
                                [sh_options.ShSearchId, "ilike", sh_search_value]
                            ]
                        }

                        if (sh_advance_search_type === "datetime" || sh_advance_search_type === "date") {
                            if (sh_options.ShFieldIdentity === sh_options.ShSearchId + '_lvm_end_date lvm_end_date') {
                                for (var j = 0; j < self.sh_key_fields.length; j++) {
                                    this.sh_field_domain_list = self.sh_field_domain_list.concat(self.sh_field_domain_dict[self.sh_key_fields[j]]);
                                }
                                sh_advance_search_params["ShDomain"] = self.sh_field_domain_list;
                                if (self.sh_search_domain.length === 0) {
                                    self.ShBaseDomain = []
                                }
                                sh_advance_search_params["domain"] = self.ShBaseDomain.concat(self.sh_field_domain_list)
                                self.ShDomain = sh_advance_search_params["ShDomain"]
                                self.mydomain = sh_advance_search_params["ShDomain"]
                                self.sh_update(self.mydomain);
                                // Fixme update
                                //                                    self.update(sh_advance_search_params, undefined);
                                self.sh_start_date = undefined;
                                self.sh_end_date = undefined;
                                self.sh_start_date_id = undefined;
                                self.sh_end_date_id = undefined;
                            }
                        } else {
                            if (sh_advance_search_type === 'monetary' || sh_advance_search_type === 'integer' || sh_advance_search_type === 'float') {
                                if (!(isNaN(sh_search_value))) {
                                    for (var j = 0; j < self.sh_key_fields.length; j++) {
                                        self.sh_field_domain_list = self.sh_field_domain_list.concat(self.sh_field_domain_dict[self.sh_key_fields[j]]);
                                    }
                                    sh_advance_search_params["ShDomain"] = self.sh_field_domain_list;
                                    if (self.sh_search_domain.length === 0) {
                                        self.ShBaseDomain = []
                                    }
                                    sh_advance_search_params["domain"] = self.ShBaseDomain.concat(self.sh_field_domain_list)
                                    self.ShDomain = sh_advance_search_params["ShDomain"]
                                    self.mydomain = sh_advance_search_params["ShDomain"]
                                    self.sh_update(self.mydomain);
                                    // FIXME update
                                    //                                        self.update(sh_advance_search_params, undefined);
                                } else {
                                    if (self.sh_search_domain.length === 0) {
                                        self.ShBaseDomain = []
                                    }
                                    sh_advance_search_params["domain"] = self.ShDomain || []
                                    self.mydomain = sh_advance_search_params["domain"]
                                    self.sh_update(self.mydomain);
                                    // Fixme update
                                    //                                        self.update(sh_advance_search_params, undefined);
                                }
                            } else {
                                for (var j = 0; j < self.sh_key_fields.length; j++) {
                                    self.sh_field_domain_list = self.sh_field_domain_list.concat(self.sh_field_domain_dict[self.sh_key_fields[j]]);
                                }
                                sh_advance_search_params["ShDomain"] = self.sh_field_domain_list;
                                if (self.sh_search_domain.length === 0) {
                                    self.ShBaseDomain = []
                                }
                                sh_advance_search_params["domain"] = self.ShBaseDomain.concat(self.sh_field_domain_list)
                                self.ShDomain = sh_advance_search_params["ShDomain"];
                                self.mydomain = sh_advance_search_params["ShDomain"]
                                self.sh_update(self.mydomain);
                                // Fixme update
                                //                                    self.update(sh_advance_search_params, undefined);
                            }
                        }
                    } else {
                        for (var j = 0; j < self.sh_key_fields.length; j++) {
                            self.sh_field_domain_list = self.sh_field_domain_list.concat(self.sh_field_domain_dict[self.sh_key_fields[j]]);
                        }
                        sh_advance_search_params["ShDomain"] = self.sh_field_domain_list;
                        if (self.sh_search_domain.length === 0) {
                            self.ShBaseDomain = []
                        }
                        sh_advance_search_params["domain"] = self.ShBaseDomain.concat(self.sh_field_domain_list)
                        self.ShDomain = sh_advance_search_params["ShDomain"]
                        self.mydomain = sh_advance_search_params["ShDomain"]
                        self.sh_update(self.mydomain);
                        // Fixme update
                        //                            self.update(sh_advance_search_params, undefined);
                    }
                } else {
                    self.sh_advance_search_refresh = true;
                    //                        var sh_search_value = $('#' + sh_options.data.ShSearchId).val().trim();
                    if (sh_options.Shfieldtype == "selection") {
                        var sh_search_value = $(".custom-control-searchbar-change[data-name=" + sh_options.ShSearchId + "]").val().trim();
                    } else {
                        var sh_search_value = $(".custom-control-searchbar-advance[data-name=" + sh_options.ShSearchId + "]").val();
                    }
                    //                        var sh_search_value = $(".custom-control-searchbar-advance[data-name=" + sh_options.data.ShSearchId + "]").val().trim();
                    var sh_advance_search_type = sh_options.Shfieldtype;
                    var sh_selection_values = [];
                    var sh_advance_search_params = {};
                    self.sh_field_domain_list = [];
                    self.sh_key_insert_flag = false;
                    var sh_data_insert_flag = false;
                    var sh_value = sh_options.ShSearchId.split("_lvm_start_date")

                    sh_advance_search_params["modelName"] = self.props.list.resModel;
                    sh_advance_search_params["context"] = self.props.context;
                    sh_advance_search_params["ids"] = sh_options.res_ids;
                    sh_advance_search_params["offset"] = self.props.list.model.root.offset;
                    sh_advance_search_params["selectRecords"] = self.props.list.model.root.selection;
                    sh_advance_search_params["groupBy"] = [];

                    for (var j = 0; j < self.sh_key_fields.length; j++) {
                        self.sh_field_domain_list = self.sh_field_domain_list.concat(self.sh_field_domain_dict[self.sh_key_fields[j]]);
                    }
                    sh_advance_search_params["ShDomain"] = self.sh_field_domain_list;
                    if (self.sh_search_domain.length === 0) {
                        self.ShBaseDomain = []
                    }
                    sh_advance_search_params["domain"] = self.ShBaseDomain.concat(self.sh_field_domain_list)
                    self.ShDomain = sh_advance_search_params["ShDomain"]
                    self.mydomain = sh_advance_search_params["ShDomain"]
                    self.sh_update(self.mydomain);

                }
            }
        }
    },

        async sh_update(data) {
        const list = this.props.list.model.root;
        this.sh_search_domain  = [];
        var browser_search_domain =[];
        this.env.searchModel.globalDomain = [];
        for (let item of this.default_domain){
            if (item != undefined){
                this.sh_search_domain.push(item);
            }
        }
        for (let items of this.search_default){
            if (items != undefined){
                this.env.searchModel.globalDomain.push(items);
            }
        }
        for(let sh_domain of data){
            if (sh_domain != undefined){
                this.env.searchModel.globalDomain.push(sh_domain);
                this.sh_search_domain.push(sh_domain)
            }
        }

        await this.env.searchModel._notify();

        },

        sh_remove_popup_domain_event(e,field_type) {
        if ($(e.target).hasClass("sh_remove_popup")) {

            var div = e.target.closest('.sh_inner_search')
            $('#end_date').addClass('d-none');
            $('#start_date').removeClass('sh_date_main')
            var sh_remove_options = {
                ShDiv: div,
                Shfieldtype: e.target.parentElement.parentElement.children[1].dataset.fieldType || field_type
            };
            this.sh_remove_popup_domain(sh_remove_options);
        }
    },

        sh_remove_popup_domain(sh_options) {
        if (this.sh_lvm_mode) {
            var self = this;
            var sh_i;
            var key;
            var key_array;

            if (sh_options.ShDiv !== undefined) {
                key_array = sh_options.ShDiv.id.split("_value")
                key = key_array[0];
                if(key === 'product_template_variant'){
                    key = key+'_value'+'_ids'
                }
            } else {
                key = event.target.id;
            }

            if (self.sh_field_domain_dict[key] !== undefined) {
                if (self.sh_field_domain_dict[key].length === 1 || sh_options.Shfieldtype === "date" || sh_options.Shfieldtype === "datetime") {
                    delete self.sh_field_domain_dict[key]
                    for (sh_i = 0; sh_i < self.sh_key_fields.length; sh_i++) {
                        if (key === self.sh_key_fields[sh_i]) {
                            break;
                        }
                    }

                    if (sh_options.ShDiv !== undefined) {
//                        $("#" + sh_options.ShDiv.id).remove()
                    } else {
                        // fixme
                        //                            $("#" + $(sh_options.event.target).parent().children()[$(sh_options.data.event.target).parent().children().length - 2].id).remove();
                    }

                    self.sh_key_fields.splice(sh_i, 1);
                    self.sh_remove_popup_flag = true;
                    self.sh_update_advance_search_controller(false);
                } else {
                    for (var j = 0; j < self.sh_field_domain_dict[key].length; j++) {
                        if (self.sh_field_domain_dict[key][j] !== '|') {
                            if (sh_options.ShDiv !== undefined) {
                                if (self.sh_field_domain_dict[key][j][2] === sh_options.ShDiv.innerText) {
                                    self.sh_field_domain_dict[key].splice(j, 1)
                                    self.sh_field_domain_dict[key].splice(0, 1);
                                    break;
                                }

                            } else {
                                self.sh_field_domain_dict[key].splice(j, 1)
                                self.sh_field_domain_dict[key].splice(0, 1);
                                break;
                            }
                        }
                    }
                    if (sh_options.ShDiv !== undefined) {
//                        $("#" + sh_options.ShDiv.id).remove()
                    } else {
                        //fixme
                        //                            $("#" + $(sh_options.data.event.target).parent().children()[$(sh_options.data.event.target).parent().children().length - 2].id).remove();
                    }
                    self.sh_remove_popup_flag = true;
                    self.sh_update_advance_search_controller(false);
                }
            } else {
                self.sh_remove_popup_flag = true;
                self.sh_update_advance_search_controller(false);
            }
        }
    },

        getRowClass(record) {
            var classNames = super.getRowClass(...arguments);
            if (this.props.list.selection && this.props.list.selection.length > 0) {
                $('.copy_button').css('display', 'block')
            } else {
                $('.copy_button').css('display', 'none');
            }
            if (record.selected) {
                $('.o_data_row[data-id="' + record.id + '"]').addClass('sh_highlight_row');
                classNames = "o_data_row_selected"
            }else{
            $('.o_data_row[data-id="' + record.id + '"]').removeClass('sh_highlight_row');
            }
            return classNames;
        },

    toggleSelection() {
        super.toggleSelection(...arguments);
        if (this.props.list.selection && this.props.list.selection.length === 0) {
            $('.o_data_row').removeClass('sh_highlight_row');
            $('.o_data_row').addClass('text-info');
        }
    },

    toggleRecordSelection(record) {
        super.toggleRecordSelection(...arguments);
        if (!record.selected) {
            $('.o_data_row[data-id="' + record.id + '"]').removeClass('sh_highlight_row');
            $('.o_data_row[data-id="' + record.id + '"]').addClass('text-info');
        }
    },
    onClickCapture(record, ev) {
        super.onClickCapture(...arguments);
        if ($(ev.currentTarget).hasClass("sh_highlight_row")){
            $(document.querySelectorAll(".sh_highlight_row")).removeClass("sh_highlight_row")
        }
    },
            freezeColumnWidths() {
            if (!this.sh_is_lines){
                var tableRef = this.tableRef;
                $(tableRef.el).hasClass('o_field_many2many')
                // if (session.sh_header_text_color !="white"){
                //     var sh_header_text_color = session.sh_header_text_color;
                //        (tableRef.el.querySelectorAll("thead .sh-primary th")).forEach((item) =>{item.style.setProperty("color", session.sh_header_text_color, "important")})
                // }
                if (session.sh_header_color){
                    var sh_header_color = 'white';
                    // session.sh_header_color;
                    (tableRef.el.querySelectorAll("thead .sh-primary th")).forEach((item,index) =>{
                        if (index === 0){
                            item.style.setProperty("background-color", sh_header_color, "important")
                            const formCheckInput = item.querySelector('.form-check-input');
                            if (formCheckInput) {
                                // If it exists, set the border color
                                formCheckInput.style.setProperty("border-color", session.sh_header_text_color, "important");
                            }
                        }else{
                            item.style.setProperty("background-color", sh_header_color, "important")
                        }
                    })
                }
                if (tableRef.el && ($(tableRef.el).hasClass('o_field_one2many') !== false || $(tableRef.el).hasClass('o_field_many2many') !== false)) {
                    super.freezeColumnWidths();
                }
                if (!this.keepColumnWidths) {
                    this.columnWidths = null;
                }

                if ($('.o_optional_columns_dropdown').length === 1 && !session.sh_dynamic_list_show) {
                    $('.o_optional_columns_dropdown').parent().removeClass('d-none');
                }

                const headers = [...tableRef.el.querySelectorAll("thead .sh-primary th:not(.o_list_actions_header)")];

                if (!this.columnWidths || !this.columnWidths.length) {
                    tableRef.el.style.tableLayout = "fixed";
                     const allowedWidth = tableRef.el.parentNode.getBoundingClientRect().width;
                      // Set table layout auto and remove inline style to make sure that css
                        // rules apply (e.g. fixed width of record selector)
                    tableRef.el.style.tableLayout = "auto";
                    headers.forEach((th) => {
                        th.style.width = null;
                        th.style.maxWidth = null;
                    });

                    this.setDefaultColumnWidths();

                    this.columnWidths = this.computeColumnWidthsFromContent(allowedWidth);
                    tableRef.el.style.tableLayout = "fixed";
                }

                headers.forEach((th, index) => {
                    if (!th.style.width) {
                        th.style.width = `${Math.floor(this.columnWidths[index])}px`;
                    }
                    if(!parseInt(th.style.width)|| th.style.width == "100%"){
                     th.style.width = '';
                     th.style['max-width'] = '';
                     }
                });

                if (this.props.activeActions && this.props.activeActions.type === 'view') {
                    var table_width = 0
                    this.allColumns.forEach((item,index) =>{
                       if(item.attrs && item.attrs.width !== undefined &&  parseInt(item.attrs.width) != 0  && $("thead .sh-primary th[data-name="+item.name+"]").length > 0){
                            $("thead .sh-primary th[data-name="+item.name+"]")[0].style.width = `${Math.floor(parseInt(item.attrs.width))}px`;
                            $("thead .sh-primary th[data-name="+item.name+"]")[0].style['max-width'] = `${Math.floor(parseInt(item.attrs.width))}px`;
                            table_width +=parseInt(item.attrs.width)
                            }
                    });
                }

            }else{
                super.freezeColumnWidths();
            }
        },
        computeColumnWidthsFromContent(allowedWidth) {

            if (!this.sh_is_lines){

                const table = this.tableRef.el;

                // Toggle a className used to remove style that could interfere with the ideal width
                // computation algorithm (e.g. prevent text fields from being wrapped during the
                // computation, to prevent them from being completely crushed)
                table.classList.add("o_list_computing_widths");

                const headers = [...table.querySelectorAll("thead .sh-primary th")];
                const columnWidths = headers.map((th) => th.getBoundingClientRect().width);
                const getWidth = (th) => columnWidths[headers.indexOf(th)] || 0;
                const getTotalWidth = () => columnWidths.reduce((tot, width) => tot + width, 0);
                const shrinkColumns = (thsToShrink, shrinkAmount) => {
                    let canKeepShrinking = true;
                    for (const th of thsToShrink) {
                        const index = headers.indexOf(th);
                        let maxWidth = columnWidths[index] - shrinkAmount;
                        // prevent the columns from shrinking under 92px (~ date field)
                        if (maxWidth < 92) {
                            maxWidth = 92;
                            canKeepShrinking = false;
                        }
                        th.style.maxWidth = `${Math.floor(maxWidth)}px`;
                        columnWidths[index] = maxWidth;
                    }
                    return canKeepShrinking;
                };
                // Sort columns, largest first
                const sortedThs = [...table.querySelectorAll("thead .sh-primary th:not(.o_list_button)")].sort(
                    (a, b) => getWidth(b) - getWidth(a)
                );

                let totalWidth = getTotalWidth();
                for (let index = 1; totalWidth > allowedWidth; index++) {
                    // Find the largest columns
                    const largestCols = sortedThs.slice(0, index);
                    const currentWidth = getWidth(largestCols[0]);
                    for (; currentWidth === getWidth(sortedThs[index]); index++) {
                        largestCols.push(sortedThs[index]);
                    }

                    // Compute the number of px to remove from the largest columns
                    const nextLargest = sortedThs[index];
                    const toRemove = Math.ceil((totalWidth - allowedWidth) / largestCols.length);
                    const shrinkAmount = Math.min(toRemove, currentWidth - getWidth(nextLargest));

                    // Shrink the largest columns
                    const canKeepShrinking = shrinkColumns(largestCols, shrinkAmount);
                    if (!canKeepShrinking) {
                        break;
                    }

                    totalWidth = getTotalWidth();
                }

                // We are no longer computing widths, so restore the normal style
                table.classList.remove("o_list_computing_widths");
                return columnWidths;
            }else{
                return super.computeColumnWidthsFromContent(...arguments);
            }
    },


    onStartResize(ev) {
        super.onStartResize(...arguments);
        if (!this.sh_is_lines){
            const table = this.tableRef.el;
            const th = ev.target.closest("th");
            const handler = th.querySelector(".o_resize");
            table.style.width = `${Math.floor(table.getBoundingClientRect().width)}px`;
            const thPosition = [...th.parentNode.children].indexOf(th);
            const resizingColumnElements = [...table.getElementsByTagName("tr")]
                .filter((tr) => tr.children.length === th.parentNode.children.length)
                .map((tr) => tr.children[thPosition]);
            const initialX = ev.clientX;
            const initialWidth = th.getBoundingClientRect().width;
            const initialTableWidth = table.getBoundingClientRect().width;
            const resizeStoppingEvents = ["keydown", "mousedown", "mouseup"];

            const stopResize = (ev) => {
                for (const eventType of resizeStoppingEvents) {
                    window.removeEventListener(eventType, stopResize);
                }

                // we remove the focus to make sure that the there is no focus inside
                // the tr.  If that is the case, there is some css to darken the whole
                // thead, and it looks quite weird with the small css hover effect.
                document.activeElement.blur();
                this.sh_data_width = $(resizingColumnElements[0]).innerWidth();
                var sh_field_data_width = this.sh_list_data.fields_data[resizingColumnElements[0].dataset.name];
                sh_field_data_width.sh_width = this.sh_data_width;
                if (!this.sh_list_data.table_data){
                         this.props.sh_initialize_lvm_data(this.sh_list_data.fields_data,true);
                }else{
                    this.props.sh_update_field_data([], [sh_field_data_width], true,true);
                    }

            };
            for (const eventType of resizeStoppingEvents) {
                window.addEventListener(eventType, stopResize);
            }
        }
    },
    async onCellClicked(record, column, ev) {
    if (this.sh_is_lines){
        super.onCellClicked(...arguments);
    }
    if (this.props.activeActions.type == 'view'){
        if (window.getSelection().toString() && this.props.activeActions.type == 'view') {
            return;
        }
        if (this.sh_list_data){
            if (this.sh_lvm_mode && this.sh_list_data.table_data.sh_editable && this.props.activeActions.type == 'view') {
                if (ev.target.special_click) {
                    return;
                }
                const recordAfterResequence = async () => {
                    const recordIndex = this.props.list.records.indexOf(record);
                    await this.resequencePromise;
                    // row might have changed record after resequence
                    record = this.props.list.records[recordIndex] || record;
                };
                if (record.isInEdition && this.props.list.editedRecord === record) {
                    this.focusCell(column);
                    this.cellToFocus = null;
                } else {
                    await recordAfterResequence();
                    await record.switchMode("edit");
                    this.cellToFocus = { column, record };
                }

            } else {
                super.onCellClicked(...arguments);
            }
            }else{
                super.onCellClicked(...arguments);
            }
        }
},

  });

  ListRenderer.components = { ...ListRenderer.components };


ListRenderer.props = [...ListRenderer.props,
    "sh_update_field_data?",
    "sh_initialize_lvm_data?",
    "list_data?",
];
