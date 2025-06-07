import frappe
from frappe import _
import traceback
from eval_app.data_management.doctype.import_csv.csv_importer_service import make_row_import
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from eval_app.data_management.doctype.file_1___material_request_import.file_1___material_request_import import File1DataImporter
from erpnext.buying.doctype.request_for_quotation.request_for_quotation import make_supplier_quotation_from_rfq
from eval_app.data_management.doctype.eval_import_v3.eval_import_v3 import EvalImportV3
from frappe.utils.file_manager import save_file
from eval_app.data_management.doctype.reset_data.reset_data import reset_data
from collections import defaultdict
from hrms.payroll.doctype.payroll_entry.payroll_entry import get_end_date

from frappe.utils import getdate

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
            "email": user.email,
            "roles":user.roles
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
            po["status"] +=" and Unpaid"
            # Query related Purchase Invoices through the 'items' child table
            invoices = frappe.db.get_all(
                "Purchase Invoice",
                filters=[["Purchase Invoice Item", "purchase_order", "=", po.name]],
                fields=["name", "status", "outstanding_amount", "rounded_total"]
            )

            total_paid = 0.0
            inv_len = len(invoices)
            order_status = po["status"]
            reste_a_payer = 0

            for inv in invoices:
                paid = (inv["rounded_total"] or 0) - (inv["outstanding_amount"] or 0)
                total_paid += paid
                reste_a_payer += inv["outstanding_amount"] or 0

            amount_to_paid = po.grand_total or 0.0

            # Determine custom payment status
            if inv_len > 0 and amount_to_paid == total_paid:
                    po["status"] +=" and Paid"

            po["invoices"] = {
                "data":invoices,
                "total_paid": total_paid,
                "to_paid":amount_to_paid
            }


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
def remote_reset_data():
    try:
        logs = reset_data()
        if logs.__len__() > 0 :
            return make_response(False,"Reset failed logs",{"logs":logs})
        return make_response(True,"Reset done successfully",{"logs":logs})
            
    except Exception as e:
        frappe.log_error(f"Erreur pendant remote reset:\n{traceback.format_exc()}")
        return make_response(False,f"Failed to reset data : {str(e)}",None,traceback(e))

@frappe.whitelist(allow_guest=False)
def remote_import():

    files = frappe.request.files
    emp_file = files.get("emp_file")
    structure_file = files.get("structure_file")
    salary_file = files.get("salary_file")

    try:

        # 🧱 Vérification initiale
        if not emp_file or not structure_file or not salary_file:
            return make_response(False, "Tous les fichiers requis n'ont pas été fournis.", errors=files)

        eval_v3 : EvalImportV3 = frappe.new_doc("Eval Import V3")
        eval_v3.insert()


        # 🗂️ Upload des fichiers dans public.files
        emp_uploaded = save_file(emp_file.filename, emp_file.stream.read(), eval_v3.doctype, eval_v3.name, is_private=False)

        struct_uploaded = save_file(structure_file.filename, structure_file.stream.read(), eval_v3.doctype, eval_v3.name, is_private=False)
        
        salary_uploaded = save_file(salary_file.filename, salary_file.stream.read(), eval_v3.doctype, eval_v3.name, is_private=False)

        # 🧩 Mise en place des chemins pour traitement
        eval_v3.setup_files(
            emp_file=emp_uploaded.get("file_url"),
            structure_file=struct_uploaded.get("file_url"),
            salary_file=salary_uploaded.get("file_url")
        )


        # ✅ Vérification des fichiers (logique métier)
        check, message = eval_v3.check_files()
        if not check:
            return make_response(False, message, errors=files)

        # 🚀 Début import
        eval_v3.save()
        result = eval_v3.start_files_import()
        
        
        return make_response(True, "Import lancé avec succès depuis l'API.", data=result)

    except Exception as e:
        frappe.log_error(f"Erreur pendant l'import API remote :\n{traceback.format_exc()}")
        return make_response(False, f"Erreur : {str(e)}")
    
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
    try :
        if len(unique_names) == 0 :
            sq = make_supplier_quotation_from_rfq(
                source_name=rfq_name,
                for_supplier=supplier
            )
            sq.insert()
            frappe.db.commit()
            unique_names.append(sq.name)
    except Exception as e :
        frappe.db.rollback()
        frappe.log_error(e)
    
        
    
    return {
        "success": True,
        "message": f"Found {len(unique_names)} quotations for RFQ {rfq_name}" + 
                  (f" (filtered by supplier: {supplier})" if supplier else ""),
        "data": {
            "unique_names": unique_names,
        }
    }

