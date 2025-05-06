// Copyright (c) 2025, JACQUES Chan Alex and contributors
// For license information, please see license.txt

frappe.ui.form.on("Eval Import", {
	refresh(frm) {

	},

    start_import_btn(frm){
        if (!frm.is_new()) {
            frm.trigger("start_import");
        }
    },

    start_import(frm) {
		frm.call({
			method: "form_start_import",
			args: { import_name: frm.doc.name },
			freeze: true,
			freeze_message: __("Importing..."),
		}).then((r) => {
			if (r.message === true) {
                frm.refresh();
			}
            else{
                frm.refresh()
            }
		});
	},

});
