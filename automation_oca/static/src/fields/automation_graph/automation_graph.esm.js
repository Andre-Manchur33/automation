import {Component, useProps} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useChart} from "@web/core/utils/chart_hook";

export class AutomationGraph extends Component {
    static template = "automation_oca.AutomationGraph";
    props = useProps({...standardFieldProps});

    setup() {
        // Odoo 20: the chart.js bundle loading and the chart life cycle are
        // handled by the core hook; the canvas takes ``this.chart.ref``.
        this.chart = useChart(() => this._getChartConfig());
    }

    _getChartConfig() {
        return {
            type: "line",
            data: {
                labels: this.props.record.data[this.props.name].done.map(function (pt) {
                    return pt.x;
                }),
                datasets: [
                    {
                        backgroundColor: "#4CAF5080",
                        borderColor: "#4CAF50",
                        data: this.props.record.data[this.props.name].done,
                        fill: "start",
                        label: _t("Done"),
                        borderWidth: 2,
                    },
                    {
                        backgroundColor: "#F4433680",
                        borderColor: "#F44336",
                        data: this.props.record.data[this.props.name].error,
                        fill: "start",
                        label: _t("Error"),
                        borderWidth: 2,
                    },
                ],
            },
            options: {
                plugins: {
                    legend: {display: false},
                },
                layout: {
                    padding: {left: 10, right: 10, top: 10, bottom: 10},
                },
                scales: {
                    y: {
                        type: "linear",
                        display: false,
                        beginAtZero: true,
                    },
                    x: {
                        ticks: {
                            maxRotation: 0,
                        },
                    },
                },
                maintainAspectRatio: false,
                elements: {
                    line: {
                        tension: 0.000001,
                    },
                },
                tooltips: {
                    intersect: false,
                    position: "nearest",
                    caretSize: 0,
                    borderWidth: 2,
                },
            },
        };
    }
}

export const AutomationGraphField = {component: AutomationGraph};
registry.category("fields").add("automation_graph", AutomationGraphField);
