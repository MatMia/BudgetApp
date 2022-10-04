from .display_data import *
import time

#supporting functions - type validation
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

#input form validation
class InputFormValidation(object):

    def __init__(self, key, name, **kwargs):
        self.key = key
        self.name = name
        if 'category' in kwargs:
            self.category = kwargs["category"]
        if 'type' in kwargs:
            self.type = kwargs["type"]

    def check_type(self):
        if self.name == "expense_value":
            if isfloat(self.key):
                return True
            else:
                return False

    def check_length(self):
        if self.name == "expense_name" or self.name == "category_name" or self.name == "sub_category_name" or self.name == "type_name":
            if len(self.key) > 2:
                return True
            else:
                return False
    
    def check_name_existance(self):
        if self.name == "type_name":
            types = ShowBudgetTable.show_types_table()
            types_table = []
            for key in types.items:
                types_table.append(key.name)
            if self.key in types_table:
                return False
            else:
                return True
        elif self.name == "category_name":
            categories = ShowBudgetTable.show_categories_table(type=self.type)
            categories_table = []
            for key in categories.items:
                categories_table.append(key.name)
            if self.key in categories_table:
                return False
            else:
                return True
        elif self.name == "sub_category_name":
            sub_categories = ShowBudgetTable.show_sub_categories_table(self.type, self.category)
            sub_categories_table = []
            for key in sub_categories.items:
                sub_categories_table.append(key.name)
            if self.key in sub_categories_table:
                return False
            else:
                return True    


#filters validation
class BudgetFiltersValidation(object):

    def __init__(self, date_from, date_to):
        self.date_from = time.strptime(date_from, "%Y-%m-%d")
        self.date_to = time.strptime(date_to, "%Y-%m-%d")

    def compare_dates(self):
        if self.date_from <= self.date_to:
            return True
        else:
            return False