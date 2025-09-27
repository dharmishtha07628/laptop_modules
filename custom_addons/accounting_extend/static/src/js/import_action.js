/** @odoo-module **/

import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { ImportAction } from "@base_import/import_action/import_action";
import { useImportModel } from "@base_import/import_model";
import { _t } from "@web/core/l10n/translation";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";

patch(ImportAction.prototype, {
    async setup() {
        super.setup();
        this.state.filelist = false
        const params = this.props.action.params;
        if (params.file_content) {
            const byteCharacters = atob(params.file_content);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], {
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            });
            const file = new File([blob], params.filename, {
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            });

            console.log("File created: ", file);

            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            const fileList = dataTransfer.files;

            // console.log("FileList created: ", fileList);

            this.state.filelist = fileList
            // console.log("this.state.filelist=========", this.state.filelist)
            // debugger;

            this.handleFilesUpload(fileList);
        }
    },

    async handleFilesUpload(files) {
        // console.log("handleFilesUpload=====myyyyyyy=======handleFilesUpload=====myyyyyyy=====handleFilesUpload======")
        if (this.state.filelist){
            // console.log("Yes availabe it is--------------------")
            files = this.state.filelist
        }
        if (!files || files.length <= 0) {
            return;
        }

        this.state.filename = files[0].name;
        this.state.importMessages = [];

        this.model.block(_t("Loading file..."));
        const { res, error } = await this.model.updateData(true);
        console.log("res==========", res)

        if (error) {
            this.state.previewError = error;
        } else {
            this.state.fileLength = res.file_length;
            this.state.previewError = undefined;
        }
        this.model.unblock();
    }
});





















// /** @odoo-module **/

// import { registry } from "@web/core/registry";
// import { patch } from "@web/core/utils/patch";
// import { ImportAction } from "@base_import/import_action/import_action";
// import { _t } from "@web/core/l10n/translation";

// patch(ImportAction.prototype, {
//     async setup() {
//         super.setup();
//         const params = this.props.action.params;
//         if (params.file_content) {
//             const byteCharacters = atob(params.file_content);
//             const byteNumbers = new Array(byteCharacters.length);
//             for (let i = 0; i < byteCharacters.length; i++) {
//                 byteNumbers[i] = byteCharacters.charCodeAt(i);
//             }
//             const byteArray = new Uint8Array(byteNumbers);
//             const blob = new Blob([byteArray], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
//             const file = new File([blob], params.filename, { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
//             console.log("file:================================", file);
//             await this.handleFilesUpload([file, params.filename]);
//         }
//     },
// });

