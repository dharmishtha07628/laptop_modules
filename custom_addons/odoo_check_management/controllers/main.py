# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

# 2 :  imports of odoo

import logging

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug

_logger = logging.getLogger(__name__)


class BankCheckManagement(http.Controller):
    @http.route('/bank/check/<model("res.bank"):bank_check_id>', type='http', auth="user", website=True)
    def bank_check_management(self, bank_check_id, **post):
        values = {"bank_check_obj": bank_check_id}
        return request.render("odoo_check_management.bank_check_management_template", values)

    @http.route('/bank/check/update', type='http', auth="user", website=True)
    def bank_check_update_attrs(self, **post):
        is_updated = False
        if post.get("check_attribute_line_id"):
            is_updated = request.env["bank.check.attribute.line"].browse(
                int(post.get('check_attribute_line_id'))).write({
                    "top_displacement": int(post.get("y1", 0)),
                    "left_displacement": int(post.get("x1")) if post.get("x1") else 0,
                    "height": int(post.get("h")) if post.get("h") else 0,
                    "width": int(post.get("w")) if post.get("w") else 0,
                    # "font_size": post.get(""),
                    # "font_family": post.get(""),
                })
        values = {
            "bank_check_obj": request.env["res.bank"].browse(int(post.get('bank_check_id')))
            if post.get('bank_check_id') else False,
        }
        if is_updated:
            values.update({
                "updated_check_attribute_line_id": int(post.get('check_attribute_line_id'))
            })
        # return self.bank_check_management(
        #     bank_check_id=values.get("bank_check_obj"))
        # post = {}
        # return request.render("odoo_check_management.bank_check_management_template", values)
        return request.redirect("/bank/check/%s" % slug(values.get("bank_check_obj")))

    @http.route('/bank/check/preview/<model("res.bank"):bank_check_id>', type='http', auth="user", website=True)
    def bank_check_preview(self, bank_check_id, **post):
        values = {"bank_check_obj": bank_check_id}
        return request.render("odoo_check_management.bank_check_priview", values)