@frappe.whitelist()
def get_salary_annual(year = 2025):
    months_str = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    months = []

    month_idx = set()
    component_idx = set()

    try:
        for i in range(12):
            month = f"{i+1}"

            if i < 9:
                month = f"0{month}"
            month_name = f"{months_str[i]} {year}"

            start_date = f"{year}-{month}-01"
            end_date = get_end_date(start_date,"monthly").get("end_date")
            month_data = filter_salary_slip(start_date=start_date, end_date=end_date, component_idx=component_idx)

            component_idx = month_data.get("component_idx")
            month_idx.add(month_name)
            months.append({
                "month_num":month,
                "period":month_name,
                "start_date":start_date,
                "end_date":end_date,    # Info Mois
                "total_earnings":month_data.get("sum_earnings"),        # total gains
                "total_deductions":month_data.get("sum_deductions"),    # total deductions
                "total_salary":month_data.get("sum_salary"),            # total Salaire du mois
                "components":month_data.get("components"),
                # "salaries":month_data.get("salaries"),                  # Les details du salaire du mois
                # "salaries":[],                  # Les details du salaire du mois
            })

        return make_response(True,f"Data fetched for {year}",{
            "year":year,
            "component_idx":component_idx,
            "month_idx":month_idx,
            "months":months
        })

    except Exception as e:
        frappe.log_error(
            title="Error fetching salary slips",
            message=traceback.format_exc()
        )
        return make_response(False,"error while getting annual summary data",[],traceback(e))

def filter_salary_slip(employee=None, employee_name=None,start_date=None, end_date=None , component_idx = set()):
    """
    Récupère les fiches de paie avec les détails des employés et des structures de salaire.
    Returns:
        dict: {success: bool, message: str, data: list}
    """
    data = []
    filters = {}
    if employee:
        filters["employee"] = employee
    if employee_name:
        filters["employee_name"] = employee_name
    if start_date:
        filters["start_date"] = [">=", start_date]
    if end_date:
        filters["end_date"] = ["<=", end_date]
    salary_slips = frappe.get_all(
        "Salary Slip",
        fields=["name"],
        filters=filters,
    )
    sum_earnings = 0
    sum_deductions = 0
    sum_net_pay = 0
    earnings = defaultdict(float)
    deductions = defaultdict(float)
    components = defaultdict(float)
    
    period = getdate(start_date).strftime('%B %Y')

    for slip in salary_slips:
        slip = frappe.get_doc("Salary Slip",slip.name) #
        slip_dict = slip.as_dict()
        slip_dict.__setitem__("period",period)
        data.append(slip_dict) # liste des salary slip compris dans la periode
        sum_earnings += slip.gross_pay  # calcul somme earnings
        sum_deductions += slip.total_deduction # calcul somme deductions
        sum_net_pay += slip.net_pay # calcul somme salaire net

        for earn in slip.earnings :
            component_name = earn.salary_component

            curr_val = earnings.pop(component_name, 0)
            curr_val += earn.amount
            earnings.__setitem__(component_name, curr_val)
            
            components.__setitem__(component_name, curr_val)
            component_idx.add(component_name)

        for deduct in slip.deductions :
            component_name = deduct.salary_component
            curr_val = deductions.pop(component_name, 0)
            curr_val += deduct.amount
            deductions.__setitem__(component_name, curr_val)
            
            components.__setitem__(component_name, curr_val)
            component_idx.add(component_name)

    return {
            "component_idx":component_idx,
            "sum_earnings":sum_earnings,
            "sum_deductions":sum_deductions,
            "sum_salary":sum_net_pay,
            "salaries":data,
            "components":{
                "earnings":earnings,
                "deductions":deductions,
                "all": components
            }
        }
    
@frappe.whitelist()
def get_salary_slip_with_details(employee=None, employee_name=None,start_date=None, end_date=None):
    """
    Récupère les fiches de paie avec les détails des employés et des structures de salaire.
    Returns:
        dict: {success: bool, message: str, data: list}
    """
    try:
        
        data = filter_salary_slip(employee,employee_name,start_date,end_date)
        return make_response(
            success=True,
            message=_("Fetched salary slips successfully."),
            data=data
        )

    except Exception as e:
        frappe.log_error(
            title="Error fetching salary slips",
            message=traceback.format_exc()
        )
        return make_response(
            success=False,
            message=_("An error occurred while fetching salary slips."),
            errors=[traceback.format_exc()]
        )
