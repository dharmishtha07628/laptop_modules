/** @odoo-module **/
import { SearchView } from "@sh_dynamic_list_view/component/search_view";
import {AccountMoveUploadListRenderer} from "@account/components/bills_upload/bills_upload";
import {ExpenseListRenderer} from "@hr_expense/views/list";
import {ExpenseDashboardListRenderer} from"@hr_expense/views/list";
import {PurchaseDashBoardRenderer} from "@purchase/views/purchase_listview";

  AccountMoveUploadListRenderer.components = {...AccountMoveUploadListRenderer.components,SearchView};
  ExpenseListRenderer.components = {...ExpenseListRenderer.components,SearchView};
  ExpenseDashboardListRenderer.components = {...ExpenseDashboardListRenderer.components,SearchView};
  PurchaseDashBoardRenderer.components = {...PurchaseDashBoardRenderer.components,SearchView};
