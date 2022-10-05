import sqlite3
import pandas as pd
import numpy as np
from .validators import InputFormValidation
from .db import BudgetDB
import uuid

class importCSV(object):

    def init(self, name):
        self.name = name
        

class importXLS(object):
   
    def __init__(self, file):
        self.file = file
        self.xls_data = pd.read_excel(self.file).rename(columns = {"Data transakcji": "date", "Szczegóły transakcji": "name","Kwota w walucie rachunku": "value"})[['date', 'name','value','category','sub-category']]
        self.xls_data['type'] = np.where(self.xls_data['value'] < 0, "expense", "income")
        self.xls_data['date'] = pd.to_datetime(self.xls_data["date"], dayfirst=True).astype(str)

    def validate_columns(self):
        print(self.xls_data)
        required_columns = ['name', 'value', 'date', 'type', 'category', 'sub-category']
        missing_columns = []
        for column in required_columns:
            if column not in list(self.xls_data.columns):
                missing_columns.append(column)
        if len(missing_columns) > 0:
            return(missing_columns)
        else:
            return 'validation_ok'

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
        # BudgetDB.clear_db()
        for row in self.xls_data.values.tolist():
            expense_name = row[1]
            expense_value = row[2]
            expense_category = row[3]
            expense_sub_category = row[4]
            expense_type = row[5]
            expense_date = row[0]
            input_uuid = str(uuid.uuid4())

            BudgetDB.insert_row(input_uuid, expense_name, expense_value, expense_category, expense_sub_category, expense_type, expense_date, clear_db='N')
