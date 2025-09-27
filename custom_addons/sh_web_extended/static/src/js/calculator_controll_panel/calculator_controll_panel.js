/* @odoo-module */

// ===========================================
//  Calculator Controll Panel
// ===========================================

import { Component, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { ControlPanel } from "@web/search/control_panel/control_panel";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

export class CalcDialog extends ConfirmationDialog {

    setup() {
        this.state = useState({ calculate_result: '' });
        this.CalcInput = useRef('CalcInput');
    }

    appendToResult(value) {
        if (this.state.calculate_result === 'Error') {
            this.state.calculate_result = '';
        }
        this.state.calculate_result += value;
    }

    clearResult(ev) {
        this.state.calculate_result = '';
    }

    calculate(ev) {
        try {
            let expression = this.state.calculate_result;

            // Handle special cases for square, square root, and percentage
            expression = expression.replace(/\^2/g, '**2');
            expression = expression.replace(/√/g, 'Math.sqrt');

            // Replace percentage values with correct calculation
            expression = expression.replace(/(\d+\.?\d*)%/g, '(($1) / 100) * 100');

            const result = eval(expression);
            this.state.calculate_result = result;
        } catch (error) {
            this.state.calculate_result = 'Error';
        }
    }

    async _onKeydown(event) {
        this.state.calculate_result = this.CalcInput.el.value;
        event.preventDefault();
        const key = event.key;
        if (key === 'Enter') {
            event.preventDefault();
            this.calculate();
        } else if (key === 'C') {
            this.clearResult();
        } else {
            this.appendToResult(key);
        }
    }

    async _ec_btn_click(ev) {
        ev.preventDefault();
        const key = ev.currentTarget.getAttribute('data-key');
        this.state.calculate_result = this.CalcInput.el.value;
        if (key === '=') {
            this.calculate();
        } else if (key === 'C') {
            this.clearResult();
        } else if (key === 'x^2') {
            this.appendToResult('^2');
        } else if (key === '√') {
            this.appendToResult('√(');
        } else if (key === '%') {
            this.appendToResult('%');
        } else {
            this.appendToResult(key);
        }
    }
}

CalcDialog.template = "sh_backmate_theme_adv.CalcDialog";

export class CalculaterSh extends Component {

    setup() {
        this.dialogService = useService("dialog");
        // this.search_sh_enable_calculator_mode();
    }

    // search_sh_enable_calculator_mode() {
    //     this.sh_enable_calculator_mode = session.sh_enable_calculator_mode;
    // }

    onClickCalculator() {
        this.dialogService.add(CalcDialog, {
            title: _t("Calculator"),
            body: _t(''),
        });
    }
}

CalculaterSh.template = "sh_backmate_theme_adv.CalculatorCPTemplate";

ControlPanel.components = {
    ...ControlPanel.components,
    CalculaterSh,
}
