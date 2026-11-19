import {CardCompiler} from "@web/views/card/card_compiler";

// Odoo 20: the kanban records are compiled by the shared card compiler
export class AutomationKanbanCompiler extends CardCompiler {
    setup() {
        super.setup();
        this.compilers.push({
            selector: ".o_automation_kanban_child_add_button[t-att-trigger-type]",
            fn: this.compileHierarchyAddButton,
        });
    }

    compileHierarchyAddButton(el) {
        el.setAttribute(
            "t-on-click",
            "() => __comp__.addNewChild({trigger_type: " +
                el.getAttribute("t-att-trigger-type") +
                "})"
        );
        return el;
    }
}
