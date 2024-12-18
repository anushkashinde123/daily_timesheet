import frappe
from frappe import _
def execute(filters=None):
	if not filters:
		filters={}
	columns, data = [], []
	
	columns = get_columns()
	cs_data = get_cs_data(filters)

	if not cs_data: 
		frappe.msgprint(_("No records found"))
		return columns, cs_data

	data = []
	for d in cs_data:
		row = frappe._dict({
			'check':0,
			'employee':d.employee,
			'workflow_state':d.workflow_state,
			'name':d.name,
			'employee_name':d.employee_name,
			'start_date':d.start_date,
			'end_date':d.end_date,
			'parent_project':d.parent_project,
			'activity_type':d.activity_type,
			'approve':d.approve,
			'reject':d.reject,
			'project_name': d.project_name
		})
		data.append(row)
	return columns,data,None


def get_columns():
	return [
		
		{	'fieldname':'employee' ,
			'fieldtype': 'Link',
			'label':_('Employee'),
			'options':'Employee',
			'width':'150'
		},
		# {
		# 	'fieldname':'workflow_state' ,
		# 	'fieldtype': 'Link',
		# 	'label':_('Approval Status'),
		# 	'options':'Timesheet',
		# 	'width':'100'
		# },
		{
			'fieldname':'employee_name' ,
			'fieldtype': 'Data',
			'label':_('Employee Name'),
			'width':'150'
		},
        {
			'fieldname':'name' ,
			'fieldtype': 'Data',
			'label':_('Timesheet Name'),
			'width':'150'
		},
		{
			'fieldname':'parent_project' ,
			'fieldtype': 'Link',
			'label':_('Project'),
			'options':'Project',
			'width':'100'
		},
		{
			'fieldname':'start_date',
			'fieldtype': 'Date',
			'label':_('Start Date'),
			'width':'100'
	
		},
		{
			'fieldname':'activity_type',
			'fieldtype': 'Data',
			'label':_('Activity type'),
			'width':'150'
		},
		{
			'fieldname':'approve',
			'fieldtype': 'Data',
			'label':_('Approved'),
			'width':'100'
		},
		{
			'fieldname':'reject',
			'fieldtype': 'Data',
			'label':_('Rejected'),
			'width':'100'
		},
		{		
			'fieldname':'project_name',
			'fieldtype': 'Data',
			'label':_('Project Name'),
			'width':'200'
		},

		
	]

def get_cs_data(filters):
	if not filters.get('reports_to'):
		frappe.msgprint(_("Please select an approver to filter the records."))
	employee_ids = frappe.get_all(
        "Employee",
        filters={"reports_to": filters.get('reports_to')},
        fields=["name"]
    )
	# employee_ids = frappe.get_all(
	# 	'Employee',
	# 	filters = {'user_id': ['in',frappe.get_all(
	# 		'Has Role',
	# 		filters = {'role':'Projects Manager'},
	# 		pluck = 'parent'
	# 	)]},
	# 	fields = ['name','employee_name','user_id']
	# )
	print(employee_ids)
	for em in employee_ids:
		print('==',em)	
	employee_ids = [emp.name for emp in employee_ids]
	if not employee_ids:
		# frappe.msgprint('No employees found')
		return []
	# print(employee_ids,'=====')
	# conditions = [{"employee": ["in", employee_ids]}]
	# if filters.get('employee'):
	# 	conditions.append({'employee':filters.get('employee')})
	# if filters.get('parent_project'):
	# 	conditions.append({'parent_project':filters.get('parent_project')})
	# if filters.get('start_date'):
	# 	conditions.append({'start_date':filters.get('start_date')})
	# if filters.get('end_date'):
	# 	conditions.append({'end_date':filters.get('end_date')})

	conditions = " AND parent.employee IN %(employee_ids)s"
	params = {"employee_ids": employee_ids}
	if filters.get('employee'):
		conditions += " AND parent.employee = %(employee)s"
		params['employee'] = filters.get('employee')
	if filters.get('parent_project'):
		conditions += " AND parent.parent_project = %(parent_project)s"
		params['parent_project'] = filters.get('parent_project')
	if filters.get('start_date'):
		conditions += " AND parent.start_date >= %(start_date)s"
		params['start_date'] = filters.get('start_date')
	if filters.get('end_date'):
		conditions += " AND parent.end_date <= %(end_date)s"
		params['end_date'] = filters.get('end_date')
	
	data = frappe.db.sql(
        f"""
        SELECT parent.employee, parent.name, parent.employee_name, parent.workflow_state,
               parent.parent_project, parent.start_date, parent.end_date, 
			   child.activity_type,child.approve,child.reject,child.project_name
        FROM `tabTimesheet` AS parent
        JOIN `tabTimesheet Detail` AS child ON parent.name = child.parent
        WHERE 1=1 {conditions}
        """,
		params,as_dict=1
		)

	# data = frappe.get_all(
	# 	doctype = 'Timesheet',
	# 	fields = ['employee','name','employee_name','workflow_state','parent_project','start_date','end_date','time_logs'],
	# 	filters = conditions)

	# data = frappe.db.sql("""
	# select parent.employee,parent.name,employee_name,workflow_state,parent_project,start_date,end_date
	# ,child.activity_type
	# from `tabTimesheet` as parent JOIN `tabTimesheet Detail` as child on 
	# parent.name = child.parent where 1=1 {0}""".format(conditions),as_dict=0)
	return data

