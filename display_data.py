import db as db
from flask_table import Table, Col

class BudgetItemTable(Table):

    name = Col('expense_name')
    value = Col('expense_value')


class TypesItemTable(Table):

    name = Col('types_name')

class CategoriesItemTable(Table):

    name = Col('categories_name')

class SubCategoriesItemTable(Table):

    name = Col('sub_categories_name')

class BudgetItem(object):

    def __init__(self, input_uuid, name, value, category, sub_category, expense_type, date):
        self.input_uuid = input_uuid
        self.name = name
        self.value = value
        self.category = category
        self.sub_category = sub_category
        self.expense_type = expense_type
        self.date = date


class TypesItem(object):

    def __init__(self, name):
        self.name = name


class CategoriesItem(object):

    def __init__(self, name):
        self.name = name

class SubCategoriesItem(object):

    def __init__(self, name):
        self.name = name


#show DB tables
class ShowBudgetTable():

    def show_budget_table(**kwargs):
        if 'limit' in kwargs:
            if 'active_filters' in kwargs:
                db_results = db.BudgetDB.show_db(limit=kwargs['limit'], offset=kwargs['offset'], active_filters=kwargs['active_filters'])
            else:
                db_results = db.BudgetDB.show_db(limit=kwargs['limit'], offset=kwargs['offset'])

        elif 'active_filters' in kwargs:
            db_results = db.BudgetDB.show_db(active_filters=kwargs['active_filters'])

        else:
            db_results = db.BudgetDB.show_db()

        total_count = len(db_results)
        table_results = []
        value_sum = 0
        for record in db_results:
            value_sum += float(record[2])
            table_results.append(BudgetItem(record[0],record[1],record[2],record[3],record[4],record[5],record[6]))
        table = BudgetItemTable(table_results)
        return (table, value_sum, total_count)

    def show_types_table():
        db_results = db.TypesDB.show_db()
        table_results = []
        for record in db_results:
            table_results.append(TypesItem(record[0]))
        table = TypesItemTable(table_results)
        return (table)

    def show_categories_table(**kwargs):
        if 'type' in kwargs:
            db_results = db.CategoriesDB.show_db(type=kwargs['type'])
        else:
            db_results = db.CategoriesDB.show_db()
        table_results = []
        for record in db_results:
            table_results.append(CategoriesItem(record[0]))
        table = CategoriesItemTable(table_results)
        return (table)

    def show_sub_categories_table(**kwargs):
        if 'type' in kwargs:
            db_results = db.SubCategoriesDB.show_db(type=kwargs["type"], category=kwargs["category"])
        else:
            db_results = db.SubCategoriesDB.show_db()
        table_results = []
        for record in db_results:
            table_results.append(SubCategoriesItem(record[0]))
        table = SubCategoriesItemTable(table_results)
        return (table)

    def show_sub_category_data_table(category, sub_category, **kwargs):
        if 'limit' in kwargs:
            if 'active_filters' in kwargs:
                db_results = db.BudgetDB.sub_category_data_table(category, sub_category, active_filters=kwargs['active_filters'], limit=kwargs['limit'],offset=kwargs['offset'])
            else:
                db_results = db.BudgetDB.sub_category_data_table(category, sub_category, limit=kwargs['limit'],offset=kwargs['offset'])
        elif 'active_filters' in kwargs:
            db_results = db.BudgetDB.sub_category_data_table(category, sub_category, active_filters=kwargs['active_filters'])
        else:
            db_results = db.BudgetDB.sub_category_data_table(category, sub_category)
            
        total_count = len(db_results)
        return(db_results, total_count)

class ShowChartsData():
    def show_pie_chart(**kwargs):
        if 'active_filters' in kwargs:
            db_results = db.BudgetDB.show_db(pie_chart='pie_chart', active_filters=kwargs['active_filters'])
        else:
            db_results = db.BudgetDB.show_db(pie_chart='pie_chart')
        return(db_results)
    def sub_cat_chart_data(category, **kwargs):
        if 'active_filters' in kwargs:
            db_results = db.BudgetDB.show_db(sub_cat_pie_chart=category, active_filters=kwargs['active_filters'])
        else:
            db_results = db.BudgetDB.show_db(sub_cat_pie_chart=category)
        return(db_results)    
