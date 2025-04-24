// Copyright (c) 2025, JACQUES Chan Alex and contributors
// For license information, please see license.txt

frappe.ui.form.on("Reset Data", {
	refresh(frm) {
        frm.set_intro("Ce Doctype va reinitialiser l'entierete des donnees de l'application");
        frm.set_value("logs","");
	},

    reset_button: function(frm){
        frappe.confirm('Es-tu sûr de vouloir réinitialiser toutes les données ?',
            // Confirm reset
            function() {
                frappe.call(
                {
                    method: 'eval_app.data_management.doctype.reset_data.reset_data.reset_data',
                    args : {
                        module: frm.doc.module,
                    },
                    freeze: true,
                    freeze_message: "Réinitialisation en cours...",
                })
                .then((r) => {
                    console.log(r);
                    if (r.message && Array.isArray(r.message)) {
                        
                        if (r.message.length > 0) {
                            r.message.forEach(msg => {
                                frappe.msgprint({
                                    message:msg,
                                    title: __('Réinitialisation Logs'),
                                    indicator: 'red'
                                }
                            );
                            });
                        }
                        else {
                            frappe.msgprint({
                                message:'Reinitialisation terminé et avec succès',
                                title: __('Réinitialisation Logs'),
                                indicator: 'green'
                            });
                        }
                    }
                }
                )
                .catch((e) => {
                    frappe.msgprint({
                        message: 'Réinitialisation échouée avec des erreurs.',
                        title: 'Erreur',
                        indicator: 'red'
                    });
                });
            },
            // Cancel reset
            function() {
                frappe.msgprint('Opération annulée');
                frm.set_value("logs","Donnee reinitialiser canceled");
            }
        );
    },


    before_save: function(frm) {
        frm.set_value("logs","");
    }
});
