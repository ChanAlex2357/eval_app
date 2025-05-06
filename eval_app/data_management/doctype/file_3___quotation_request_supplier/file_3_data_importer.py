from erpnext.stock.doctype.material_request.material_reques import make_request_for_quotation
from eval_app.data_management.doctype.import_csv.data_importer import DataImporter
import frappe

class File3DataImporter(DataImporter):

    def make_stack_import(self, rows, dt):
        import_log = []
        errors_count = 0
        success_count = 0

        # Étape 1 : Grouper les lignes par ref_request_quotation
        from collections import defaultdict
        grouped_rows = defaultdict(list)
        for row in rows:
            grouped_rows[row.ref_request_quotation].append(row)

        # Étape 2 : Traiter chaque groupe
        for ref, group in grouped_rows.items():
        
            # Dans ta boucle de ref :
            try:
                mr = frappe.get_doc("Material Request", {"ref": ref})
                if not mr :
                    raise Exception(f"Aucun Materiel Request avec ref {ref}")
                
                if mr.docstatus != 0:
                    raise Exception(f"Material Request {ref} n'est pas en draft")

                # Utilise la fonction existante pour générer le RFQ
                rfq = make_request_for_quotation(source_name=mr.name)

                # Ajoute les suppliers
                for row in group:
                    supplier_name = row.supplier.strip()
                    if not frappe.db.exists("Supplier", supplier_name):
                        raise Exception(f"Supplier '{supplier_name}' introuvable")

                    rfq.append()
                    frappe.get_doc({
                        "doctype": "Request For Quotation Supplier",
                        "supplier": supplier_name
                    })

                rfq.insert(ignore_permissions=True)
                rfq.submit()

            except Exception as e:
                ...


                # Pour chaque supplier dans les lignes du groupe
                for row in group:
                    supplier_name = row.supplier.strip()
                    if not frappe.db.exists("Supplier", supplier_name):
                        raise Exception(f"Supplier '{supplier_name}' introuvable")

                    # Créer une instance de Request for Quotation Supplier
                    frappe.get_doc({
                        "doctype": "Request For Quotation Supplier",
                        "supplier": supplier_name,
                        "request_for_quotation": rfq.name
                    }).insert(ignore_permissions=True)

                # Soumettre le RFQ
                rfq.submit()
                import_log.append(f"RFQ créé et soumis pour ref {ref}")
                success_count += 1

            except Exception as e:
                import_log.append(f"Erreur pour ref {ref} : {str(e)}")
                errors_count += 1

        return import_log, errors_count, success_count
