frappe.ui.form.on('Payment Entry', {
     setup: function(frm) {

        // Filter Cheque Book Master (hide cancelled)
        frm.set_query("cheque_book_master_ref", function() {
            return {
                filters: {
                    docstatus: ["!=", 2]
                }
            };
        });

        // Filter Cheque Book Leave (by master + status)
        frm.set_query("cheque_book_leave_ref", function() {
          
            return {
                filters: {
                    bank_account: frm.doc.bank_account,
                    status: "Unused"
                }
            };
        });

    },

    cheque_book_master_ref: function(frm) {
        // Clear leave when master changes
        frm.set_value("cheque_book_leave_ref", "");
    },
    cheque_book_leave_ref: function(frm) {
        if (frm.doc.cheque_book_leave_ref) {
            frappe.db.get_value(
                "Cheque Book Leave",
                frm.doc.cheque_book_leave_ref,
                "status",
                (r) => {
                    if (r.status === "Cancelled") {
                        frappe.throw("You cannot use this Cheque Book Leave because it is cancelled.");
                    }
                }
            );
        }
    },
    refresh(frm) {

    if (frm.doc.docstatus == 1 && frm.doc.mode_of_payment == "Cheque") {

        setTimeout(() => {

            frm.page.btn_secondary.hide();

            frm.add_custom_button(__('Cancel'), function () {

                let d = new frappe.ui.Dialog({
                    title: 'Select Cheque Status',
                    fields: [
                        {
                            label: 'Revert Cheque Status To',
                            fieldname: 'status',
                            fieldtype: 'Select',
                            options: ['Unused', 'Cancelled'],
                            reqd: 1
                        }
                    ],
                    primary_action_label: 'Proceed',
                    primary_action(values) {

                        frappe.call({
                            method: 'cheque_management.cheque_management.doc_event.payment_entry.custom_cancel_payment_entry',
                            args: {
                                name: frm.doc.name,
                                status: values.status
                            },
                            callback: function () {
                                d.hide();
                                frappe.msgprint('Cancelled Successfully');
                                frm.reload_doc();
                            }
                        });

                    }
                });

                d.show();

            });

        }, 500);
    }
}

});