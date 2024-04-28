import pandas as pd
import numpy as np
from src.validators import InputFormValidation
from src.db.db import BudgetDB
from src.display_data import ShowBudgetTable
import uuid

class importCSV(object):

    def init(self, name):
        self.name = name
        

class importAliorXLS(object):
   
    def __init__(self, file):
        self.file = file
        self.xls_data = pd.read_excel(self.file,header=1).rename(columns = {"Data transakcji": "date",
                                                                            "Szczegóły transakcji": "name",
                                                                            "Kwota w walucie rachunku": "value",
                                                                            "Nazwa odbiorcy": "recipient"})[['date', 'name','value','recipient']]
        self.xls_data['type'] = np.where(self.xls_data['value'] < 0, "Expense", "Income")
        self.xls_data['date'] = pd.to_datetime(self.xls_data["date"], dayfirst=True).astype(str)
        self.assignment_rules_table = ShowBudgetTable.show_assignment_type_table()
        self.xls_data = self.xls_data.apply(self.assign_category_and_sub_category, axis=1)
        self.xls_data['category'] = self.xls_data['category'].fillna('Unknown')
        self.xls_data['sub_category'] = self.xls_data['sub_category'].fillna('Unknown')
        print(self.xls_data)


    def validate_columns(self):
        required_columns = ['name', 'value', 'date', 'type','recipient']
        missing_columns = []
        for column in required_columns:
            if column not in list(self.xls_data.columns):
                missing_columns.append(column)
        if len(missing_columns) > 0:
            return(missing_columns)
        else:
            return 'validation_ok'
        
    def assign_category_and_sub_category(self, row):
        for assignment_rule in self.assignment_rules_table.items:
            if str(assignment_rule.keyword).upper() in str(row['name']).upper() or str(assignment_rule.keyword).upper() in str(row['recipient']).upper():
                row['category'] = assignment_rule.category
                row['sub_category'] = assignment_rule.sub_category
        return row


    def validate_values(self):
        ErrorsArray = []

        for i, row in enumerate(self.xls_data.values.tolist()):
            expense_name = row[1]
            expense_value = row[2]
            expense_category = row[3]
            expense_sub_category = row[4]
            expense_type = row[5]
            expense_date = row[0]

            nameValidator = InputFormValidation(expense_name, "expense_name")
            valueValidator = InputFormValidation(expense_value, "expense_value")
            categoryValidator = InputFormValidation(expense_category, "category_name", type=expense_type)
            sub_categoryValidator = InputFormValidation(expense_sub_category, "sub_category_name", category=expense_category, type=expense_type)


            if nameValidator.check_length() is False:
                ErrorsArray.append("Name error in row " + str(i))

            if valueValidator.check_type() is False:
                ErrorsArray.append("Value error in row " + str(i))

            if (categoryValidator.check_length() is False) or (categoryValidator.check_name_existance() is True):
                ErrorsArray.append("Category error in row " + str(i))

            if (sub_categoryValidator.check_length() is False) or (sub_categoryValidator.check_name_existance() is True):
                ErrorsArray.append("Sub-Category error in row " + str(i))

        if len(ErrorsArray) > 0: 
            return(ErrorsArray)
        else:
            return 'validation_ok'

    def insert_to_db(self):
        for row in self.xls_data.iterrows():
            expense_name = row[1]['name']
            expense_value = row[1]['value']
            expense_category = row[1]['category']
            expense_sub_category = row[1]['sub_category']
            expense_type = row[1]['type']
            expense_date = row[1]['date']
            input_uuid = str(uuid.uuid4())

            BudgetDB.insert_row(input_uuid, expense_name, expense_value, expense_category, expense_sub_category, expense_type, expense_date, clear_db='N')
