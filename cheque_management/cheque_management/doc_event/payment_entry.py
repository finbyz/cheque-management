import frappe

def validate(self, method):
    if self.payment_type == "Cheque":
        
        if not self.cheque_book_leave_ref:
            return

        # Fetch required fields in one query
        cheque_data = frappe.db.get_value(
            "Cheque Book Leave",
            self.cheque_book_leave_ref,
            ["status", "cheque_book_master_no"],
            as_dict=True
        )

        if not cheque_data:
            return

        # Status validation
        if cheque_data.status in ["Used", "Cancelled"]:
            frappe.throw(
                f"This cheque is {cheque_data.status.lower()}. Please select another cheque."
            )

        # Fetch issue date directly
        issue_date = frappe.db.get_value(
            "Cheque Book Master",
            cheque_data.cheque_book_master_no,
            "cheque_book_issue_date"
        )

        # Date validation
        if issue_date and self.posting_date < issue_date:
            frappe.throw(
                f"Cheque cannot be used before its issue date "
                f"({frappe.utils.formatdate(issue_date)})."
            )

def on_submit(self,method):
    if self.payment_type == "Cheque":
        
        if  self.cheque_book_leave_ref:
            cheque_book_leave = frappe.get_doc("Cheque Book Leave", self.cheque_book_leave_ref)
            cheque_book_leave.status = "Used"
            cheque_book_leave.party_type = self.party_type
            cheque_book_leave.party = self.party
            cheque_book_leave.paid_amount = self.paid_amount
            cheque_book_leave.payment_entry = self.name
            cheque_book_leave.date_used = self.posting_date
            cheque_book_leave.save(ignore_permissions=True)
        
@frappe.whitelist()
def custom_cancel_payment_entry(name, status):
    doc = frappe.get_doc("Payment Entry", name)

    if doc.docstatus != 1:
        frappe.throw("Only submitted document can be cancelled")

    # Update cheque status
    if doc.cheque_book_leave_ref:
        cheque_doc = frappe.get_doc("Cheque Book Leave", doc.cheque_book_leave_ref)
        
        if status == "Unused":
            cheque_doc.status = "Unused"
            cheque_doc.party_type = ""
            cheque_doc.party = ""
            cheque_doc.paid_amount = ""
            cheque_doc.payment_entry = ""
            cheque_doc.date_used = ""
            
        elif status == "Cancelled":
            cheque_doc.status = "Cancelled"

        cheque_doc.save()

    # Allow cancel
    frappe.flags.allow_custom_cancel = True

    doc.cancel()

    return True