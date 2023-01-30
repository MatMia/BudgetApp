import pandas as pd
import numpy as np
from datetime import datetime
import db.db as db

class MonthsComparison(object):

    def __init__(self, months_filter_value, type="default_value", category="default_value"):
        self.months_list = months_filter_value.split(",")
        self.months_list = ['01-' + month for month in self.months_list]
        self.months_list = [datetime.strftime(datetime.strptime(month, "%d-%B-%y"),"%Y-%m") for month in self.months_list]

        if type != "default_value" and category == "default_value":
            self.required_months_sql_criteria = '''formatted_date in (''' + str(self.months_list)[1:-1] + ''') and expense_type = "''' + type + '''"'''
        elif category != "default_value":
            self.required_months_sql_criteria = '''formatted_date in (''' + str(self.months_list)[1:-1] + ''') \
                 and expense_type = "''' + type + '''"''' + '''and category = "''' + category + '''"'''
        else:
            self.required_months_sql_criteria = '''formatted_date in (''' + str(self.months_list)[1:-1] + ''')'''

        self.type = type
        self.category = category

    def get_months_data_grouped_by_date_and_type(self):
        months_data_grouped_by_year_and_type = db.Analytics.get_grouped_data_by_date_and_type(self.required_months_sql_criteria)
        months_data_grouped_by_year_and_type_df = pd.DataFrame(months_data_grouped_by_year_and_type, columns=["date", "type", "value"])
        missing_months_df = pd.DataFrame([])

        for month in self.months_list:
            if month not in list(months_data_grouped_by_year_and_type_df['date']):
                for type in months_data_grouped_by_year_and_type_df.type:
                    missing_months_df = missing_months_df.append({'date' : month, 'type' : type, 'value' : 0}, ignore_index=True)
        final_df = pd.concat([months_data_grouped_by_year_and_type_df, missing_months_df])

        final_pivot_table = pd.pivot_table(final_df, values='value', index=['type'],
                    columns=['date'],fill_value=0)

        return(self.transform_data(final_pivot_table))


    def get_months_data_grouped_by_date_type_and_category(self):
        months_data_grouped_by_year_type_and_category = db.Analytics.get_grouped_data_by_date_type_and_category(self.required_months_sql_criteria)
        months_data_grouped_by_year_type_and_category_df = pd.DataFrame(months_data_grouped_by_year_type_and_category, columns=["date", "type", "category", "value"])
        missing_months_df = pd.DataFrame([])

        for month in self.months_list:
            if month not in list(months_data_grouped_by_year_type_and_category_df['date']):
                for category in months_data_grouped_by_year_type_and_category_df.category:
                    missing_months_df = missing_months_df.append({'date' : month, 'type' : self.type, 'category' : category, 'value' : 0}, ignore_index=True)
        final_df = pd.concat([months_data_grouped_by_year_type_and_category_df, missing_months_df])
        final_pivot_table = pd.pivot_table(final_df, values='value', index=['category'],
                    columns=['date'],fill_value=0)

        return(self.transform_data(final_pivot_table))


    def get_months_data_grouped_by_date_type_category_and_sub_category(self):
        months_data_grouped_by_year_type_category_and_sub_category = db.Analytics.get_grouped_data_by_date_type_category_and_sub_category(self.required_months_sql_criteria)
        months_data_grouped_by_year_type_category_and_sub_category_df = pd.DataFrame(months_data_grouped_by_year_type_category_and_sub_category, columns=["date", "type", "category", "sub_category", "value"])
        missing_months_df = pd.DataFrame([])

        for month in self.months_list:
            if month not in list(months_data_grouped_by_year_type_category_and_sub_category_df['date']):
                for sub_category in months_data_grouped_by_year_type_category_and_sub_category_df.sub_category:
                    missing_months_df = missing_months_df.append({'date' : month, 'sub_category' : sub_category, 'value' : 0}, ignore_index=True)
        final_df = pd.concat([months_data_grouped_by_year_type_category_and_sub_category_df, missing_months_df])
        final_pivot_table = pd.pivot_table(final_df, values='value', index=['sub_category'],
                    columns=['date'],fill_value=0)

        return(self.transform_data(final_pivot_table))

    def transform_data(self, final_pivot_table):
        my_working_pivot_values = []
        my_final_pivot_values =[]
        for i, row in enumerate(final_pivot_table.values):
            my_working_pivot_values.append(final_pivot_table.index[i])
            for item in row:
                my_working_pivot_values.append(item)
            my_final_pivot_values.append(my_working_pivot_values)
            my_working_pivot_values = []

        return(list(final_pivot_table.columns), list(my_final_pivot_values))
