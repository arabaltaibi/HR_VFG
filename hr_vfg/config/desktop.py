from frappe import _

def get_data():
    return [
        {
            "module_name": "HR VentureForce Global",
            "color": "grey",
            "icon": "octicon octicon-file-directory",
            "type": "module",
            "label": _("HR VentureForce Global")
        },
        {
            "label": _("HR VentureForce Global"),
            "items": [
                {
                    "type": "doctype",
                    "name": "V HR Settings",
                    "label": _("V HR Settings"),
                    "description": _("V HR Settings"),
                },
                {
                    "type": "doctype",
                    "name": "Employee Attendance",
                    "label": _("Employee Attendance"),
                    "description": _("Employee Attendance"),
                },
            ],
        },
    ]