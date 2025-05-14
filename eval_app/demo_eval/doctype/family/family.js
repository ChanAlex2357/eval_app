// Copyright (c) 2025, JACQUES Chan Alex and contributors
// For license information, please see license.txt

frappe.ui.form.on("Family", {
	refresh(frm) {
        frappe.msgprint("Hello")
	},
    family_name(frm) {

    },
    button(frm){
        frappe.msgprint("Button clicked")
    }
});
