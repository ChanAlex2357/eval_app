from frappe import _
import frappe
from frappe.utils import getdate
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

@frappe.whitelist(allow_guest=False)
def get_salary_stats_by_month(year):
    year = int(year)
    # Requête SQL pour agréger les données
    salary_slips = frappe.db.sql("""
        SELECT
            DATE_FORMAT(start_date, '%%Y-%%m') AS month,
            SUM(gross_pay) AS total_gross,
            SUM(net_pay) AS total_net
        FROM `tabSalary Slip`
        WHERE docstatus = 1 AND YEAR(start_date) = %s
        GROUP BY DATE_FORMAT(start_date, '%%Y-%%m')
        ORDER BY month
    """, year, as_dict=True)

    # Récupérer les détails des composants
    result = []
    for slip in salary_slips:
        month = slip.month
        components = frappe.db.sql("""
            SELECT
                e.salary_component,
                SUM(e.amount) AS total_amount
            FROM `tabSalary Slip` ss
            JOIN `tabSalary Detail` e ON e.parent = ss.name
            WHERE ss.docstatus = 1
                AND DATE_FORMAT(ss.start_date, '%%Y-%%m') = %s
                AND e.parentfield IN ('earnings', 'deductions')
            GROUP BY e.salary_component
        """, month, as_dict=True)
        
        result.append({
            "month": month,
            "Total brut": slip.total_gross,
            "Total net": slip.total_net,
            "components": {c.salary_component: c.total_amount for c in components}
        })
    
    return result

@frappe.whitelist(allow_guest=False)
def get_employee_salary_breakdown(month_year):
    # Valider le format de month_year (YYYY-MM)
    if not re.match(r'^\d{4}-\d{2}$', month_year) :
        frappe.throw("Le paramètre month_year doit être au format YYYY-MM (par exemple, 2025-01)")

    # Requête SQL
    result = frappe.db.sql("""
        SELECT
            ss.employee,
            sc.type AS component_type,
            e.salary_component,
            SUM(e.amount) AS total_amount
        FROM `tabSalary Slip` ss
        JOIN `tabSalary Detail` e ON e.parent = ss.name
        JOIN `tabSalary Component` sc ON e.salary_component = sc.name
        WHERE ss.docstatus = 1
            AND DATE_FORMAT(ss.start_date, '%%Y-%%m') = %(month_year)s
        GROUP BY ss.employee, e.salary_component
        ORDER BY ss.employee, e.salary_component
    """, {"month_year": month_year}, as_dict=True)

    # Structurer les résultats
    breakdown = {}
    for row in result:
        employee = row.employee
        if employee not in breakdown:
            breakdown[employee] = {
                "employee": employee,
                "components": {},
                "total_earnings": 0.0,
                "total_deductions": 0.0
            }
        breakdown[employee]["components"][row.salary_component] = {
            "component_type": row.component_type,
            "total_amount": float(row.total_amount)  # Convertir en float pour JSON
        }
        # Ajouter le montant au total correspondant (earnings ou deductions)
        if row.component_type == "Earning":
            breakdown[employee]["total_earnings"] += float(row.total_amount)
        elif row.component_type == "Deduction":
            breakdown[employee]["total_deductions"] += float(row.total_amount)

    # Convertir en liste pour une sortie JSON claire
    return list(breakdown.values())

