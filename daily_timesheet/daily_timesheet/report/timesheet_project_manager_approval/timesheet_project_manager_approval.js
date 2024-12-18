frappe.query_reports["Timesheet Project Manager Approval"] = {
	"filters": [
		{
            'fieldname':'employee' ,
			'fieldtype': 'Link',
			'label':__('Employee'),
			'options':'Employee'
		},
		{
			'fieldname':'project_manager',
			'fieldtype': 'Link',
			'label':__('Project Manager'),
			'options':'User',
			'default':frappe.session.user,
			'read_only':1
		}
		,{
			'fieldname':'parent_project' ,
			'fieldtype': 'Link',
			'label':__('Project'),
			'options':'Project',
			'get_query':function(){
				frappe.call({
					method :'daily_timesheet.daily_timesheet.report.timesheet_project_manager_approval.timesheet_project_manager_approval.get_project_for_manager',
					args :
					{
						user:frappe.session.user
					},
					callback : function(r)
					{
                         if(r.message){
							frappe.msgprint(r.message)
							console.log(r.message)
						 }

					}
					
				})


				return{
					filters : {

					}
				}
			}
		},
		{
			'fieldname':'start_date' ,
			'fieldtype': 'Date',
			'label':__('From Date'),
		},
		{
			'fieldname':'end_date' ,
			'fieldtype': 'Date',
			'label':__('To Date'),
		},
],

get_datatable_options(options) {
	return Object.assign(options, {
		checkboxColumn: true,
	});
},
onload: function(report) {
	report.page.add_action_item(__("Approve"), function() {
		let checked_rows_indexes = report.datatable.rowmanager.getCheckedRows();
		let checked_rows = checked_rows_indexes.map(i => report.data[i]);
		// console.log(checked_rows)
		if (checked_rows.length === 0) {
		frappe.throw(__('Please select at least one timesheet.'));
	    }
		const timesheet_ids = checked_rows.map(row => {
			return {
				employee: row.employee,
				name: row.name
			};
		});
		console.log(timesheet_ids)
		frappe.call({
			            method: "daily_timesheet.daily_timesheet.report.timesheet_approval_report.timesheet_approval_report.approve_timesheets",
			            args: {
			                timesheet_ids: timesheet_ids,
			                approver: 'reports_to'
			            },
			            callback: function (r) {
			                if (r.message === "success") {
			                    frappe.msgprint(__('Timesheets approved successfully.'));
			                    report.refresh(); // Refresh the report to update data
			                } else {
			                    frappe.msgprint(r.message || __('Approval failed.'));
			                }
			            }
			        });
	});

	report.page.add_action_item(__('Reject'),function(){

		let checked_rows_indexes = report.datatable.rowmanager.getCheckedRows();
		let checked_rows = checked_rows_indexes.map(i => report.data[i]);
		if (checked_rows.length === 0) {
			frappe.throw(__('Please select at least one timesheet.'));
			}
			const timesheet_ids = checked_rows.map(row => {
				return {
					employee: row.employee,
					name: row.name
				};
			});
			console.log(timesheet_ids)
			frappe.call({
							method: "daily_timesheet.daily_timesheet.report.timesheet_approval_report.timesheet_approval_report.reject_timesheets",
							args: {
								timesheet_ids: timesheet_ids,
								approver: 'reports_to'
							},
							callback: function (r) {
								if (r.message === "success") {
									frappe.msgprint(__('Timesheets rejected successfully.'));
									report.refresh(); 
								} else {
									frappe.msgprint(r.message || __('Rejection failed.'));
								}
							}
						});
	})
},
};

