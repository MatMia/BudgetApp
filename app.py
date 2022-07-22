from flask import Flask, flash, request, render_template, session, redirect, url_for, jsonify
from markupsafe import escape
from .db import BudgetDB, CategoriesDB, SubCategoriesDB
from flask_table import Table, Col


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


#main page and input form endpoints
@app.route("/")
def expenses_main():
        categories = ShowBudgetTable.show_categories_table()
        return render_template("index.html", validity_class_name="form-control is-invalid", validity_class_value="form-control is-invalid", \
            invalid_feedback_name="", invalid_feedback_value="", \
                input_form_buttom="nav-link active", current_budget_button="nav-link", categories_button = "nav-link", \
                    categories=categories, sub_categories=[])

@app.route('/', methods=['GET', 'POST'])
def expense_input():
    if request.form.get("btn") == "submit_form":
        return InputForm.main_input_form()

    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_categories'))



#read sub_categories from the category value - AJAX
@app.route('/input_sub_category', methods=['GET', 'POST'])
def input_sub_category():
        active_category = [name for name, value in request.form.to_dict().items()][0]
        sub_categories = ShowBudgetTable.show_sub_categories_table(active_category)
        ajax_dict = {}
        for i, value in enumerate(sub_categories.items):
            ajax_dict.update({value.name : i})
        return (jsonify(ajax_dict))




#budget status endpoints
@app.route("/db_state")
def show_db_state():
    db_results = ShowBudgetTable.show_budget_table()
    table = db_results[0]
    value_sum = round(db_results[1],2)
    return render_template("budget_table.html", table=table, value_sum=value_sum, \
        input_form_buttom="nav-link", current_budget_button="nav-link active", categories_button = "nav-link")


@app.route('/db_state', methods=['GET', 'POST'])
def return_to_input():
    if request.form.get("delete_record"):
        BudgetDB.delete_record(request.form.get("delete_record"))
        return succesfull_message_budget('delete')

    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_categories'))




#categories endpoints
@app.route("/categories")
def show_db_categories():
    table = ShowBudgetTable.show_categories_table()
    return render_template("categories_table.html", table=table, \
        input_form_buttom="nav-link", current_budget_button="nav-link", categories_button = "nav-link active")

@app.route('/categories', methods=['GET', 'POST'])
def categories_actions():
    if request.form.get("add_category") == "my_category":
        return InputForm.category_input_form()

    elif request.form.get("delete_category_record"):
        CategoriesDB.delete_record(request.form.get("delete_category_record"))
        return succesfull_message_categories('delete', request.form.get("delete_category_record"))

    elif request.form.get("show_subcategories"):
        category = request.form.get("show_subcategories")
        return redirect(url_for('show_db_sub_categories', category=category))

    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_categories'))





#sub_categories endpoints
@app.route("/sub_categories/<category>")
def show_db_sub_categories(category):
    table = ShowBudgetTable.show_sub_categories_table(category)
    return render_template("sub_categories_table.html", table=table, category=category, \
        input_form_buttom="nav-link", current_budget_button="nav-link", categories_button = "nav-link active")

@app.route('/sub_categories/<category>', methods=['GET', 'POST'])
def sub_categories_actions(category):
    if request.form.get("add_sub_category") == "my_sub_category":
        return InputForm.sub_category_input_form(category)

    elif request.form.get("delete_sub_category_record"):
        SubCategoriesDB.delete_record(category, request.form.get("delete_sub_category_record"))
        return succesfull_message_sub_categories('delete', request.form.get("delete_sub_category_record"), category)

    elif request.form.get("btn") == "return_to_categories":
        return redirect(url_for('show_db_categories'))

    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_categories'))




#flash messages handler
def succesfull_message_budget(action, **kwargs):
    if action == 'submit':
        flash("Request submitted succesfully with \n\n name: " + kwargs["name"] + "\n\n and value: " + str(kwargs["value"] + " PLN."))
        return redirect(url_for('expenses_main'))
    elif action == 'delete':
        flash("Record deleted succesfully")
        return redirect(url_for('show_db_state'))

def succesfull_message_categories(action, name):
    if action == 'submit':
        flash("Request submitted succesfully with \n\n name: " + name)
        return redirect(url_for('show_db_categories'))
    elif action == 'delete':
        flash("Record deleted succesfully")
        return redirect(url_for('show_db_categories'))

def succesfull_message_sub_categories(action, name, category):
    if action == 'submit':
        flash("Request submitted succesfully with \n\n name: " + name)
        return redirect(url_for('show_db_sub_categories', category=category))
    elif action == 'delete':
        flash("Record deleted succesfully")
        return redirect(url_for('show_db_sub_categories', category=category))




#insert records to DB
def insert_to_budget_db(expense_name, expense_value, expense_category, expense_sub_category, expense_date):
    BudgetDB.insert_row(expense_name, expense_value, expense_category, expense_sub_category, expense_date, clear_db='N')

def insert_to_categories_db(category_name):
    CategoriesDB.insert_row(category_name, clear_db='N')