@frappe.whitelist(allow_guest=False)
def get_salary_component_breakdown_by_year(year):
    # Valider l'année
    try:
        year = int(year)
        if not (1900 <= year <= 9999):
            frappe.throw("L'année doit être une valeur valide entre 1900 et 9999")
    except ValueError:
        frappe.throw("L'année doit être un nombre entier")

    # Requête SQL
    result = frappe.db.sql("""
        SELECT
            DATE_FORMAT(ss.start_date, '%%Y-%%m') AS month,
            sc.name AS salary_component,
            COALESCE(SUM(sd.amount), 0) AS total_amount
        FROM `tabSalary Component` sc
        LEFT JOIN `tabSalary Detail` sd
            ON sd.salary_component = sc.name
            AND sd.parentfield IN ('earnings', 'deductions')
        LEFT JOIN `tabSalary Slip` ss
            ON ss.name = sd.parent
            AND ss.docstatus = 1
            AND YEAR(ss.start_date) = %(year)s
        WHERE YEAR(ss.start_date) = %(year)s OR ss.start_date IS NULL
        GROUP BY DATE_FORMAT(ss.start_date, '%%Y-%%m'), sc.name
        ORDER BY DATE_FORMAT(ss.start_date, '%%Y-%%m'), sc.name
    """, {"year": year}, as_dict=True)

    # Structurer les résultats
    breakdown = {}
    for row in result:
        salary_component = row.salary_component
        month = row.month
        if salary_component not in breakdown:
            breakdown[salary_component] = {}
        if month:  # Ignorer les mois NULL
            breakdown[salary_component][month] = float(row.total_amount)  # Convertir en float pour JSON

    salary_slips = frappe.db.sql("""
        SELECT
            DATE_FORMAT(start_date, '%%Y-%%m') AS month,
            SUM(gross_pay) AS total_gross,
            SUM(net_pay) AS total_net
        FROM `tabSalary Slip`
        WHERE docstatus = 1 AND YEAR(start_date) = %s
        GROUP BY DATE_FORMAT(start_date, '%%Y-%%m')
        ORDER BY month
    """, year, as_dict=True)

    for slip in salary_slips:
        month = slip.month
        if "Total brut" not in breakdown and "Total net" not in breakdown:
            breakdown["Total brut"] = {}
            breakdown["Total net"] = {}

        if month :
            breakdown["Total brut"][month] = slip.total_gross
            breakdown["Total net"][month] = slip.total_net

    return breakdown

@frappe.whitelist(allow_guest=False)
def get_salary_slip_by_component(salary_component,operation,amount):
    try:
        result = frappe.db.sql("""
            SELECT
                ss.start_date AS start_date,
                ss.employee AS employee
            FROM `tabSalary Slip` ss
            LEFT JOIN `tabSalary Detail` sd
                ON ss.name = sd.parent
            LEFT JOIN `tabSalary Structure Assignment` sa
                ON sa.salary_structure = ss.salary_structure
                AND sa.from_date = ss.start_date
            WHERE ss.docstatus = 1
                AND sd.salary_component = %s
                AND sd.amount {} %s
        """.format(operation), (salary_component, amount), as_dict=True)
        return result
    except Exception as e:
        frappe.log_error(f"Erreur dans get_salary_slip_by_component: {str(e)}", "Salary Slip Query")
        frappe.throw(_("Erreur lors de la récupération des Salary Slips : {0}").format(str(e)))
    return result

@frappe.whitelist(allow_guest=True)
def update_salary_condition(salary_component, operation, amount, percent):
    try:
        dateEmployees = get_salary_slip_by_component(salary_component, operation, amount)
        for dateEmployee in dateEmployees:
            startDate = dateEmployee.start_date
            employee = dateEmployee.employee
            

            salaryAssignementName = frappe.db.exists("Salary Structure Assignment", {"from_date": startDate, "employee": employee, "docstatus": "1"})
            salarySlipName = frappe.db.exists("Salary Slip", {"start_date": startDate, "employee": employee, "docstatus": "1"})
            if salaryAssignementName and salarySlipName:
                salaryAssignement = frappe.get_doc("Salary Structure Assignment", salaryAssignementName)
                salarySlip = frappe.get_doc("Salary Slip", salarySlipName)
                
                salaryAssignement.docstatus = 2
                salarySlip.docstatus = 2
                original_base = salaryAssignement.base
                if not isinstance(original_base, (int, float)):
                    frappe.throw(_("La base salariale doit être un nombre, reçu : {0}").format(type(original_base)))
                salarySlip_data = salarySlip.as_dict()
                salaryAssignement_data = salaryAssignement.as_dict()
                
                salarySlip.save(ignore_permissions=True)
                salaryAssignement.save(ignore_permissions=True)
                salarySlip.delete(ignore_permissions=True)
                salaryAssignement.delete(ignore_permissions=True)
                
                salaryAssignement = frappe.get_doc(salaryAssignement_data)
                salarySlip = frappe.get_doc(salarySlip_data)
                base = original_base + (original_base * percent / 100)
                salaryAssignement.base = base
                if salaryAssignement.base < 0:
                    salaryAssignement.base = abs(original_base)
                salaryAssignement.docstatus = 1
                salarySlip.docstatus = 1
                salaryAssignement.insert(ignore_permissions=True)
                salarySlip.insert(ignore_permissions=True)
                frappe.db.commit()

        return {"status": "success", "message": "Salary Slip et Assignment mis à jour avec succès"}
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Erreur dans update_salary_condition: {str(e)}", "Salary Slip Query")
        frappe.throw(_("Erreur lors de la mise à jour : {0}").format(str(e)))

