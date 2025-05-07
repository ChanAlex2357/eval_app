import frappe
from frappe import _
import traceback
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

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
            data = [],
            errors = [traceback.format_exc()]
        )

@frappe.whitelist()
def make_payment_entry(paid_amount, doc_name):

    try:
        # pi = frappe.get_doc("Purchase Invoice", doc_name)
        payment_entry = get_payment_entry(dt="Purchase Invoice" , dn = doc_name)

        payment_entry.paid_amount = paid_amount
        payment_entry.reference_no = doc_name

        for reference in payment_entry.references:
            reference.allocated_amount = paid_amount
        payment_entry.submit()
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()

    return make_response(True,"Payment effectuer",payment_entry)


@frappe.whitelist()
def get_request_quotation_list(supplier=None):

    filters = None
    if supplier :
        filters = [["Request for Quotation Supplier","supplier_name","=",supplier]]

    requests = frappe.db.get_list(
        "Request for Quotation",
        filters = filters,
        fields = ["*"]
    )
    return make_response(True,"Request for Quotations",requests)

@frappe.whitelist()
def get_quotations_for_rfq(rfq_name, supplier=None):
    """
    Récupère les devis fournisseurs uniques pour une RFQ
    Args:
        rfq_name (str): Nom de la Request for Quotation
        supplier (str, optional): Nom du fournisseur à filtrer
    Returns:
        dict: {success: bool, message: str, data: list}
    """
    # Initialisation du filtre de base
    filters = {"request_for_quotation": rfq_name}
    
    # Ajout du filtre fournisseur si spécifié
    if supplier:
        filters["supplier"] = supplier
    
    # Récupération des devis
    quotations = frappe.get_all(
        "Supplier Quotation",
        filters=filters,
        fields=["name", "supplier", "grand_total", "status"],
        # distinct=True  # Garantit l'unicité
    )
    
    # Extraction des noms uniques
    unique_names = list({q['name'] for q in quotations})
    
    return {
        "success": True,
        "message": f"Found {len(unique_names)} quotations for RFQ {rfq_name}" + 
                  (f" (filtered by supplier: {supplier})" if supplier else ""),
        "data": {
            "unique_names": unique_names,
        }
    }