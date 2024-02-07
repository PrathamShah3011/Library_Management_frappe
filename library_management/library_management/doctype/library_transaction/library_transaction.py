# Copyright (c) 2024, Pratham Shah and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LibraryTransaction(Document):
    # Validate Membership
    def validate_membership(self):
        # check if a valid membership exist for this library member
        valid_membership = frappe.db.exists(
            'Library Membership',
            {
                'library_member': self.library_member,
                'docstatus': 1,
                'from_date': ('<', self.date),
                'to_date': ('>', self.date),
            },
        )
        if not valid_membership:
            frappe.throw('The member does not have a valid membership')
            
    def validate_maximum_limit(self):
        max_articles = frappe.db.get_single_value('Library Settings', 'max_articles')
        count = frappe.db.count(
            'Library Transaction',
            {'library_member': self.library_member, 'type': 'Issue', 'docstatus': 1},
        )
        if count >= max_articles:
            frappe.throw('Maximum limit reached for issuing articles')
            
    def validate_issue(self):
        self.validate_membership()
        self.validate_membership()
        article = frappe.get_doc("Article",self.article)
        if article.status == 'Issued':
            frappe.throw('Article is already issued by another member')
            
    def validate_return(self):
        article = frappe.get_doc('Article', self.article)
        # article cannot be returned if it is not issued first
        if article.status == 'Available':
            frappe.throw('Article cannot be returned without being issued first')

#####   MAIN   #######
    def before_submit(self):
        if self.type == 'Issue':
            self.validate_issue()
            article = frappe.get_doc('Article',self.article)
            article.status = 'Issued'
            article.save()
            
        elif self.type == 'Return':
            self.validate_return()
            article = frappe.get_doc('Article', self.article)
            article.status = 'Available'
            article.save()
                        
