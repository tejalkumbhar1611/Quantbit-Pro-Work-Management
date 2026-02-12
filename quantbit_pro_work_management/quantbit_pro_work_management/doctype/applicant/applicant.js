// Copyright (c) 2026, Quantbit Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Applicant", {
    employee: function(frm) {
        if (frm.doc.applicant_type === "Employee" && frm.doc.employee) {
            frappe.db.get_value(
                "Employee",
                frm.doc.employee,
                "employee_name"
            ).then(r => {
                if (r.message) {
                    frm.set_value("full_name", r.message.employee_name);
                }
            });
        }
    }
});
