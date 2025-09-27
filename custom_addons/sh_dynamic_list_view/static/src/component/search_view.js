/** @odoo-module */

import { Component,useState,useExternalListener,useRef, onMounted} from "@odoo/owl";
import { jsonrpc } from "@web/core/network/rpc_service";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { _t } from "@web/core/l10n/translation";
import { localization } from "@web/core/l10n/localization";
import {formatDate,formatDateTime} from "@web/core/l10n/dates";
import {parseDateTime,parseDate,} from "@web/core/l10n/dates";
import { formatFloat,formatInteger } from "@web/views/fields/formatters";



export class SearchView extends Component {
   setup()  {
        this.state = useState({
            startdate:false,
            enddate:false,
        })

        this.start_date = null;
        this.end_date = null;

        this.apply_daterange = false;
        this.date_start = moment().subtract(30, 'days');
        this.date_end = moment();

        this.sh_autocomplete_data = {};
        this.sh_autocomplete_data_result = {};
        this.root = useRef("root");
        this.sh_allow_search = true;

        onMounted(() => {
            if (this.props.sh_field_type == 'date' || this.props.sh_field_type == 'datetime') {                
                this._updateDates();
            }
        });
   }

   async _updateDates() {
        // debugger
        var reportrange = '#reportrange_' + this.props.sh_field_id;
        $(reportrange).daterangepicker({
            startDate: this.date_start,
            endDate: this.date_end,
            ranges: {
               'Today': [moment(), moment()],
               'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
               'Last 7 Days': [moment().subtract(6, 'days'), moment()],
               'Last 30 Days': [moment().subtract(29, 'days'), moment()],
               'This Month': [moment().startOf('month'), moment().endOf('month')],
               'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            }
        }, this._UpdateDateFilter.bind(this));
        if (this.apply_daterange) {
            this._UpdateDateFilter(this.date_start, this.date_end);
        }
    }

    async _UpdateDateFilter(start, end) {
        this.apply_daterange = true;
        if (start && end) {
            var reportrange = '#reportrange_' + this.props.sh_field_id + ' span';
            // $(reportrange).html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
            this.date_start = start;
            this.date_end = end;

            var self=this

            // code for set start date filter
            var sh_date_field_name = self.props.sh_field_id
            self.start_date = start
            var sh_date_widget = new Date(self.start_date);
            var search_id = self.props.sh_field_id + "_lvm_start_date"
            var field_identity = search_id + " lvm_start_date"
            var sh_options = {
                ShFieldName: self.props.sh_description,
                ShSearchId: search_id,
                Shfieldtype: self.props.sh_field_type,
                ShFieldIdentity:field_identity,
                sh_val: sh_date_widget.toISOString()
            }
            this.props.sh_search_event(sh_options);

            // code for set end date filter
            var sh_date_field_name = self.props.sh_field_id
            self.end_date = end
            var sh_date_widget = new Date(self.end_date);
            var search_id = self.props.sh_field_id + "_lvm_end_date"
            var field_identity = search_id + " lvm_end_date"

            var sh_options = {
                ShFieldName: self.props.sh_description,
                ShSearchId: search_id,
                Shfieldtype: self.props.sh_field_type,
                ShFieldIdentity:field_identity,
                sh_val: sh_date_widget.toISOString()
            }
            this.props.sh_search_event(sh_options);
        }
    }

   async sh_advance_searchbar(request) {
            // block of code for Autocomplete
            var self = this;
            this.sh_allow_search = true;
            var sh_field_type = self.props.sh_field_type;
            var sh_field_name = self.props.sh_field_id;
            var sh_one2many_relation;
            var sh_input_val = request.target.value;

            if (sh_input_val){


                if (sh_field_type === "one2many") {
                    sh_one2many_relation = self.props.list.fields[sh_field_name].relation
                }

                this.env.services.orm.searchRead(self.props.model,[[sh_field_name,"ilike",sh_input_val]],[sh_field_name]).then(function(sh_auto_Data){

                        self.sh_autocomplete_data_result = sh_auto_Data
                        if (self.props.model === 'hr.employee.skill.report' && sh_field_name === 'level_progress'){
                            for (var i=0; i< sh_auto_Data.length; i++){
                                sh_auto_Data[i]['level_progress'] = (sh_auto_Data[i]['level_progress'])*100

                            }

                        }

                        if (!(sh_field_type === "date" || sh_field_type === "datetime" || sh_field_type === "selection")) {
                            var sh_unique_data = {}
                            self.sh_autocomplete_data[sh_field_name] = [];

                            if (sh_field_type === 'one2many') {
                                for (var i = 0; i < self.sh_autocomplete_data_result.length; i++) {

                                    if (!(sh_unique_data[self.sh_autocomplete_data_result[i]])) {
                                        self.sh_autocomplete_data[sh_field_name].push(String(self.sh_autocomplete_data_result[i]));
                                        sh_unique_data[self.sh_autocomplete_data_result[i]] = true;
                                    }
                                }
                            } else if (sh_field_type === 'many2many' || sh_field_type === 'many2one') {
                                for (var i = 0; i < self.sh_autocomplete_data_result.length; i++) {

                                    if (!(sh_unique_data[self.sh_autocomplete_data_result[i][sh_field_name][1]])) {
                                        self.sh_autocomplete_data[sh_field_name].push(String(self.sh_autocomplete_data_result[i][sh_field_name][1]));
                                        sh_unique_data[self.sh_autocomplete_data_result[i][sh_field_name][1]] = true;
                                    }
                                }
                            } else {
                                for (var i = 0; i < self.sh_autocomplete_data_result.length; i++) {

                                    if (!(sh_unique_data[self.sh_autocomplete_data_result[i][sh_field_name]])) {
                                        self.sh_autocomplete_data[sh_field_name].push(String(self.sh_autocomplete_data_result[i][sh_field_name]));
                                        sh_unique_data[self.sh_autocomplete_data_result[i][sh_field_name]] = true;
                                    }
                                }
                            }



                           if (sh_field_type != 'many2many'){
                            $(".custom-control-searchbar-advance[data-name=" + sh_field_name + "]").autocomplete({
                                source: self.sh_autocomplete_data[sh_field_name],
                                response: function (event, ui) {
                                    if (!ui.content.length) {
                                        var noResult = { value: "", label: "No results found" };
                                        ui.content.push(noResult);
                                    }
                                }

                            }).keydown(function(event) {
                                if (event.keyCode == 13) { // Check if Enter key is pressed
                                    $(this).autocomplete("close"); // Close the autocomplete dropdown
                                }
                            });
                        }
                    }
                });

                if (request.keyCode == 8 && this.sh_allow_search) {
                    if (request.target.parentNode.children.length !== 1) {
                        this.props.sh_remove_search(request);
                        this.sh_allow_search = false;
                    }
                }
            if (request.keyCode == 13 && this.sh_allow_search) {
                var options = {
                    ShFieldName: self.props.sh_description,
                    ShSearchId: self.props.sh_field_id,
                    Shfieldtype: self.props.sh_field_type,
                };

                this.props.sh_search_event(options)
                this.sh_allow_search = false;
            }

            }


    }

   sh_on_start_date_filter_change(date,check){
        var self=this
        var sh_date_field_name = self.props.sh_field_id
        if (check === 1){
                self.start_date = $('#start_date').find('#input_start_val').val();
                var sh_date_widget = new Date(self.start_date);
                var search_id = self.props.sh_field_id + "_lvm_start_date"
                var field_identity = search_id + " lvm_start_date"
        }else{
                self.end_date = $('#end_date').find('#input_end_val').val();
                var sh_date_widget = new Date(self.end_date);
                var search_id = self.props.sh_field_id + "_lvm_end_date"
                var field_identity = search_id + " lvm_end_date"
        }
        if (self.start_date){
            $('#end_date').removeClass('d-none');
            $('#start_date').addClass('sh_date_main')

          var sh_options = {
                ShFieldName: self.props.sh_description,
                ShSearchId: search_id,
                Shfieldtype: self.props.sh_field_type,
                ShFieldIdentity:field_identity,
                sh_val: sh_date_widget.toISOString()
          }
          this.props.sh_search_event(sh_options);
        }else{
            $('#end_date').addClass('d-none');
            $('#start_date').removeClass('sh_date_main')
        }
   }


     sh_change_event(e) {
        var self=this;
            if (self.props.sh_field_type !== "datetime" && self.props.sh_field_type !== 'date') {
                var sh_options = {
                    ShFieldName: self.props.sh_description,
                    ShSearchId: self.props.sh_field_id,
                    Shfieldtype: self.props.sh_field_type,
                }
                this.props.sh_search_event(sh_options)

            }

    }

    format_text(data){
        return formatFloat(parseFloat(data),{digits: [0, 2]})
    }
    get placeholder(){
        if (!(this.props.sh_field_type === 'many2one' || this.props.sh_field_type === 'many2many' || this.props.sh_field_type === 'one2many') && !this.props.sh_field_search_info[this.props.sh_field_id]){
            return "Search..."
        }
        else if(this.props.sh_field_type === 'many2one' || this.props.sh_field_type === 'many2many' || this.props.sh_field_type === 'one2many'){
            return "Search..."
        }else{
            return ""
        }
    }
    get value(){
        return ''
    }


   };

    SearchView.template = "sh_list_view_advance_search";
    SearchView.props = {
                   sh_field_id : { type: String ,Optional:true } ,
                   sh_description: { type: String,Optional:true },
                   sh_field_type:  { type: String, Optional:true },
                   sh_selection_values: { type: Array , Optional:true },
                   sh_search_event : {type:Function,Optional:true},
                   model:{type:String,Optional:true},
                   sh_field_search_info:{type:Object , optional:true},
                   sh_remove_search:{type:Function,optional:true}
                };
     SearchView.components={DateTimeInput}
