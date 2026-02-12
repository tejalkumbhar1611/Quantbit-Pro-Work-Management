# Copyright (c) 2026, Quantbit Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class Applicant(Document):
    def validate(self):
        self.handle_applicant_type()

    def handle_applicant_type(self):
        if self.applicant_type == "Employee":
            if not self.employee:
                frappe.throw("Employee is required when Applicant Type is Employee.")
            employee = frappe.get_doc("Employee", self.employee)
            self.full_name = employee.employee_name
        elif self.applicant_type == "External":
            if not self.full_name:
                frappe.throw("Full Name is required for External Applicant.")
