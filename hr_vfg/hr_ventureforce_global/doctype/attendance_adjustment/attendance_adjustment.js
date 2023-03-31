// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Adjustment', {
	// refresh: function(frm) {

	// },
	after_workflow_action: (frm) => {
		console.log(frm.doc)
		if(frm.doc.workflow_state == "Approved"){
			console.log("calling")
			frm.call({
				method:"create_logs",
				doc:frm.doc,
				args:{},
				callback:function(r){}

			})
		}
	}
});

frappe.ui.form.on('Attendance Adjustment CT', {
	employee_id: function(frm, cdt, cdn) {
	    debugger;
		let row = locals[cdt][cdn]
		
		frappe.call({
			method: "erpnext.hr.doctype.attendance_adjustment.attendance_adjustment.get_check_in_out",
			args: {
				date: frm.doc.date,
				month: frm.doc.month,
				employee_id: row.employee_id
			},
			async: false,
			callback: function(r) {
				if(r.message) {
					frappe.model.set_value(cdt, cdn, 'check_in_1',r.message[0]);
					frappe.model.set_value(cdt, cdn, 'check_out_1',r.message[1]);
				}
			}
		});
	}
})
