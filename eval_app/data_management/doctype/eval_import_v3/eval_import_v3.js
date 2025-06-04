// Copyright (c) 2025, JACQUES Chan Alex and contributors
// For license information, please see license.txt

frappe.ui.form.on("Eval Import V3", {
	refresh(frm) {

	},

    start_import_btn(frm){
        // if (!frm.is_new()) {
        frm.trigger("start_import");
        // frm.msgprint( __("This import is not available in this version. Please use the latest version of Eval App.") );
    },

    start_import(frm) {
		frm.call({
			method: "form_start_import",
			args: { import_name: frm.doc.name },
			freeze: true,
			freeze_message: __("Importing..."),
		}).then((r) => {
			frm.events.show_global_import_summary(frm,r.message)
		});
	},
	show_global_import_summary(frm, summary_data) {
		const container = frm.get_field("files_logs_html").$wrapper;
		container.empty();
	
		if (!summary_data || Object.keys(summary_data).length === 0) {
			container.html("<p class='text-muted'>Aucun résultat d'importation disponible.</p>");
			return;
		}
	
		let html = `
			<table class="table table-bordered mt-3">
				<thead>
					<tr>
						<th>Fichier</th>
						<th>Etat global</th>
						<th>Lignes réussies</th>
						<th>Erreurs</th>
						<th>Détails</th>
					</tr>
				</thead>
				<tbody>
		`;
	
		Object.keys(summary_data).sort().forEach(file_key => {
			const file_info = summary_data[file_key];
			const status_badge = file_info.status === 1
				? `<span class="badge badge-success">Succès</span>`
				: `<span class="badge badge-danger">Erreur</span>`;
	
			const success_count = file_info.success_count || 0;
			const error_count = file_info.error_count || 0;
			const detail_link = file_info.import_link
				? `<a href="${file_info.import_link}" target="_blank">Voir l'import</a>`
				: "-";
	
			html += `
				<tr>
					<td><strong>${file_key}</strong></td>
					<td>${status_badge}</td>
					<td>${success_count}</td>
					<td>${error_count}</td>
					<td>${detail_link}</td>
				</tr>
			`;
		});
	
		html += `</tbody></table>`;
	
		container.html(html);
	},
	

});
