import src.display_data as display_data
import time
from dataclasses import dataclass
import src.db.db as db
import pandas as pd

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
        if self.name == "expense_name" or self.name == "category_name" or self.name == "sub_category_name" or self.name == "type_name" or self.name  == 'key_word_name':
            if len(self.key) > 2:
                return True
            else:
                return False
    
    def check_name_existance(self):
        if self.name == "type_name":
            types = display_data.ShowBudgetTable.show_types_table()
            types_table = []
            for key in types.items:
                types_table.append(key.name)
            if self.key in types_table:
                return False
            else:
                return True
        elif self.name == "category_name":
            categories = display_data.ShowBudgetTable.show_categories_table(type=self.type)
            categories_table = []
            for key in categories.items:
                categories_table.append(key.name)
            if self.key in categories_table:
                return False
            else:
                return True
        elif self.name == "sub_category_name":
            sub_categories = display_data.ShowBudgetTable.show_sub_categories_table(type=self.type, category=self.category)
            sub_categories_table = []
            for key in sub_categories.items:
                sub_categories_table.append(key.name)
            if self.key in sub_categories_table:
                return False
            else:
                return True    


#filters validation
class BudgetFiltersValidation(object):

    def __init__(self, active_filters):
        if active_filters['date_from'] : self.date_from = time.strptime(active_filters['date_from'], "%Y-%m-%d") 
        if active_filters['date_to'] : self.date_to = time.strptime(active_filters['date_to'], "%Y-%m-%d") 

    def compare_dates(self):
        if self.date_from <= self.date_to:
            return True
        else:
            return False

#assignment_rule validation
@dataclass
class AssignmentRuleValidator:
    keyword: str
    type: str
    category: str
    sub_category: str

    def check_name_existance(self) -> bool:
        pd_assignment_rules = pd.DataFrame(db.CategoriesAssignment.show_db(), columns=['assignment_rule_uuid', 'keyword', 'type', 'category','sub_category'])
        assignment_rule_tuple = (self.keyword, self.type, self.category, self.sub_category)
        for row in pd_assignment_rules.iterrows():
            row_tuple = (row[1].keyword, row[1].type, row[1].category, row[1].sub_category)
            if row_tuple == assignment_rule_tuple:
                return False
        return True
        
    def check_type_existance(self) -> bool:
        available_types = pd.DataFrame(db.TypesDB.show_db(), columns=['type'])
        if self.type not in available_types['type'].to_list():
            return False
        else:
            return True
        
    def check_category_existance(self) -> bool:
        available_categories = pd.DataFrame(db.CategoriesDB.show_db(), columns=['category', 'type'])
        if self.category not in available_categories['category'].to_list():
            return False
        else:
            return True
        
    def check_sub_category_existance(self) -> bool:
        available_sub_categories = pd.DataFrame(db.SubCategoriesDB.show_db(full_data='Y'), columns=['category', 'sub_category', 'type'])
        sub_categories_list = []
        for i in available_sub_categories.get(['category','sub_category']).iterrows():
            sub_categories_list.append((i[1]['category'],i[1]['sub_category']))
        if (self.category, self.sub_category) not in sub_categories_list:
            return False
        else:
            return True
        
    def check_length(self, value):

        if len(value) > 2:
            return True 
        else:
            return False

