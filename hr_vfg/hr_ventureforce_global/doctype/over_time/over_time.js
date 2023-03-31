// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Over Time', {
	// refresh: function(frm) {

	// }
	date:function(frm){
        get_overtime(frm)
	},
	data_8:function(frm){
		get_overtime(frm)
	},
	month:function(frm){
		get_overtime(frm)
	}
});

function get_overtime(frm){
	console.log("ook")
	if(frm.doc.month && frm.doc.data_8){
		frappe.call({
			method:"get_overtime",
			doc:frm.doc,
			args:{
				employee:frm.doc.data_8,
				month:frm.doc.month
			},
			callback:function(r){
				console.log(r)
				frappe.model.clear_table(frm.doc, "table_4");
				$.each(r.message, function(index, row) {
					
						var d = frm.add_child("table_4")
						d.date = row.date
						d.actual_over_time = row.actual_over_time
						d.checkin = row.checkin
						d.checkout = row.checkout
						
					
				});
				frm.refresh_field("table_4")
				
			}
		})
	}
}