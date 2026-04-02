# Copyright (c) 2026, Finbyz Tech Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ChequeBookMaster(Document):

    def on_submit(self):
        if not self.start_cheque_no or not self.end_cheque_no:
            return

        start = int(self.start_cheque_no)
        end = int(self.end_cheque_no)

        if end < start:
            frappe.throw("End cheque number must be greater than start cheque number")

        created_count = 0

        for cheque_no in range(start, end + 1):  # ✅ include end
            if frappe.db.exists("Cheque Book Leave", {
                "cheque_no": cheque_no,
                "cheque_book_master_no": self.name,
                
            }):
                continue

            cheque = frappe.new_doc("Cheque Book Leave")
            cheque.cheque_no = cheque_no
            cheque.status = "Unused"
            cheque.cheque_book_master_no = self.name
            cheque.bank_account = self.bank_account

            cheque.insert(ignore_permissions=True)
            created_count += 1

        # ✅ show message only once
        frappe.msgprint(
            f"{created_count} cheque(s) created successfully from {start} to {end}"
        )

    def on_cancel(self):
        # Get all related Cheque Book Leave records
        cheque_list = frappe.get_all(
            "Cheque Book Leave",
            filters={"cheque_book_master_no": self.name},
            pluck="name"
        )

        # Delete all records
        for cheque in cheque_list:
            frappe.delete_doc("Cheque Book Leave", cheque, ignore_permissions=True)

        frappe.msgprint("All related Cheque Book Leave records deleted")