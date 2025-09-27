/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { DomainSelectorDialog } from "@web/core/domain_selector_dialog/domain_selector_dialog";
import { getDomainDisplayedOperators } from "@web/core/domain_selector/domain_selector_operator_editor";
import { getDefaultValue } from "@web/core/tree_editor/tree_editor_value_editors";
import { useService } from "@web/core/utils/hooks";
import { useGetDefaultLeafDomain } from "@web/core/domain_selector/utils";
import { _t } from "@web/core/l10n/translation";
import {
    domainFromTree,
    condition,
 } from "@web/core/tree_editor/condition_tree";


patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.getDefaultLeafDomain = useGetDefaultLeafDomain();
    },

    getDefaultColumnCondition(fieldDef) {
        const operator = getDomainDisplayedOperators(fieldDef)[0];
        const value = getDefaultValue(fieldDef, operator);
        return domainFromTree(condition(fieldDef.name, operator, value));
    },

    // getDefaultColumnCondition(fieldDef, value) {
    //     // debugger
    //     const operator = getDomainDisplayedOperators(fieldDef)[2];
    //     // const value = getDefaultValue(fieldDef, operator);
    //     return domainFromTree(condition(fieldDef.name, operator, value));
    // },

    getColumnFieldDef(name) {
        return this.fields[name];
    },

    // Override
    onClickSearchColumn(column) {
        this.preventReorder = true;
        // super.onClickSortColumn(column);
        const { domainEvalContext: context, resModel } = this.env.searchModel;
        const columnFieldDef = this.getColumnFieldDef(column.name)
        const domain =  this.getDefaultColumnCondition(columnFieldDef);
        this.dialogService.add(DomainSelectorDialog, {
            resModel,
            defaultConnector: "|",
            domain,
            context,
            onConfirm: (domain) => this.env.searchModel.splitAndAddDomain(domain),
            disableConfirmButton: (domain) => domain === `[]`,
            title: _t("Add Custom Filter"),
            confirmButtonText: _t("Add"),
            discardButtonText: _t("Cancel"),
            isDebugMode: this.env.searchModel.isDebugMode,
        });
    }


    // onClickSearchColumnCustom(ev, column) {
    //     console.log(">>>>>>>>>>> ev", ev)
    //     console.log(">>>>>>>>>>> column", column)
    //     // debugger
    //     const value = ev.currentTarget.parentElement.firstElementChild.value;
    //     console.log(">>>>>>>>>>>>>> value of search", value)
    //     // alert(">>>>>>>>>> success ")
    //     const columnFieldDef = this.getColumnFieldDef(column.name)
    //     console.log(">>>>>>>>>>> columnFieldDef", columnFieldDef)
    //     const domain =  this.getDefaultColumnCondition(columnFieldDef, value);
    //     // const domain = [(column.name, 'ilike', value)]
    //     // debugger
    //     console.log(">>>>>>>>>> domain", domain)
    //     // this.env.searchModel.splitAndAddDomain(domain);
    //     debugger
    // }


});
