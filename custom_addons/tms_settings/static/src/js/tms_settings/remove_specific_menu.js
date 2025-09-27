/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { UserMenu } from "@web/webclient/user_menu/user_menu";

// Define the patch
patch(UserMenu.prototype, {
    setup(...args) {
        // Call the original setup method if it exists
       super.setup(...args);
        // Remove specific menu items from the registry
        const categoriesToRemoveFrom = ["user_menuitems"]; // Add category names here
        const itemsToRemove = ["documentation", "support", "shortcuts", "odoo_account"]; // Add item IDs here

        categoriesToRemoveFrom.forEach(category => {
            itemsToRemove.forEach(itemId => {
                registry.category(category).remove(itemId);
            });
        });
    },
});


