// Copyright (c) 2025, JACQUES Chan Alex and contributors
// For license information, please see license.txt

frappe.ui.form.on("Import Csv", {
	setup(frm) {
        if( !frm.is_new() ){
            frm.trigger("show_preview");
        }
		frm.get_field("file").df.options = {
			restrictions: {
				allowed_file_types: [".csv", ".xls", ".xlsx"],
			},
		};
	},

	refresh(frm) {
		frm.page.hide_icon_group();
    },

    start_import(frm) {
        frappe.msgprint("Start Import");
		frm.call({
			method: "form_start_import",
			args: { import_name: frm.doc.name },
			btn: frm.page.btn_primary,
		}).then((r) => {
			if (r.message === true) {
                frappe.msgprint("Import TRUE");
			}
            else{
                frappe.msgprint("Import FALSE");
            }
		});
	},

    start_import_btn(frm){
        if (!frm.is_new()) {
            frm.trigger("start_import");
        }
    },

    show_preview(frm){
        frm.get_field("import_preview").$wrapper.empty();
        $('<span class="text-muted">')
			.html(__("Loading import file..."))
			.appendTo(frm.get_field("import_preview").$wrapper);

		frm.call({
			method: "get_html_preview",
			args: {
				import_name: frm.doc.name,
				import_file: frm.doc.file,
			},
			error_handlers: {
				TimestampMismatchError() {
					// ignore this error
				},
			},
		}).then((r) => {
			let preview_data = r.message;
			frm.events.show_import_preview(frm, preview_data);
			frm.events.show_import_warnings(frm, preview_data);
		});
    },
	show_import_preview(frm, preview_data) {
	
	},
	show_import_warnings(frm,preview_data){
		
	}
});
