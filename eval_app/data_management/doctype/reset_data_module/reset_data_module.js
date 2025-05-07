// Copyright (c) 2025, JACQUES Chan Alex and contributors
// For license information, please see license.txt

frappe.ui.form.on("Reset Data Module", {
	refresh(frm) {

	},
    module_def: function(frm) {
        if (frm.doc.module_def) {
            frappe.db.get_doc('Module Def', frm.doc.module_def)
                .then(doc => {
                    // Set the label field with the name of the Module Def
                    frm.set_value('label', doc.name);
                })
                .catch(err => {
                    frappe.msgprint({
                        title: __('Erreur'),
                        message: __('Impossible de charger le module défini.'),
                        indicator: 'red'
                    });
                    console.error(err);
                });
        }
    }
});
