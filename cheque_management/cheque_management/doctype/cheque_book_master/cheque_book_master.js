// Copyright (c) 2026, Finbyz Tech Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cheque Book Master", {
    start_cheque_no: function(frm) {
        calculate_total_cheques(frm);
    },
    end_cheque_no: function(frm) {
        calculate_total_cheques(frm);
    }
});

function calculate_total_cheques(frm) {
    let start = frm.doc.start_cheque_no;
    let end = frm.doc.end_cheque_no;

    if (start && end) {
        let total = (end - start) + 1;

        if (total > 0) {
            frm.set_value('total_cheques', total);
        }
    }
}