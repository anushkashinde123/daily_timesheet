import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe.utils import add_to_date,now_datetime, add_days,nowtime,today,getdate,flt


def test(doc,method=None):
    # frappe.msgprint('success')
    settings = frappe.db.get_single_value('Settings timesheet','day_limit')
    limit_date = add_to_date(datetime.now().strftime('%Y-%m-%d'),days=-settings,as_string=True)
    # diff = days_diff(datetime.now().strftime('%Y-%m-%d'),)
    # print('=========',limit_date)
    if str(doc.start_date) < limit_date:
        frappe.throw("Sorry you can't fill timesheets now as your deadline is closed.")
    
    t_setttings = frappe.get_doc('Settings timesheet')
    # print(doc.time_logs[row].get('hours'))
    for i in doc.time_logs:
        # print(i.hours)
        # print(i.idx)
        if i.hours > t_setttings.lesshours and i.hours < t_setttings.morehours:
            frappe.msgprint(f"Please break your tasks properly for row {i.idx}")
        elif i.hours >= t_setttings.morehours:
            frappe.throw(f"Error : Hours in Timesheet are more ,please break tasks for row {i.idx}")
    

def cron():
    print("heyy there\n\n")
    print("timesheet reminders")
    
    timesheet_settings = frappe.get_single("Settings timesheet")
    reminder_timings = timesheet_settings.time

    if not reminder_timings:
        return

    current_time = nowtime()
    for timing in reminder_timings:

        # print(timing)
        if any(str(current_time)[:5]== str(getattr(timing,time_field))[:5] for time_field in ['time_1']):
            employee = frappe.get_all("Employee", filters={"status": "Active"},fields=["personal_email",'employee_name'])
            for employee in employee:

                if timing.compulsory:
                    send_reminder(employee)
                else:
                    timesheet_count = frappe.db.count("Timesheet", {
                    "employee_name": employee.employee_name,
                    "start_date": add_days(datetime.now().strftime('%Y-%m-%d'), -2), 
                    })
                    if timesheet_count == 0:
                        send_reminder(employee)
                        print("send successful")

        # elif any(str(current_time)[:5]==str(getattr(timing,time_field))[:5] for time_field in ['compulsory']):
        #     employee = frappe.get_all("Employee", filters={"status": "Active"},fields=["personal_email",'employee_name'])
        #     for employee in employee:
        #         send_reminder(employee)

def send_reminder(employee):
    # Send reminder email
    recipient = employee['personal_email']
    if recipient:
        frappe.sendmail(
            recipients=recipient,
            subject="Timesheet Reminder",
            message=f"Dear {employee['employee_name']},<br><br>"
                    f"Please ensure your timesheet is submitted before deadline.<br><br>"
                    f"Thank you."
                    
        )

# def daily(doc,method=None):
#     print('daily=========')
#     print(doc.employee)
#     print(doc.start_date)
    # print("======",data)
    # timesheet_settings = frappe.get_single("Settings timesheet")
    # reminder_timings = timesheet_settings.time
    # attendance_time = timesheet_settings.attendance_time
    # if not attendance_time:
    #     data = frappe.db.sql("""select sum(total_hours) from `tabTimesheet` 
    #     where employee={doc.employee} and start_date = {doc.start_date}
    #     """)
    #     print(data)


def calculate_employee_hours():
    print("calculate emp hrs")
    two_days_ago = add_days(today(), -2)
    one_days_ago = add_days(today(),-1)
    print(one_days_ago)
    
    employees = frappe.get_all("Employee", fields=["employee"])
    print(employees)
    
    for employee in employees:
        emp_id = employee.employee
        
        for date in frappe.db.sql_list("SELECT DISTINCT(start_date) FROM `tabTimesheet` WHERE date(creation) BETWEEN %s AND %s and start_date = %s", 
        (one_days_ago, today(),one_days_ago)):
            print('==',date)
            total_hours = frappe.db.sql("""
                SELECT SUM(total_hours) FROM `tabTimesheet` where start_date = %s
                 and employee = %s group by employee
                """,(one_days_ago,emp_id))
            total_hours = total_hours[0][0] if total_hours else 0
            print(f"Total hours for {emp_id} on {one_days_ago}: {total_hours}")
            if total_hours >= 8:
                attendance_status = 'Present'
            elif 0 < total_hours < 8:
                attendance_status = 'Half Day'
            else:
                attendance_status = 'Absent'
            attendance = frappe.db.get_value('Attendance',{'employee': emp_id, 'attendance_date': one_days_ago})
            if not attendance:
                attendance_doc = frappe.new_doc('Attendance')
                attendance_doc.employee = emp_id
                attendance_doc.status = attendance_status
                attendance_doc.attendance_date = one_days_ago
                attendance_doc.insert()
                attendance_doc.submit()
                frappe.db.commit()
            else:
                attendance_doc = frappe.get_doc('Attendance',attendance)
                attendance_doc.cancel()
                attendance_doc.delete()
                attendance_doc = frappe.new_doc('Attendance')
                attendance_doc.employee = emp_id
                attendance_doc.status = attendance_status
                attendance_doc.attendance_date = one_days_ago
                attendance_doc.save()  
                attendance_doc.submit() 
                frappe.db.commit()

           
        for date in frappe.db.sql_list("SELECT DISTINCT(start_date) FROM `tabTimesheet` WHERE date(creation) BETWEEN %s AND %s and start_date = %s", 
        (two_days_ago, today(),two_days_ago)):
            print('====',date)
            total_hours = frappe.db.sql("""
                SELECT SUM(total_hours) FROM `tabTimesheet` where start_date = %s
                 and employee = %s group by employee
                """,(two_days_ago,emp_id))

            total_hours = total_hours[0][0] if total_hours else 0
            print(f"Total hours for {emp_id} on {two_days_ago}: {total_hours}")

            # attendance_status = 'Present' if total_hours >= 8 elif total_hours!=0 and total_hours<8 'Half Day'
            if total_hours >= 8:
                attendance_status = 'Present'
            elif 0 < total_hours < 8:
                attendance_status = 'Half Day'
            else:
                attendance_status = 'Absent'
            attendance = frappe.db.get_value('Attendance',{'employee': emp_id, 'attendance_date': two_days_ago})

            if not attendance:
                attendance_doc = frappe.new_doc('Attendance')
                attendance_doc.employee = emp_id
                attendance_doc.status = attendance_status
                attendance_doc.attendance_date = two_days_ago
                attendance_doc.insert()
                attendance_doc.submit()
                frappe.db.commit()
            else:
                attendance_doc = frappe.get_doc('Attendance',attendance)
                attendance_doc.cancel()
                attendance_doc.delete()
                attendance_doc = frappe.new_doc('Attendance')
                attendance_doc.employee = emp_id
                attendance_doc.status = attendance_status
                attendance_doc.attendance_date = two_days_ago
                attendance_doc.save()  # Save the modified document
                attendance_doc.submit() 
                frappe.db.commit()
                

# def on_submit(doc,method=None):

#     attendance = frappe.new_doc('Attendance')

#     attendance.employee = doc.employee
#     if doc.total_hours >= 8:
#         attendance.status = 'Present'
#     else:
#         attendance.status = 'Half Day'

#     attendance.attendance_date = doc.start_date
#     attendance.save(ignore_permissions=True)
#     attendance.submit()


    
