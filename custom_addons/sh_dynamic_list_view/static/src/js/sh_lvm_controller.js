/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { useListener } from "@web/core/utils/hooks";
import { useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";
import { patch } from "@web/core/utils/patch";
import { renderToElement } from "@web/core/utils/render";
import { renderToFragment } from "@web/core/utils/render";
import { Dialog } from "@web/core/dialog/dialog";
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";
import { listView } from '@web/views/list/list_view';
import { registry } from "@web/core/registry";
import { ListArchParser } from "@web/views/list/list_arch_parser";
import { session } from "@web/session";
import { parseXML } from "@web/core/utils/xml";
import { nbsp } from "@web/core/utils/strings";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { loadJS } from "@web/core/assets";


const { onWillStart, useState, useRef, onMounted, useExternalListener ,onWillUnmount } = owl;

patch(ListController.prototype,  {
    setup(params) {
        var self = this;
        this.tableRef = useRef("table");
        if (session.server_version === '16.0+e' && this.env.services.cookie.current.color_scheme === 'dark'){
                document.body.style.setProperty("--sh_lvm_background_color", '#3b3b3b');
        }
        this.sh_fields_data_dirty = {};
        onMounted(this._mounted);
        this.sh_editable = false;
        this.sh_remove_popup_flag = false;
        onWillStart(async () => {
            await this.willStart();
        });

       return super.setup();
    },
    async willStart() {
        var self = this;
        this.sh_searchdomain = [];
        if (!$.fn.sortable) {
            await loadJS("sh_dynamic_list_view/static/lib/jquery.ui/jquery-ui.js");
        }
        if ((browser.localStorage.getItem("sh_model"))){
            if ((browser.localStorage.getItem("sh_model")) === this.props.resModel && (browser.localStorage.getItem("search_domain")) && this.env.config.actionId == browser.localStorage.getItem("sh_actionid")){
                this.sh_searchdomain = JSON.parse(browser.localStorage.getItem("search_domain"))
            }else{
                browser.localStorage.removeItem("search_domain");
                browser.localStorage.removeItem("sh_model");
                browser.localStorage.removeItem("field_dict");
                browser.localStorage.removeItem("key_field")
            }
            if (this.sh_searchdomain.length){
            this.ShBaseDomain = [...this.props.domain];
            for (let sh_values of this.sh_searchdomain){
                this.props.domain.push(sh_values);
            }
             this.model.load();
        }
     }
        const data = await jsonrpc('/sh_lvm_control/sh_generate_arch_view', {
        'sh_context':this.props.context,
        'sh_model': this.props.resModel,
        'sh_view_id': this.env.config.viewId || false,
        'sh_search_id': this.props.info.searchViewId || false
        });
        if (data) {
            this.data = data;
            this.data.views.list.sh_lvm_user_data['fields'] = data['models'][this.props.resModel];
            this.sh_lvm_data = Object.assign({}, this.data.views.list.sh_lvm_user_data);
            this.currency_id = this.data.views.list.sh_lvm_user_data.sh_lvm_user_mode_data.currency_id;

        }
        this.sh_lvm_data = this.sh_lvm_data ? this.sh_lvm_data : false;
        this.sh_table_data = this.sh_lvm_data && this.sh_lvm_data.sh_lvm_user_table_result ? this.sh_lvm_data.sh_lvm_user_table_result.sh_table_data : false;
        this.sh_lvm_user_mode_data = this.sh_lvm_data ? this.sh_lvm_data.sh_lvm_user_mode_data : false;
        this.sh_user_table_result = this.sh_lvm_data && this.sh_lvm_data.sh_lvm_user_table_result ? this.sh_lvm_data.sh_lvm_user_table_result : false;
        this.userMode = this.sh_lvm_data ? this.sh_lvm_data.sh_lvm_user_mode_data.list_view_data : false;
        this.sh_fields_data = this.sh_user_table_result.sh_fields_data ? self.sh_user_table_result.sh_fields_data : self.ShComputeFieldData(this.props.archInfo, this.props.fields);
        this.sh_field_list = Object.values(this.sh_fields_data).sort((a, b) => a.sh_field_order - b.sh_field_order);
        this.list_data ={"fields_data":this.sh_fields_data,"currency":this.currency_id,"table_data":this.sh_table_data}
        session.list_data  = this.list_data;

        },
        ShComputeFieldData: function (arch, fields) {
            var sh_field_list = {};
            var self = this;
            //            Making Field List
            var sort_counter = arch.columns.length;
             Object.entries(fields).map(([y,x])=> {
                if (y !== "activity_exception_decoration") {
                    sh_field_list[y] = {
                        sh_columns_name: x.string,
                        ShShowField: false,
                        field_name: y,
                        sh_width: 0,
                        sh_field_order: sort_counter,
                        sh_tag: 'field'
                    }
                }
            })
            //            Assigning visible/invisible from arch
            sort_counter = 0;
            arch.columns.map(function (x) {

                if (x.attrs !== undefined){
                    var invis = x.attrs.column_invisible || x.optional === "hide";
                }else{
                    var invis = x.optional === "hide";
                }

                if(x["type"] === "field" || x["type"] === "button_group") {
                    if (sh_field_list.hasOwnProperty(x.name)) {
                        Object.assign(sh_field_list[x.name], {
                            ShShowField: !invis,
                            sh_field_order: sort_counter,
                            sh_columns_name: x.string || sh_field_list[x.name].sh_columns_name,
                            sh_tag: 'field'
                        });
                        sort_counter += 1;
                    } else if (x.name) {
                        if (x.tag === "button_group"){
                                sh_field_list[x.name] = {
                                sh_columns_name: x.string || x.name,
                                ShShowField: !invis,
                                field_name: x.name,
                                sh_width: 0,
                                sh_field_order: sort_counter,
                                sh_tag: 'button'
                            }


                    } else {
                        sh_field_list[x.name] = {
                            sh_columns_name: x.string || "Undefined",
                            ShShowField: !invis,
                            field_name: x.name,
                            sh_width: 0,
                            sh_field_order: sort_counter,
                            sh_tag: 'field'
                        }
                    }
                }
            }
        })
        return sh_field_list;
    },


    _mounted() {
        var self=this;
        var table = this.tableRef;
        this.sh_lvm_mode = true;
        this.sh_resize = false;
        this.sh_enable_list_view_manager = session.sh_enable_list_view_manager
        if(session.sh_enable_list_view_manager){
            $('.sh_list_view_dropdown').show()
        }
        this.sh_lvm_data = {};
        this._sh_init_sortable();
        if(this.sh_table_data.sh_editable == true){
            $("#mode").prop('checked',true);
        }

        if ($('.o_list_buttons').length > 0) {
            if (!this.sh_lvm_user_mode_data.sh_can_edit){
                $('.mode_button').addClass('d-none')
            }
            if (!this.sh_lvm_user_mode_data.sh_can_duplicate){
                $('.copy_button').addClass('d-none')
            }
            if (!this.sh_lvm_user_mode_data.sh_dynamic_list_show){
                $('.toggle_button').parent().addClass('d-none');
            }
            if (!this.sh_lvm_user_mode_data.sh_can_advanced_search){
                $('.hide-on-modal').addClass('d-none');
            }
        }

    },

    _sh_init_sortable() {
        if (this.sh_lvm_mode) {
            var self = this;
            $(".sh_columns_list").sortable({
                axis: 'y',
                update: function (event, ui) {
                    self._sh_update_fields_order(event, ui);
                }
            });
        if (session.sh_toggle_color) {
             $("input:checked + .sh_slider").css("background-color", session.sh_toggle_color);
        }
        }
    },
    sh_searchBar(e) {
        if ($(e.target).hasClass("myinput")) {
            if (this.sh_lvm_mode) {
                var sh_input = e.target.value.toUpperCase();
                ($(".sh_columns_list").children().each(function (index,$field) {
                    $field.style.display = $field.dataset.sh_columns_name.toUpperCase().indexOf(sh_input) > -1 ? "" : "none";
                }))
            }
        }
    },

    async sh_update(params) {
        await this.actionService.restore(this.actionService.currentController.jsId)

    },
    async sh_toggle_update() {
        const list = this.model.root
        var self = this
        for(const j in self.sh_fields_data){
            if(!this.model.config.activeFields.hasOwnProperty(j)){
                if(self.sh_fields_data[j].ShShowField){
                   let copyField = this.model.config.activeFields.name;
                   this.model.config.activeFields[self.sh_fields_data[j].field_name] = copyField
                }
            }
        }
        await list.load();
        this.render(true);
    },

    // Update Field Status in LVM DB. TODO: Add condition to either update data or not
    sh_update_field_data(sh_table_data, sh_field_data, sh_reset_renderer,toggle_mode) {
        if (this.sh_lvm_mode) {
            var self = this;
            if (!self.sh_table_data) {
                return self.sh_initialize_lvm_data(this.sh_fields_data,false);
            }

            var sh_reset_renderer = sh_reset_renderer;

            var sh_fetch_options = {
                'sh_context':this.props.context,
                'sh_model': this.props.resModel,
                'sh_view_id': this.env.config.viewId || false,
                'sh_search_id': self.props.info.searchViewId
            }

           return jsonrpc('/sh_lvm_control/update_list_view_data', {
                'sh_table_data': sh_table_data,
                'sh_fields_data': sh_field_data,
                'sh_fetch_options': sh_fetch_options,


            }).then(function (sh_list_view_data) {
                if (sh_reset_renderer) {
                    const archXmlDoc = parseXML(sh_list_view_data.views.list.arch.replace(/&amp;nbsp;/g, nbsp));
                    var archInfo = new ListArchParser().parse(archXmlDoc, self.props.relatedModels, self.props.resModel);
                    Object.assign(self.archInfo, archInfo);
                    Object.assign(self.model.root.activeFields, self.archInfo.activeFields);
                    self.sh_resize = false;
                    if (toggle_mode == false){
                        self.sh_update(sh_list_view_data);
                        self.env.bus.trigger("CLEAR-CACHES");
                    }else{
                        self.sh_toggle_update()
                    }
                };
            });

        }
    },


    // Initialize LVM data in Database
    sh_initialize_lvm_data: function (sh_fields_data,toggle_mode) {
        if (this.sh_lvm_mode) {
            var self = this;
            var sh_table_width_px = $('.o_list_table').width();
            //patchy code to convert float number up to two decimal precisions
            var sh_table_width_per = +(((sh_table_width_px / $(window).width()) * 100).toFixed(14))

              return  jsonrpc('/sh_lvm_control/create_list_view_data', {
                   'sh_context' :this.props.context,
                    'sh_model': this.model.root.resModel,
                    'sh_editable':this.sh_editable,
                    'sh_view_id': this.env.config.viewId || false,
                    'sh_table_width_per': sh_table_width_per || 99.45,
                    'sh_fields_data': sh_fields_data,
                    'sh_resize': self.sh_resize,
                    'sh_search_id': self.props.info.searchViewId,
                })
                .then(function (sh_list_view_data) {
                    self.sh_table_data = sh_list_view_data.views.list.sh_lvm_user_data.sh_lvm_user_table_result.sh_table_data;
                    self.sh_fields_data = sh_list_view_data.views.list.sh_lvm_user_data.sh_lvm_user_table_result.sh_fields_data;
                    self.list_data.fields_data = self.sh_fields_data;
                    self.list_data.table_data = self.sh_table_data;
                    self.sh_resize = false;
                    self.sh_field_list = Object.values(self.sh_fields_data).sort((a, b) => a.sh_field_order - b.sh_field_order);
                    var archXmlDoc = parseXML(sh_list_view_data.views.list.arch.replace(/&amp;nbsp;/g, nbsp));
                    var archInfo = new ListArchParser().parse(archXmlDoc, self.props.relatedModels, self.props.resModel);
                    Object.assign(self.archInfo, archInfo),
                    Object.assign(self.model.root.activeFields, self.archInfo.activeFields);
                    if (toggle_mode == false){
                        self.sh_update(sh_list_view_data);
                        self.env.bus.trigger("CLEAR-CACHES");
                    }else{
                        self.sh_toggle_update(sh_list_view_data)
                    }

                });
        }

    },

    sh_confirm_restoreData: function (event) {
        if (this.sh_lvm_mode) {
        var self = this;
        self.sh_resize = false;
        this.env.services.dialog.add(ConfirmationDialog, {
            body: _t("Are you sure you want to restore to Odoo default View?"),
            confirm: () => {
                 self.sh_is_restore_flag = true;
                 self.ShResetLvmData();
            },
            cancel: () => {},
        });
        }
    },
    ShResetLvmData: function () {
            if (this.sh_lvm_mode) {
                var self = this;
                if (this.sh_table_data) {
                    return jsonrpc("/sh_lvm_control/sh_reset_list_view_data",{
                            'sh_context':this.props.context,
                            'sh_model': this.model.root.resModel,
                            'sh_view_id': this.env.config.viewId || false,
                            'sh_lvm_table_id': this.sh_table_data.id,
                            'sh_search_view_id': self.props.info.searchViewId
                        }).then(function (sh_list_view_data) {
                            self.ShResetControllerData(sh_list_view_data);

                    });
                }
                return $.when();
            }
        },
         ShResetControllerData(data) {
            if (this.sh_lvm_mode) {
                var self = this;
                if (data){
                    this.data = data;
                    this.data.views.list.sh_lvm_user_data['fields'] = data['models'][this.props.resModel];
                    this.sh_lvm_data = Object.assign({}, this.data.views.list.sh_lvm_user_data);
                    this.currency_id = this.data.views.list.sh_lvm_user_data.sh_lvm_user_mode_data.currency_id;
                }
              const archXmlDoc = parseXML(data.views.list.arch.replace(/&amp;nbsp;/g, nbsp));
                var archInfo = new ListArchParser().parse(archXmlDoc, self.props.relatedModels, self.props.resModel);

            Object.assign(self.archInfo, archInfo),
            Object.assign(self.model.root.activeFields, self.archInfo.activeFields);
            this.sh_lvm_data = this.sh_lvm_data ? this.sh_lvm_data : false;
            this.sh_table_data = this.sh_lvm_data && this.sh_lvm_data.sh_lvm_user_table_result ? this.sh_lvm_data.sh_lvm_user_table_result.sh_table_data : false;
            this.sh_lvm_user_mode_data = this.sh_lvm_data ? this.sh_lvm_data.sh_lvm_user_mode_data : false;
            this.sh_user_table_result = this.sh_lvm_data && this.sh_lvm_data.sh_lvm_user_table_result ? this.sh_lvm_data.sh_lvm_user_table_result : false;
            this.userMode = this.sh_lvm_data ? this.sh_lvm_data.sh_lvm_user_mode_data.list_view_data : false;
            this.sh_fields_data = this.sh_user_table_result.sh_fields_data ? self.sh_user_table_result.sh_fields_data : self.ShComputeFieldData(this.props.archInfo, this.props.fields);
            this.sh_field_list = Object.values(this.sh_fields_data).sort((a, b) => a.sh_field_order - b.sh_field_order);
            this.list_data ={"fields_data":this.sh_fields_data,"currency":this.currency_id,"table_data":this.sh_table_data}
            this.sh_lvm_user_mode_data = false;
            self.sh_update(data);
            self.env.bus.trigger("CLEAR-CACHES");
            self._sh_init_sortable()

            }
        },



     _OnShSpanFieldEditableClick(event) {
        if ($(event.target).hasClass("sh_editable_span")) {
            if (this.sh_lvm_mode) {
                event.stopPropagation();
                var self = this;
                var sh_field_id = event.target.dataset.fieldId;
                var $field_span_el = $(event.target);
                var $field_input_el = $(this.rootRef.el).find('input.sh_editable[data-field-id=' + sh_field_id + ']');
                var name = this.sh_fields_data[sh_field_id].sh_columns_name;
                $field_input_el.val(name);
                $field_span_el.hide();
                $field_input_el.removeClass("d-none");
                $field_input_el.focus();
                $(".cancel_button").removeClass("d-none");
            }
        }
    },

     _OnShInputFieldEditableFocusout(event) {
        if ($(event.target).hasClass("sh_editable_input")) {
            if (this.sh_lvm_mode) {
                event.stopPropagation();
                var self = this;
                var sh_field_id = event.target.dataset.fieldId;
                var $field_span_el = $(self.rootRef.el).find('span.sh_editable[data-field-id=' + sh_field_id + ']');
                var $field_input_el = $(event.target)
                var name = self.sh_fields_data[sh_field_id].sh_columns_name;
                var input_val = $field_input_el.val();

                if (input_val.length !== 0) {
                    $field_span_el.text(input_val);
                    self.sh_fields_data_dirty[sh_field_id] = Object.assign({}, self.sh_fields_data_dirty[sh_field_id], {
                        sh_columns_name: input_val,
                        id: self.sh_fields_data[sh_field_id].id,
                    })
                }
                $field_span_el.show();
                $field_input_el.addClass("d-none");
            }
        }
    },
     _OnShCancelButtonClick(event) {
        if ($(event.target).hasClass("cancel_button")) {
            if (this.sh_lvm_mode) {
                event.stopPropagation();
                var self = this;
              Object.keys(self.sh_fields_data_dirty).map((sh_field_id)=>{
               var $field_span_el = $(self.rootRef.el).find('span.sh_editable[data-field-id=' + sh_field_id + ']');
               var name = self.sh_fields_data[sh_field_id].sh_columns_name;
                $field_span_el.text(name);
              });
                self.sh_fields_data_dirty = {};
                $(".cancel_button").addClass("d-none");
            }
        }
    },

     _OnShHideLvmDropDown(event) {
        if (this.sh_lvm_mode) {
                event.stopPropagation();
                var self = this;

                // Box Hide Reset View
                $(".cancel_button").addClass("d-none");
                $("#myInput").val("");
                ($(".sh_columns_list").children().each(function (index,$field) {
                    $field.style.display = "";
                }))

                // Hack code to control drop down button click again when drop down is active
//                if (!event.hasOwnProperty("clickEvent")) return false;

                // Handle BS hide : Write Dirty Data
//                if (!$(".sh_lvm_dd").has(event.clickEvent.target).length > 0) {
                    if (Object.keys(self.sh_fields_data_dirty).length > 0 && !self.sh_is_restore_flag) {
                        var sh_update_field_list = [];

                        Object.entries(self.sh_fields_data_dirty).map(([key,value])=> {
                            sh_update_field_list.push(value);
                            self.sh_fields_data[key]['sh_columns_name'] = value['sh_columns_name'];
                        })
                        self.sh_update_field_data([], sh_update_field_list, true,false)
                    }
                    self.sh_is_restore_flag = false;
                    self.sh_fields_data_dirty = {};
//                }
//                return !$(".sh_lvm_dd").has(event.clickEvent.target).length > 0;
            }Object.keys(self.sh_fields_data_dirty).map((sh_field_id)=>{
                var $field_span_el = $(self.rootRef.el).find('span.sh_editable[data-field-id=' + sh_field_id + ']');
                var name = self.sh_fields_data[sh_field_id].sh_columns_name;
                $field_span_el.text(name);
             });
             self.sh_fields_data_dirty = {};


    },
         _OnShFieldActiveClickrender(event) {
                if (this.sh_lvm_mode) {
                event.stopPropagation();
                var self = this;
                self.sh_list_data = self.list_data ? self.list_data : session.list_data
                self.sh_resize = false;
                if (session.sh_toggle_color) {
                    $("input:checked + .sh_slider").css("background-color", session.sh_toggle_color);
                    $("input:not(:checked) + .sh_slider").css("background-color", "");
                }
                var sh_field_data = self.sh_list_data.fields_data[event.target.dataset.field_name];
                sh_field_data.ShShowField = event.target.checked;
                if (!self.sh_list_data.table_data){
                    return self.sh_initialize_lvm_data(this.sh_list_data.fields_data,false);
                }
                self.sh_update_field_data([], [sh_field_data], true,false);
            }

    },

    _sh_update_fields_order(event, ui) {
        if (this.sh_lvm_mode) {
            var self = this;
            var sort_counter = 0;
            ($(".sh_columns_list").children().each(function (index,$field) {
                if(self.sh_fields_data[$field.dataset.field_name]){
                self.sh_fields_data[$field.dataset.field_name].sh_field_order = sort_counter;
                sort_counter += 1;
                }
            }))

            if (!self.sh_table_data) {
                return self.sh_initialize_lvm_data(self.sh_fields_data,false);
            }

            self.sh_update_field_data([], Object.values(self.sh_fields_data), true,false);
        }
    },

});

