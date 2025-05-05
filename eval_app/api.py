import frappe
from frappe import _
import traceback

class ApiResponse:
    def __init__(self, success=True, message="", data=None, errors=None):
        self.success = bool(success)
        self.message = message or _("No message")
        self.data = data or {}
        self.errors = errors or []

    def as_dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
        }

def make_response(success=True, message="", data=None, errors=None):
    return ApiResponse(success=success, message=message, data=data, errors=errors).as_dict()


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError as e:
        frappe.clear_messages()
        frappe.log_error(
            title="Authentication Failed",
            message=traceback.format_exc()
        )
        return make_response(
            success=False,
            message=traceback.format_exc(),
        )
    except Exception as e:
        # Catch any unexpected errors
        frappe.log_error(
            title="Login Error",
            message=traceback.format_exc()
        )
        return make_response(
            success=False,
            message="An unexpected error occurred. Please try again later.",
        )

    api_secret = generate_keys(frappe.session.user)
    user = frappe.get_doc('User', frappe.session.user)

    return make_response(
        success=True,
        message="Authentication success",
        data={
            "sid": frappe.session.sid,
            "api_key": user.api_key,
            "api_secret": api_secret,
            "username": user.username,
            "full_name":user.full_name,
            "email": user.email
        }
    )

def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save()

    return api_secret

@frappe.whitelist()
def get_purchase_orders_with_invoices(supplier_name=None):
    try:
        filters = {}
        if supplier_name:
            filters["supplier"] = supplier_name

        # Fetch Purchase Orders
        pos = frappe.get_all("Purchase Order", fields=["*"], filters=filters)

        for po in pos:
            # Query related Purchase Invoices through the 'items' child table
            invoices = frappe.db.get_all(
                "Purchase Invoice",
                filters=[["Purchase Invoice Item", "purchase_order", "=", po.name]],
                fields=["name", "status", "outstanding_amount", "rounded_total"]
            )

            total_paid = 0.0
            inv_len = len(invoices)

            for inv in invoices:
                paid = (inv["rounded_total"] or 0) - (inv["outstanding_amount"] or 0)
                total_paid += paid

            amount_to_paid = po.grand_total or 0

            # Determine custom payment status
            if inv_len > 0 :
                if amount_to_paid != total_paid:
                    po["status"] +=" and Unpaid"
                else:
                    po["status"] +=" and Paid"

            po["invoices"] = invoices


        return make_response(
            success=True,
            message=_("Fetched purchase orders successfully."),
            data=pos
        )

    except Exception:
        frappe.log_error(
            title="Error fetching purchase orders with invoices",
            message=traceback.format_exc()
        )
        return make_response(
            success=False,
            message=_("An error occurred while fetching data."),
            errors=[traceback.format_exc()]
        )

