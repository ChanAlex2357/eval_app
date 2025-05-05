// Copyright (c) 2025, JACQUES Chan Alex and contributors
// For license information, please see license.txt

frappe.ui.form.on("Import Csv", {
	setup(frm) {
		
		frm.get_field("file").df.options = {
			restrictions: {
				allowed_file_types: [".csv", ".xls", ".xlsx"],
			},
		};
	},

	refresh(frm) {
		frm.disable_save();
		frm.page.hide_icon_group();
		frm.get_field("import_preview").$wrapper.empty()
		frm.get_field("logs_preview").$wrapper.empty()
        if( !frm.is_new() ){
            frm.trigger("show_preview");
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
				},
			},
		}).then((r) => {
			let preview_data = r.message;
			console.log(preview_data);
			frm.events.show_import_preview(frm, preview_data);
			frm.events.show_logs(frm, preview_data);
			frm.events.show_import_warnings(frm, preview_data);
		});
    },
	show_import_preview(frm, preview_data) {
		const { columns, data } = preview_data;
		let idx = 1;
		const $table = $(`<table class="table table-bordered table-sm mt-3">
			<thead>
			<tr>
				<th>#</th>
				${columns.map(col => `<th>${col}</th>`).join("")}
			</tr></thead>
			<tbody>
				${data.map(row => `<tr> <td scope="row" > ${idx+=1}</td> ${row.map(val => `<td>${val}</td>`).join("")}</tr>`).join("")}
			</tbody>
		</table>`);
		frm.get_field("import_preview").$wrapper.empty().append($table);
	},
	show_logs(frm, preview_data) {
		const logs = preview_data.import_logs;
		if (!logs || logs.length === 0) {
			frm.get_field("import_logs").$wrapper.html("<p class='text-muted'>Aucun log d'importation disponible.</p>");
			return;
		}
	
		let $table = $(`<table class="table table-bordered table-sm mt-3">
			<thead>
				<tr>
					<th>#</th>
					<th>Messages</th>
				</tr>
			</thead>
			<tbody></tbody>
		</table>`);
	
		logs.forEach(log => {
			const hasException = log.exception && log.exception !== "null" && log.exception !== null;
			const row = $(`
				<tr>
					<td>
						${log.row_num}
						${hasException ?`<span class="badge badge-danger p-1"> </span>`:`<span class="badge badge-success p-1"> </span>`}
					</td>
					<td>
						<div>${log.message}</div>
						${hasException ? `
							<button class="btn btn-link p-0 mt-1 toggle-exception text-danger" style="font-size: 0.9em;">Afficher l'erreur</button>
							<pre class="exception-detail d-none bg-light border p-2 mt-1" style="white-space: pre-wrap;">${log.exception}</pre>
						` : ""}
					</td>
				</tr>
			`);
			$table.find("tbody").append(row);
		});
	
		frm.get_field("logs_preview").$wrapper.empty().append($table);
	
		// Toggle exceptions
		frm.get_field("logs_preview").$wrapper.find(".toggle-exception").on("click", function () {
			const $btn = $(this);
			const $pre = $btn.next(".exception-detail");
			const visible = !$pre.hasClass("d-none");
	
			$pre.toggleClass("d-none", visible);
			$btn.text(visible ? "Afficher l'erreur" : "Masquer l'erreur");
		});
	},
	

	import_file(frm) {
		frappe.msgprint("Important")
	},
	show_import_warnings(frm,preview_data){

	},
	
});
