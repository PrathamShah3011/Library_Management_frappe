# Copyright (c) 2024, Pratham Shah and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LibraryMembership(Document):
    def before_save(self):
        if self.to_date < self.from_date:
            frappe.throw("'From Date' cannot be greater than 'To Date'")
    
    def before_submit(self):
        exists = frappe.db.exists(
            'Library Membership',
            {
                'library_member': self.library_member,
                'docstatus': 1,
                'to_date': ('>', self.from_date),
            },
        )
        if exists:
            frappe.throw('There is an active membership for this member')
            
        loan_period = frappe.db.get_single_value('Library Settings', 'loan_period')
        self.to_date = frappe.utils.add_days(self.from_date, loan_period or 30)