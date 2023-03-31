frappe.listview_settings['Employee Attendance'] = {
	colwidths: {"subject": 6},
	onload: function(listview) {
		var method = "erpnext.hr.doctype.attendance.auto_attendance.get_attendance";

		var methods = "erpnext.hr.doctype.attendance.att_week.get_attendance_long";
        var nm = "erpnext.hr.doctype.attendance.att_week.settle_night_s";
		// listview.page.add_menu_item(__("Generate Attendance"), function() {
		// 	listview.call_for_selected_items(method, {"status": "Open"});
		// });


				listview.page.add_menu_item(__("Get Attendance"), function() {
					var dialog = new frappe.ui.Dialog({
						title: __('Add Follow Up'),
						fields: [
				
							{ fieldtype: 'Date', reqd:1, fieldname: 'from_date', label: __("From Date") },
							{ fieldtype: 'Column Break' },
							{ fieldtype: 'Date',reqd:1, fieldname: 'to_date', label: __("To Date") },
							{ fieldtype: 'Section Break' },
				
							{ fieldtype: 'Link', fieldname: 'employee', label: __("Employee"),options:"Employee" },
							{ fieldtype: 'Link', fieldname: 'department', label: __("Department"),options:"Department" },
				
				
						],
						primary_action: function () {
							var args = dialog.get_values();
							console.log(args)
							listview.call_for_selected_items(methods, args);
							dialog.hide()
						},
						primary_action_label: __("Submit")
					})
					dialog.show()
			
		});

		// listview.page.add_menu_item(__("Settle Night Shift"), function() {
		// 	listview.call_for_selected_items(nm, {"status": "Open"});
		// });
}
}