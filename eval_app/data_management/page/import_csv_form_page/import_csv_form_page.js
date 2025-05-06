frappe.pages['import-csv-form-page'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Page D\'importation de donnee',
		single_column: true
	});
}

