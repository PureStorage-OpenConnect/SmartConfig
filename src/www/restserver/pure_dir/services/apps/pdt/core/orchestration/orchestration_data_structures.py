
class Input():
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, hidden, isbasic, group_member, order, helptext, recommended):
        self.dt_type = dt_type
        self.static = static
        self.api = api
        self.name = name
        self.label = label
        self.static_values = static_values
        self.svalue = svalue
        self.mapval = mapval
        self.mandatory = mandatory
        self.group_member = group_member
        self.order = order
        self.helptext = helptext
        self.hidden = hidden
        self.isbasic = isbasic
        self.recommended = recommended


class Output():
    def __init__(self, dt_type, name, tvalue):
        self.dt_type = dt_type
        self.name = name
        self.tvalue = tvalue


class Label(Input):
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, hidden, isbasic, helptext="", group_member='0', order='0', recommended='0'):
        Input.__init__(self, dt_type, static, api, name, label, static_values,
                       svalue, mapval, mandatory, hidden, isbasic, helptext=helptext, group_member=group_member, order=order, recommended=recommended)
        self.ip_type = "label"


class Textbox(Input):
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, hidden, isbasic, validation_criteria, helptext="", group_member='0', order='0', recommended='0'):
        Input.__init__(self, dt_type, static, api, name, label, static_values,
                       svalue, mapval, mandatory, hidden, isbasic, helptext=helptext, group_member=group_member, order=order, recommended=recommended)
        self.ip_type = "text-box"
        self.validation_criteria = validation_criteria


class Dropdown(Input):
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, hidden, isbasic, helptext="", group_member='0', order='0', recommended='0', validation_criteria=''):
        Input.__init__(self, dt_type, static, api, name, label, static_values,
                       svalue, mapval, mandatory, hidden, isbasic, helptext=helptext, group_member=group_member, order=order, recommended=recommended)
        self.ip_type = "drop-down"
        self.validation_criteria = validation_criteria


class Multiselect(Input):
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, hidden, isbasic, helptext="", group_member='0', order='0', recommended='0'):
        Input.__init__(self, dt_type, static, api, name, label, static_values,
                       svalue, mapval, mandatory, hidden, isbasic, helptext=helptext, group_member=group_member, order=order, recommended=recommended)
        self.ip_type = "multi-select"


class Radiobutton(Input):
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, hidden, isbasic, helptext="", group_member='0', order='0', recommended='0'):
        Input.__init__(self, dt_type, static, api, name, label, static_values,
                       svalue, mapval, mandatory, hidden, isbasic, helptext=helptext, group_member=group_member, order=order, recommended=recommended)
        self.ip_type = "radio-button"


class Checkbox(Input):
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, allow_multiple_values, hidden, isbasic, helptext="", group_member='0', order='0', recommended='0'):
        Input.__init__(self, dt_type, static, api, name, label, static_values,
                       svalue, mapval, mandatory, hidden, isbasic, helptext=helptext, group_member=group_member, order=order, recommended=recommended)
        self.ip_type = "check-box"
        self.allow_multiple_values = allow_multiple_values


class Multiselecttext(Input):
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, hidden, isbasic, helptext="", group_member='0', order='0', recommended='0'):
        Input.__init__(self, dt_type, static, api, name, label, static_values,
                       svalue, mapval, mandatory, hidden, isbasic, helptext=helptext, group_member=group_member, order=order, recommended=recommended)
        self.ip_type = "multi-select-text"


class Multiselectdropdown(Input):
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, hidden, isbasic, helptext="", group_member='0', order='0', recommended='0'):
        Input.__init__(self, dt_type, static, api, name, label, static_values,
                       svalue, mapval, mandatory, hidden, isbasic, helptext=helptext, group_member=group_member, order=order, recommended=recommended)
        self.ip_type = "multiselect-dropdown"


class Dropbox(Input):
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, helptext="", group_member='0', order='0', recommended='0'):
        Input.__init__(self, dt_type, static, api, name, label, static_values,
                       svalue, mapval, mandatory, hidden, isbasic, helptext=helptext, group_member=group_member, order=order, recommended=recommended)
        self.ip_type = "drop-box"


class Rangepicker(Input):
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, hidden, isbasic, min_range, max_range, max_fixed, min_interval, helptext="", group_member='0', order='0', recommended='0'):
        Input.__init__(self, dt_type, static, api, name, label, static_values,
                       svalue, mapval, mandatory, hidden, isbasic, helptext=helptext, group_member=group_member, order=order, recommended=recommended)
        self.ip_type = "range-picker"
        self.min_range = min_range
        self.max_range = max_range
        self.max_fixed = max_fixed
        self.min_interval = min_interval


class Group(Input):
    def __init__(self, dt_type, static, api, name, label, static_values, svalue, mapval, mandatory, validation_criteria, members, add, hidden, isbasic, helptext="", order='0', recommended='0'):
        Input.__init__(self, dt_type, static, api, name, label, static_values,
                       svalue, mapval, mandatory, hidden, isbasic, helptext=helptext, group_member='0', order=order, recommended=recommended)
        self.ip_type = "group"
        self.members = members
        self.add = add
        self.validation_criteria = validation_criteria