def insert_to_sub_categories_db(category, sub_category_name):
    SubCategoriesDB.insert_row(category, sub_category_name, clear_db='N')



#supporting functions - type validation
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False



#input form validation
class InputFormValidation(object):

    def __init__(self, key, name):
        self.key = key
        self.name = name

    def check_type(self):
        if self.name == "expense_value":
            if isfloat(self.key):
                return True
            else:
                return False

    def check_length(self):
        if self.name == "expense_name" or self.name == "category_name" or self.name == "sub_category_name":
            if len(self.key) > 2:
                return True
            else:
                return False


class InputForm():

    #budget input form
    def main_input_form():
        expense_name =  request.form.get("expense_name")
        expense_value = request.form.get("expense_value")
        expense_category = request.form.get("expense_category")
        expense_sub_category = request.form.get("expense_sub_category") 
        expense_date = request.form.get("expense_date")

        nameValidator = InputFormValidation(expense_name, "expense_name")
        valueValidator = InputFormValidation(expense_value, "expense_value")

        # name field validation
        if nameValidator.check_length() is False:
            invalid_feedback_name = "Name needs to have at least 3 characters."
            name_boolean = False
        else:
            invalid_feedback_name = ""
            name_boolean = True

        # value field validation
        if valueValidator.check_type() is False:
            invalid_feedback_value = "Value needs to be numeric."
            value_boolean = False
        else:
            invalid_feedback_value = ""
            value_boolean = True
            
        # summary validation condition    
        if name_boolean is True and value_boolean is True:
            insert_to_budget_db(expense_name, expense_value, expense_category, expense_sub_category, expense_date)
            print(expense_name, expense_value, expense_category, expense_sub_category, expense_date)
            return succesfull_message_budget('submit', name=expense_name, value=expense_value)
        else:
            categories = ShowBudgetTable.show_categories_table()
            return render_template("index.html", validity_class_name="form-control is-invalid", validity_class_value="form-control is-invalid", \
                invalid_feedback_name=invalid_feedback_name, invalid_feedback_value=invalid_feedback_value, \
                    input_form_buttom="nav-link active", current_budget_button="nav-link", categories_button = "nav-link", \
                        categories=categories, sub_categories=[])

    #category input form
    def category_input_form():
        category_name =  request.form.get("category_name")
        categoryValidator = InputFormValidation(category_name, "category_name")

        # name field validation
        if categoryValidator.check_length() is False:
            invalid_feedback_category = "Category needs to have at least 3 characters."
            category_boolean = False
        else:
            invalid_feedback_category = ""
            category_boolean = True

        # summary validation condition    
        if category_boolean is True:
            insert_to_categories_db(category_name)
            return succesfull_message_categories('submit', category_name)
        else:
            flash("Category hasn't been submitted. " + invalid_feedback_category + " Please re-submit the category.")
            return redirect(url_for('show_db_categories'))
            
    #sub_category input form
    def sub_category_input_form(category):
        sub_category_name =  request.form.get("sub_category_name")
        sub_categoryValidator = InputFormValidation(sub_category_name, "sub_category_name")

        # name field validation
        if sub_categoryValidator.check_length() is False:
            invalid_feedback_sub_category = "Sub-category needs to have at least 3 characters."
            sub_category_boolean = False
        else:
            invalid_feedback_sub_category = ""
            sub_category_boolean = True

        # summary validation condition    
        if sub_category_boolean is True:
            insert_to_sub_categories_db(category, sub_category_name)
            return succesfull_message_sub_categories('submit', sub_category_name, category)
        else:
            flash("Category hasn't been submitted. " + invalid_feedback_sub_category + " Please re-submit the category.")
            return redirect(url_for('show_db_sub_categories', category=category))


class BudgetItemTable(Table):

    name = Col('expense_name')
    value = Col('expense_value')

class CategoriesItemTable(Table):

    name = Col('categories_name')

class SubCategoriesItemTable(Table):

    name = Col('sub_categories_name')

class BudgetItem(object):

    def __init__(self, name, value, category, sub_category, date):
        self.name = name
        self.value = value
        self.category = category
        self.sub_category = sub_category
        self.date = date

class CategoriesItem(object):

    def __init__(self, name):
        self.name = name

class SubCategoriesItem(object):

    def __init__(self, name):
        self.name = name




#show DB states
class ShowBudgetTable():

    def show_budget_table():
        db_results = BudgetDB.show_db()
        table_results = []
        value_sum = 0
        for record in db_results:
            value_sum += float(record[1])
            table_results.append(BudgetItem(record[0],record[1],record[2],record[3],record[4]))
        table = BudgetItemTable(table_results)
        return (table, value_sum)

    def show_categories_table():
        db_results = CategoriesDB.show_db()
        table_results = []
        for record in db_results:
            table_results.append(CategoriesItem(record[0]))
        table = CategoriesItemTable(table_results)
        return (table)

    def show_sub_categories_table(category):
        db_results = SubCategoriesDB.show_db(category)
        table_results = []
        for record in db_results:
            table_results.append(SubCategoriesItem(record[0]))
        table = SubCategoriesItemTable(table_results)
        return (table)



#main application handler
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)