@frappe.whitelist(allow_guest=True)
def get_salary_assignement_by_date(date,employee):
# Requête SQL corrigée
    try:
        result = frappe.db.sql("""
            SELECT 
                base,from_date
            FROM `tabSalary Structure Assignment`
            WHERE from_date <= %s 
            AND employee = %s
            ORDER BY from_date DESC;
        
        """,(date ,employee), as_dict=True)
        return result
    except Exception as e:
        frappe.log_error(f"Erreur dans get_salary_slip_by_component: {str(e)}", "Salary Slip Query")
        frappe.throw(_("Erreur lors de la récupération des Salary Slips : {0}").format(str(e)))
    return result

@frappe.whitelist(allow_guest=True)
def insert_salary(employee, month1, month2, amount):
    try:
        # Valider les paramètres
        if not employee or not frappe.db.exists("Employee", employee):
            frappe.throw(_("Employé invalide : {0}").format(employee))
        if not month1 or not month2:
            frappe.throw(_("Dates de début et de fin requises"))

        # Parser les dates
        start_date = datetime.strptime(month1, "%Y-%m")
        final_date = datetime.strptime(month2, "%Y-%m").replace(day=1)

        # Récupérer amount si non fourni
        if amount is None:
            assignments = get_salary_assignement_by_date(start_date.strftime("%Y-%m-%d"), employee)
            if not assignments:
                frappe.throw(_("Aucune base salariale trouvée pour {0}").format(employee))
            amount = assignments[0].base

        current_date = start_date
        while current_date <= final_date:
            start_date_str = current_date.strftime("%Y-%m-%d")
            end_date = current_date.replace(day=1) + relativedelta(months=1, days=-1)
            end_date_str = end_date.strftime("%Y-%m-%d")
            employee_data = frappe.get_doc(
                "Employee",employee
            )

            # Insérer Salary Structure Assignment
            assignment = frappe.get_doc({
                "doctype": "Salary Structure Assignment",
                "employee": employee,
                "salary_structure": "g1",
                "company": employee_data.company,
                "from_date": start_date_str,
                "base": float(amount),
                "docstatus": 1
            })
            existing_assignment = frappe.db.exists("Salary Structure Assignment", {"from_date": start_date_str, "employee": employee})
            if not existing_assignment:
                assignment.insert(ignore_permissions=True)

            # Insérer Salary Slip
            slip = frappe.get_doc({
                "doctype": "Salary Slip",
                "employee": employee,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "payroll_frequency": "Monthly",
                "company": employee_data.company,
                "salary_structure": "g1",
                "docstatus": 1
            })
            existing_slip = frappe.db.exists("Salary Slip", {"start_date": start_date_str, "employee": employee})
            if not existing_slip:
                slip.insert(ignore_permissions=True)

            frappe.db.commit()
            current_date += relativedelta(months=1)

        return {"status": "success", "message": "Salary Slip et Assignment insérés avec succès"}
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Erreur dans insert_salary: {str(e)}", "Salary Insert Query")
        frappe.throw(_("Erreur lors de l'insertion : {0}").format(str(e)))