@frappe.whitelist()
def approve_timesheets(timesheet_ids, approver):
	# print(timesheet_ids,'===')
	import json
	timesheet_ids = json.loads(timesheet_ids)
	for id in timesheet_ids:
		# print(id['name'])
		timesheets = frappe.get_all(
		"Timesheet",
		filters={"employee": ['in', id['employee']],
		"name": ['in', id['name']]
				},
		fields=["name", "employee", "workflow_state"]
		)
		# print('====',timesheets,'====')
		for timesheet in timesheets:
			time_logs = frappe.get_all('Timesheet Detail',
			filters = {'parent':timesheet['name']},
			fields = ['name','activity_type','reject','approve'])
			print('====',time_logs['activity_type'],'====')
			# if timesheet.workflow_state != "Approved":
			# 	frappe.db.set_value("Timesheet", timesheet.name, "workflow_state", "Approved")
			# 	print('=',timesheet.workflow_state)
			# 	frappe.db.commit()
			# else:
			# 	frappe.throw(f"Already approved for timesheet {timesheet.name} of {timesheet.employee}")
			for time_log in time_logs:
				if time_log['approve'] != 1 and time_log['reject'] !=1:
					
					frappe.db.set_value('Timesheet Detail',time_log['activity_type'],'approve',1)
					frappe.msgprint(f"Activities approval set successfully for {time_log.activity_type} of {timesheet.employee_name}")
					frappe.db.commit()
				
				else:
					frappe.throw(f"Already did action for timesheet activity type {time_log.activity_type} of {timesheet.employee_name}")
	        
	return "success"

@frappe.whitelist()
def reject_timesheets(timesheet_ids):
	# print(timesheet_ids,'===')
	import json
	timesheet_ids = json.loads(timesheet_ids)
	for id in timesheet_ids:
		timesheets = frappe.get_all(
		"Timesheet",
		filters={"employee": ['in', id['employee']],
		"name": ['in', id['name']]
				},
		fields=["name", "employee", "workflow_state"]
		)
		for timesheet in timesheets:
			time_logs = frappe.get_all('Timesheet Detail',
			filters = {'parent':timesheet['name']},
			fields = ['name','activity_type','reject','approve'])
			for time_log in time_logs:
				if time_log['reject']!=1 and time_log['approve'] !=1:
					frappe.db.set_value('Timesheet Detail',time_log['name'],'reject',1)
					frappe.db.commit()
					frappe.msgprint(f"Activities rejected successfully for {time_log.activity_type} for {timesheet.employee_name}")
				else:
					frappe.throw(f"Activities are already rejected for {time_log.activity_type} for {timesheet.employee_name}")

			# if timesheet.workflow_state != "Rejected":
			# 	frappe.db.set_value("Timesheet", timesheet.name, "workflow_state", "Rejected")
			# 	# print('=',timesheet.workflow_state)
			# 	frappe.db.commit()
			# else:
			# 	frappe.throw(f"Already rejected for timesheet {timesheet.name} of {timesheet.employee}")
	
	return "success"

