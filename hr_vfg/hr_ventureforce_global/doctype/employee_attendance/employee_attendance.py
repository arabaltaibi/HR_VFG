# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe import msgprint, _
from datetime import datetime
from datetime import timedelta
from datetime import date as dt
import datetime as special
import time
from erpnext.hr.utils import get_holidays_for_employee
from frappe.utils import cstr, flt,getdate, today
import calendar


class EmployeeAttendance(Document):
    def autoname(self):
        self.name = make_autoname(self.employee + '-' + self.month)

    def validate(self):   
        total_early = 0
        total_lates = 0
        total_half_days = 0
        total_hr_worked = timedelta(hours=0, minutes=0, seconds=0)
        total_per_day_h = timedelta(hours=0, minutes=0, seconds=0)
        total_late_hr_worked = timedelta(hours=0, minutes=0, seconds=0)
        total_early_going_hrs= timedelta(hours=0, minutes=0, seconds=0)
        total_late_coming_hours = timedelta(hours=0, minutes=0, seconds=0)
        total_additional_hours = timedelta(hours=0, minutes=0, seconds=0)
        required_working_hrs = 0.0
        total_absents = 0
        holiday_doc = None
        half_day_leave = None
        self.no_of_nights = 0
        total_working_days=0
        present_days=0
        accun_holiday=0
        try:
            month = self.get_month_no(self.month)
            if len(self.table1) > 0:
                year = frappe.utils.getdate(self.table1[0].date).year
            else:
                year  = datetime.now().year
            _, num_days = calendar.monthrange(year, month)
            first_day = dt(year, month, 1)
            last_day = dt(year, month, num_days)
            self.total_working_days = num_days -len(get_holidays_for_employee(self.employee,first_day,last_day))
            no_of_sundays = len([1 for i in calendar.monthcalendar(year,
                                  month) if i[6] != 0])
            self.no_of_sundays = no_of_sundays
        except:
            pass
        leave_flag = False
        total_holiday_hours = 0
        for ii in range(len(self.table1)):
            first_in_time = timedelta(hours=1,minutes=0,seconds=0)
            first_out_time = timedelta(hours=1,minutes=0,seconds=0)
            self.table1[ii].late_sitting = None
            self.table1[ii].additional_hours = None
            self.table1[ii].late_coming_hours = None
            self.table1[ii].early_going_hours = None
            self.table1[ii].early = 0
            self.table1[ii].total_ot_amount = 0
            tempdate = datetime.strptime(
                        str(self.table1[ii].date), '%Y-%m-%d')
            #frappe.log_error(get_holidays_for_employee(self.employee,tempdate,tempdate)+[str(getdate(tempdate))],"test"+str(getdate(tempdate)))
            if str(getdate(self.table1[ii].date)) in get_holidays_for_employee(self.employee,tempdate,tempdate):
                        #frappe.msgprint(str(day_name))
                        leave_flag = True
                        if special.datetime.strptime(str(self.table1[ii].date).replace("-", " "), '%Y %m %d').weekday() == 6:
                            self.table1[ii].sunday = 1
                        else:
                            self.table1[ii].holiday = 1
                        if self.table1[ii-1].absent == 1:
                            p_date = datetime.strptime(
                                    str(self.table1[ii-1].date), '%Y-%m-%d')
                            lv = frappe.get_all("Leave Application", filters={"from_date":["<=",p_date],"to_date":[">=",p_date],"employee":self.employee,"status":"Approved"},fields=["*"])
                            if len(lv) > 0:
                                pass
                            else:
                                self.table1[ii].absent=1
                                total_absents+=1
            #try:
            if special.datetime.strptime(str(self.table1[ii].date).replace("-", " "), '%Y %m %d').weekday() == 6:
                            self.table1[ii].sunday = 1
            if not leave_flag:
                total_working_days+=1
            LA = frappe.get_all("Leave Application", filters={"from_date":["<=",tempdate],"to_date":[">=",tempdate],"employee":self.employee,"status":"Approved"},fields=["*"])
            if len(LA) > 0:
                if LA[0].half_day:
                    half_day_leave = 1
                else:
                    #frappe.log_error("1",self.table1[ii].date)
                    total_absents+=1
                    self.table1[ii].absent = 1
                    continue

            # except:
            #     pass
            try:
                total_time = None
                hrs = timedelta(hours=0, minutes=0, seconds=0)
                s_type =None
                day_data = None
               

                #s3 = time.strftime("%H:%M:%S", time.gmtime(diff))
                
                if self.table1[ii].check_in_1 and self.table1[ii].check_out_1:
                    x = datetime.strptime(
                        str(self.table1[ii].check_in_1), '%H:%M:%S').time()
                    y = datetime.strptime(
                        str(self.table1[ii].check_out_1), '%H:%M:%S').time()
                    xh, xm, xs = str(x).split(":")
                    yh, ym, ys = str(y).split(":")
                    # xz = int(xh)*3600+int(xm)*60+int(xs)*1
                    # yz = int(yh)*3600+int(ym)*60+int(ys)*1
                    # total_time = total_time + abs(yz - xz)
                    first_in_time = timedelta(hours=float(
                        xh), minutes=float(xm), seconds=float(xs))
                    first_out_time = timedelta(hours=float(
                        yh), minutes=float(ym), seconds=float(ys))
                    diff = str(first_out_time - first_in_time)
                    if "day" in diff:
                        diff = diff.split("day, ")[1].split(":")
                        diff = timedelta(hours=float(diff[0]), minutes=float(
                            diff[1]), seconds=float(diff[2]))
                    else:
                        diff = first_out_time - first_in_time
                    total_time = total_time + diff if total_time else diff
                    #frappe.msgprint(str(total_time))
                
                
                if self.table1[ii].check_in_1:
                    shift = None
                    shift_ass = frappe.get_all("Shift Assignment", filters={'employee': self.employee,
                                                                            'start_date': ["<=", getdate(self.table1[ii].date)],'end_date': [">=", getdate(self.table1[ii].date)]}, fields=["*"])
                    if len(shift_ass) > 0:
                        shift = shift_ass[0].shift_type
                    else:
                        shift_ass = frappe.get_all("Shift Assignment", filters={'employee': self.employee,
                                                                            'start_date': ["<=", getdate(self.table1[ii].date)]}, fields=["*"])
                    if len(shift_ass) > 0:
                        shift = shift_ass[0].shift_type
                    if shift == None:
                        frappe.throw(_("No shift available for this employee"))
                    self.table1[ii].shift = shift
                    shift_doc = frappe.get_doc("Shift Type", shift)
                    s_type = shift_doc.shift_type
                    self.table1[ii].absent = 0
                    #hours_added = datetime.timedelta(hours = 2)
                    #next_value  = self.table1[ii].check_in_1 = hours_added
                    day_name = datetime.strptime(
                        str(self.table1[ii].date), '%Y-%m-%d').strftime('%A')

                    threshold = timedelta(hours=2, minutes=0, seconds=0)
                    in_diff = first_in_time - shift_doc.start_time
                   
                    day_data = None
                    # frappe.msgprint(str(day_name))
                    for day in shift_doc.day:
                        # frappe.msgprint(str(day.day))
                        if day_name == day.day:
                            day_data = day
                            break

                    if self.table1[ii].holiday == 1 or self.table1[ii].sunday:
                        if total_time:
                            total_holiday_hours+=round(
                                        flt(total_time.total_seconds())/3600, 2)
                    if not day_data:
                        self.table1[ii].difference = total_time
                        #frappe.log_error(str(leave_flag)+"  "+str(total_time),"TESTS II")
                        if leave_flag and total_time and not self.table1[ii].holiday and not self.table1[ii].sunday:
                             total_late_hr_worked = total_late_hr_worked + total_time
                        #frappe.log_error("2",self.table1[ii].date)
                        continue
                    
                    if day_data.end_time > first_out_time:
                        per_day_h = first_out_time - first_in_time
                    else:
                        per_day_h = day_data.end_time - first_in_time
                    self.table1[ii].per_day_hour = per_day_h
                    if "day" in str(per_day_h):
                        per_day_h = str(per_day_h).split("day, ")[1].split(":")
                        # frappe.msgprint(str(req_working))
                        per_day_h = timedelta(hours=float(per_day_h[0]), minutes=float(
                            per_day_h[1]), seconds=float(per_day_h[2]))
                    
                    self.table1[ii].per_day_hour = per_day_h
                    total_per_day_h = total_per_day_h + per_day_h
                    # timedelta(hours=2, minutes=0, seconds=0)
                    req_working = day_data.end_time - day_data.start_time
                    if "day" in str(req_working):
                        req_working = str(req_working).split("day, ")[1].split(":")
                        # frappe.msgprint(str(req_working))
                        req_working = timedelta(hours=float(req_working[0]), minutes=float(
                            req_working[1]), seconds=float(req_working[2]))
                    if half_day_leave:
                        t = (flt(req_working.total_seconds())/3600)/2
                        required_working_hrs= required_working_hrs+t
                        #self.table1[ii].check_out_10 = t
                        

                    else:
                        required_working_hrs= required_working_hrs+round(
                                            flt(req_working.total_seconds())/3600, 2)
                    threshold = day_data.late_mark
                    half_day_time = day_data.half_day
                    late_mark = day_data.late_mark
                    in_diff = first_in_time - day_data.start_time
                    if not half_day_time:
                        half_day_time = day_data.late_mark
                    # frappe.msgprint(str(in_diff))
                    if "day" in str(in_diff):
                        in_diff = str(in_diff).split("day, ")[1].split(":")
                        # frappe.msgprint(str(in_diff))
                        in_diff = timedelta(hours=float(in_diff[0]), minutes=float(
                            in_diff[1]), seconds=float(in_diff[2]))

                    #adjust first_in_time 
                     
                    if first_in_time < day_data.start_time:
                        first_in_time = day_data.start_time

                    if first_in_time >= late_mark and first_in_time < half_day_time:
                        self.table1[ii].late = 1
                        if first_in_time - late_mark > timedelta(hours=0,minutes=30,seconds=0):
                             self.table1[ii].late_coming_hours = first_in_time - late_mark
                    else:
                        self.table1[ii].late = 0
                    if shift_doc.shift_type == "Night":
                        if first_in_time > late_mark:
                            if (first_in_time - late_mark) > timedelta(hours=12,minutes=0,seconds=0):
                                self.table1[ii].late = 0
                            else:
                                self.table1[ii].late = 1
                        elif first_in_time < late_mark:
                            if (late_mark - first_in_time) > timedelta(hours=12,minutes=0,seconds=0):
                                self.table1[ii].late = 1
                            else:
                                self.table1[ii].late = 0

                                

                    if first_in_time >= frappe.db.get_single_value('V HR Settings', 'night_shift_start_time'):
                        self.no_of_nights += 1
                   

                    if first_in_time >= half_day_time and shift_doc.shift_type != "Night":
                        self.table1[ii].half_day = 1
                    else:
                        self.table1[ii].half_day = 0
                    
                    if shift_doc.shift_type == "Night":
                        if first_in_time > half_day_time:
                            if (first_in_time - half_day_time) > timedelta(hours=12,minutes=0,seconds=0):
                                self.table1[ii].half_day = 0
                            else:
                                self.table1[ii].late = 0
                                self.table1[ii].half_day = 1
                        elif first_in_time < half_day_time:
                            if (half_day_time - first_in_time) > timedelta(hours=12,minutes=0,seconds=0):
                                self.table1[ii].half_day = 1
                                self.table1[ii].late = 0
                            else:
                                self.table1[ii].half_day = 0
                    
                    if self.table1[ii].check_out_1:
                        out_diff = day_data.end_time - first_out_time
                        if "day" in str(out_diff):
                            out_diff = str(out_diff).split("day, ")[1].split(":")
                            out_diff = timedelta(hours=float(out_diff[0]), minutes=float(
                                out_diff[1]), seconds=float(out_diff[2]))

                        # frappe.msgprint(day_data.max_early)
                        # frappe.msgprint(str((out_diff.total_seconds()/60)))
                        # self.table1[ii].check_out_9 = out_diff.total_seconds()/60
                        # self.table1[ii].check_out_10 = day_data.max_early
                        if (out_diff.total_seconds()/60) > 00.00 and (out_diff.total_seconds()/60) <= float(day_data.max_early):
                            if first_out_time < day_data.end_time:
                                self.table1[ii].early = 1
                        elif (out_diff.total_seconds()/60) >= float(day_data.max_early) and (out_diff.total_seconds()/60) < float(day_data.max_half_day):

                            self.table1[ii].half_day = 1
                            self.table1[ii].early = 0
                        elif (out_diff.total_seconds()/60) > 720:
                            tmp  = (out_diff.total_seconds()/60) -720
                            if tmp > 15.00 and tmp <= float(day_data.max_early):

                                #self.table1[ii].early = 1
                                pass
                            elif tmp >= float(day_data.max_early) and tmp < float(day_data.max_half_day):

                                self.table1[ii].half_day = 1
                                self.table1[ii].early = 0 
                        elif (out_diff.total_seconds()/60) > float(day_data.max_half_day) and self.table1[ii].sunday==0 and self.table1[ii].holiday==0:
                            if first_out_time < day_data.end_time:
                                self.table1[ii].absent = 1
                            #frappe.log_errorfrappe.log_error(day_data.max_half_day,"absent check")
                            
                        else:
                            self.table1[ii].early = 0
                        
                        out_diff = day_data.over_time_start - first_out_time
                        
                        if "day" in str(out_diff):
                            out_diff = str(out_diff).split("day, ")[1].split(":")
                            out_diff = timedelta(hours=float(out_diff[0]), minutes=float(
                                out_diff[1]), seconds=float(out_diff[2]))
                        
                        ot_start  = day_data.over_time_start if day_data.over_time_start else day_data.end_time
                        if (out_diff.total_seconds()/60) > 720 and first_out_time < ot_start and shift_doc.shift_type!="Night":
                            hrs = timedelta(hours=24, minutes=0,
                                            seconds=0) - out_diff
                            # if hrs > timedelta(hours=2, minutes=0,
                            #                 seconds=0):
                            ot_diff = ot_start - day_data.end_time
                            if "day" in str(ot_diff):
                                ot_diff = str(ot_diff).split("day, ")[1].split(":")
                                ot_diff = timedelta(hours=float(ot_diff[0]), minutes=float(
                                    ot_diff[1]), seconds=float(ot_diff[2]))
                            hrs = hrs + ot_diff
                            self.table1[ii].late_sitting = hrs
                        if (out_diff.total_seconds()/60) > 720 and first_out_time > ot_start and shift_doc.shift_type!="Night":
                            hrs = timedelta(hours=24, minutes=0,
                                            seconds=0) - out_diff
                            # if hrs > timedelta(hours=2, minutes=0,
                            #                 seconds=0):
                            ot_diff = ot_start - day_data.end_time
                            if "day" in str(ot_diff):
                                ot_diff = str(ot_diff).split("day, ")[1].split(":")
                                ot_diff = timedelta(hours=float(ot_diff[0]), minutes=float(
                                    ot_diff[1]), seconds=float(ot_diff[2]))
                            hrs = hrs + ot_diff
                            self.table1[ii].late_sitting = hrs
                        if first_out_time > ot_start and shift_doc.shift_type == "Night":
                            hrs = timedelta(hours=24, minutes=0,
                                            seconds=0) - out_diff
                            # if hrs > timedelta(hours=2, minutes=0,
                            #                 seconds=0):
                            ot_diff = ot_start - day_data.end_time
                            if "day" in str(ot_diff):
                                ot_diff = str(ot_diff).split("day, ")[1].split(":")
                                ot_diff = timedelta(hours=float(ot_diff[0]), minutes=float(
                                    ot_diff[1]), seconds=float(ot_diff[2]))
                            hrs = hrs + ot_diff
                            self.table1[ii].late_sitting = hrs
                        if self.table1[ii].absent == 1 or not self.table1[ii].check_out_1:
                            self.table1[ii].late_sitting = None
                        if self.table1[ii].late_sitting:
                            if self.table1[ii].late_sitting >= timedelta(hours=5,minutes=0,seconds=0):
                                
                                if self.table1[ii].late_sitting > timedelta(hours=6,minutes=0,seconds=0):
                                    self.table1[ii].additional_hours  =  self.table1[ii].late_sitting - timedelta(hours=6,minutes=0,seconds=0)
                                    total_additional_hours = total_additional_hours + self.table1[ii].additional_hours
                                
                                self.table1[ii].late_sitting = timedelta(hours=10,minutes=0,seconds=0)

                else:
                    if self.table1[ii].sunday==0 and self.table1[ii].holiday==0:
                        self.table1[ii].absent = 1 
                        self.table1[ii].late = 0
                        self.table1[ii].half_day = 0
                        self.table1[ii].early = 0

                if day_data:
                    if day_data.end_time > first_out_time and self.table1[ii].early ==1:
                        self.table1[ii].early_going_hours =  day_data.end_time - first_out_time
                        total_early_going_hrs = total_early_going_hrs + self.table1[ii].early_going_hours
                if self.table1[ii].sunday==1 or self.table1[ii].holiday==1:
                     self.table1[ii].absent = 0 
                if self.table1[ii].holiday==1: #and not self.table1[ii].check_in_1:
                     self.no_of_sundays+=1
                if first_in_time:
                    if first_in_time >= timedelta(hours=20,minutes=0,seconds=0) or s_type == "Night":
                        self.table1[ii].night = 1
                
                if self.table1[ii].absent==1 and half_day_leave and total_time:
                    if (total_time.total_seconds()/60) >= 255:
                        self.table1[ii].absent = 0
                        self.table1[ii].late = 0
                        self.table1[ii].half_day = 1
                        self.table1[ii].early = 0
                    
                    # frappe.msgprint(str(self.table1[ii].date))
                if self.table1[ii].early:
                    total_early += 1
                if self.table1[ii].late:
                    total_lates += 1
                    if self.table1[ii].late_coming_hours:
                        total_late_coming_hours = total_late_coming_hours + self.table1[ii].late_coming_hours
                if self.table1[ii].half_day:
                    total_half_days += 1
                #frappe.msgprint(self.table1[ii].absent)
                #frappe.log_error(self.table1[ii].absent,self.table1[ii].date)
                if self.table1[ii].absent == 1:
                    total_absents += 1
                    for num in reversed(range(ii)) :
                        if self.table1[num].holiday ==1 or self.table1[num].sunday==1:
                            self.table1[num].absent=1
                            total_absents += 1
                        else:
                            break
                if self.table1[ii].absent == 0 and self.table1[ii].check_in_1 and not leave_flag:
                    present_days+=1

                #frappe.log_error(str(leave_flag)+"  "+str(total_time),"TESTS")
                # if leave_flag and total_time:
                #     total_late_hr_worked = total_late_hr_worked + total_time
                    
                elif total_time:    
                    total_hr_worked = total_hr_worked + total_time
                
                if self.table1[ii].late_sitting:
                    # if self.table1[ii].late_sitting > timedelta(hours=1,minutes=0,seconds=0) \
                    #      and self.table1[ii].late_sitting <= timedelta(hours=1,minutes=50,seconds=0):
                    #      self.table1[ii].late_sitting = timedelta(hours=1,minutes=30,seconds=0)
                    # if self.table1[ii].late_sitting > timedelta(hours=1,minutes=50,seconds=0) \
                    #     and self.table1[ii].late_sitting <= timedelta(hours=2,minutes=25,seconds=0):
                    #     self.table1[ii].late_sitting = timedelta(hours=2,minutes=00,seconds=0)
                    # if self.table1[ii].late_sitting > timedelta(hours=2,minutes=25,seconds=0) \
                    #     and self.table1[ii].late_sitting <= timedelta(hours=2,minutes=50,seconds=0):
                    #     self.table1[ii].late_sitting = timedelta(hours=2,minutes=30,seconds=0)
                    total_late_hr_worked = total_late_hr_worked + self.table1[ii].late_sitting #hrs
                self.table1[ii].difference = total_time  # time.strftime(
                #     "%H:%M:%S", time.gmtime(total_time))
                if leave_flag == True and getdate(tempdate) <= getdate(today()):
                    #frappe.msgprint(str(tempdate)+" ||| "+ str(getdate(today())))
                    accun_holiday+=1
                if self.table1[ii].extra_absent:
                    total_absents+=1
                if self.table1[ii].total_ot_amount > 0:
                    total_late_hr_worked = total_late_hr_worked + timedelta(hours=1,minutes=0,seconds=0)
                half_day_leave = False
                leave_flag = False
               
            except:
                frappe.log_error(frappe.get_traceback(),"Attendance")
             

        self.hours_worked = round(
            flt((total_hr_worked-total_late_hr_worked).total_seconds())/3600, 2)
        self.late_sitting_hours = round(
            flt(total_late_hr_worked.total_seconds())/3600, 2)
        #self.over_time = 0
        self.over_time = self.late_sitting_hours
        # self.difference = round(
        #     (flt(self.hours_worked)-flt(required_working_hrs)), 2)
        if self.over_time >= 1:
            self.over_time = round(self.over_time)
        else:
            self.over_time = 0.0
        self.difference = round(
            flt(total_late_coming_hours.total_seconds())/3600, 2)
        
        self.extra_hours = round(
            flt(total_additional_hours.total_seconds())/3600, 2)
        self.total_absents = total_absents
        self.total_lates = total_lates
        self.total_early_goings = total_early
        self.total_half_days = total_half_days
        self.total_early_going_hours = total_early_going_hrs
        self.holiday_hour = total_holiday_hours
        if self.holiday_hour >= 1:
            self.holiday_hour = round(self.holiday_hour)
        else:
            self.holiday_hour = 0.0
        t_lat = int(total_lates/4) if total_lates >= 4 else 0
        t_earl = 0 #int(total_early/4) if total_early > 2 else 0
        self.late_absent = t_earl + t_lat
        # if self.difference > 0:
        #     #self.over_time = self.difference
        #     self.short_hours = 0
        # else:
            #self.over_time = 0
        self.short_hours = self.difference

        self.total_working_hours = round(required_working_hrs,2)
        #self.total_working_days = total_working_days
        self.present_days = present_days #+accun_holiday
        self.adjusted_late_half_days = int(total_lates-5) if total_lates > 5  else 0

    def get_month_no(self, month):
        dict_={
            "January":1,
            "February":2,
            "March":3,
            "April":4,
            "May":5,
            "June":6,
            "July":7,
            "August":8,
            "September":9,
            "October":10,
            "November":11,
            "December":12
        }
        return dict_[month]