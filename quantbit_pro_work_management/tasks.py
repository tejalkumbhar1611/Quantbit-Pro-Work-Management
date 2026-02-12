import frappe
from frappe.utils import getdate, nowdate, add_days


def check_document_expiry_notifications():

    today = getdate(nowdate())

    documents = frappe.get_all(
        "Document Application",
        filters={
            "status": ["in", ["Active", "Issued"]]
        },
        fields=[
            "name",
            "expiry_date",
            "new_expiry_date",
            "extended_expiry_date",
            "transaction_type",
            "document_type",
            "applicant",
            "expiry_reminder_sent",
            "expired_notification_sent"
        ]
    )

    for doc in documents:

        expiry_date = get_effective_expiry_date(doc)

        if not expiry_date:
            continue

        expiry_date = getdate(expiry_date)

        # -------------------------------
        # AUTO MARK EXPIRED
        # -------------------------------
        if expiry_date < today:

            if not doc.expired_notification_sent:

                mark_document_expired(doc.name)
                send_expired_notification(doc, expiry_date)

            continue

        # -------------------------------
        # REMINDER BEFORE EXPIRY
        # -------------------------------
        doc_type = frappe.get_doc("Document Type", doc.document_type)

        if not doc_type.reminder_days_before_expiry:
            continue

        reminder_date = add_days(
            expiry_date,
            -doc_type.reminder_days_before_expiry
        )

        if reminder_date == today and not doc.expiry_reminder_sent:
            send_expiry_reminder(doc, expiry_date)


# -----------------------------------------
# GET CORRECT EXPIRY DATE
# -----------------------------------------
def get_effective_expiry_date(doc):

    if doc.transaction_type == "Renewal":
        return doc.new_expiry_date

    elif doc.transaction_type == "Extension":
        return doc.extended_expiry_date

    else:
        return doc.expiry_date


# -----------------------------------------
# MARK DOCUMENT EXPIRED
# -----------------------------------------
def mark_document_expired(docname):

    document = frappe.get_doc("Document Application", docname)

    document.status = "Expired"
    document.expired_notification_sent = 1

    document.save(ignore_permissions=True)


# -----------------------------------------
# SEND REMINDER
# -----------------------------------------
def send_expiry_reminder(doc, expiry_date):

    frappe.sendmail(
        recipients=[frappe.session.user],  # Replace later with applicant email
        subject="Document Expiry Reminder",
        message=f"""
        <b>Reminder:</b><br><br>
        Document: {doc.name}<br>
        Applicant: {doc.applicant}<br>
        Expiry Date: {expiry_date}<br><br>
        Please initiate renewal process.
        """
    )

    frappe.db.set_value(
        "Document Application",
        doc.name,
        "expiry_reminder_sent",
        1
    )


# -----------------------------------------
# SEND EXPIRED ALERT
# -----------------------------------------
def send_expired_notification(doc, expiry_date):

    frappe.sendmail(
        recipients=[frappe.session.user],  # Replace later with applicant email
        subject="Document Expired",
        message=f"""
        <b>Alert:</b><br><br>
        Document: {doc.name}<br>
        Applicant: {doc.applicant}<br>
        Expired On: {expiry_date}<br><br>
        Immediate action required.
        """
    )
