import json
import secrets
from sre_compile import isstring
from flask import Flask, flash, request, render_template, session, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, login_required
from flask import session
import numpy as np
from db import db
from display_data import *
from validators import *
import src.month_to_month as month_to_month
from flask_paginate import Pagination, get_page_parameter
import random
import uuid
from upload_data import importAliorXLS
from datetime import timedelta


app = Flask(__name__)
app.config.update(
   REMEMBER_COOKIE_SECURE = False,
   SESSION_COOKIE_SAMESITE='Strict',
)

#login section
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
app.secret_key = secrets.token_hex()

class User(object):
    def __init__(self, user_id):
        self.user_id = user_id
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    def get_id(self):
        return self.user_id

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User(user_id)
    return None

@app.route("/")
def login_page():
    return render_template("login_form.html")

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.form.get("login_btn") == "login_btn":
        user_id = request.form.get("userId")
        user_pwd = request.form.get("password")  

        if verify_login_details(user_id, user_pwd):
            user = load_user(user_id)
            login_user(user, remember=True, duration=timedelta(hours=1))
            return redirect(url_for('expenses_main'))
        else:
            flash("Incorrect user name or password.")
            return redirect(url_for('login_page'))
        
    elif request.form.get("add_user"):
        username = request.form.get("username")
        password = request.form.get("password") 
        new_user_request = db.LoginDB(username, password)
        if not new_user_request.validate_new_user_credentials():
            flash("User password doesn't meet password criteria: needs to be between 6 and 20 chars.")
            return redirect(url_for('login_page'))
        if not new_user_request.check_user_existance():
            flash("User already exists.")
            return redirect(url_for('login_page'))
        if new_user_request.add_new_user():
            flash("User has been created sucesfully.")
        else:
            flash("User hasn't been created.")
        return redirect(url_for('login_page'))


def verify_login_details(user_id: str, user_pwd: str) -> bool:
    if db.LoginDB(user_id, user_pwd).authenticate_login():
        return True
    else:
        return False

#end of login section


#single input page and input form endpoints
@login_required
@app.route("/single_input")
def expenses_main():
    types = ShowBudgetTable.show_types_table()
    return render_template("single_input_form.html", validity_class_name="form-control is-invalid", validity_class_value="form-control is-invalid", \
            invalid_feedback_name="", invalid_feedback_value="", \
                input_form_buttom="nav-link active", current_budget_button="nav-link", categories_button = "nav-link", analytics_button = "nav-link", assignment_rules_button = "nav-link", \
                    types=types, categories=[], sub_categories=[])

@app.route('/single_input', methods=['GET', 'POST'])
@login_required 
def expense_input():
    if request.form.get("btn") == "submit_form":
        return InputForm.main_input_form()

    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form") == "bulk_input_form":
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))

    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))
    
#bulk upload
@login_required
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.form.get("submit_xls"):
        file = importAliorXLS(request.files['xls_file'])

        # values_validation = file.validate_values()
        # if values_validation != 'validation_ok':
        #     flash("Incorrect values in the file: " + str(values_validation))
        #     return redirect(url_for('upload_file'))
        # else:
        #     flash("Records uploaded succesfully")

        columns_validation = file.validate_columns()
        if columns_validation != 'validation_ok':
            flash("Columns " + str(columns_validation) + " are missing in the file. Please correct the file.")
        else:
            file.insert_to_db()
            flash("Records uploaded succesfully")
            
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form") == "bulk_input_form":
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))
    
    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))
    
    else:
        return render_template("bulk_input_form.html", \
            input_form_buttom="nav-link active", current_budget_button="nav-link", categories_button = "nav-link", analytics_button = "nav-link", assignment_rules_button = "nav-link")

#read categories from the type value - AJAX
@login_required
@app.route('/input_category', methods=['GET', 'POST'])
def input_category():
        active_type = [name for name, value in request.form.to_dict().items()][0]
        categories = ShowBudgetTable.show_categories_table(type=active_type)
        ajax_dict = {}
        for i, value in enumerate(categories.items):
            ajax_dict.update({value.name : i})
        return (jsonify(ajax_dict))


#read sub_categories from the category value - AJAX
@login_required
@app.route('/input_sub_category', methods=['GET', 'POST'])
def input_sub_category():
    posted_date = []
    for name, item in request.form.items():
        posted_date.append(item)
    active_category = posted_date[0]
    active_type = posted_date[1]
    sub_categories = ShowBudgetTable.show_sub_categories_table(type=active_type, category=active_category)
    ajax_dict = {}
    for i, value in enumerate(sub_categories.items):
        ajax_dict.update({value.name : i})
    return (jsonify(ajax_dict))



#budget status endpoints
@login_required
@app.route("/db_state")
def show_db_state():
    types = ShowBudgetTable.show_types_table()
    categories = ShowBudgetTable.show_categories_table()
    sub_categories = ShowBudgetTable.show_sub_categories_table()

    total_db_results = ShowBudgetTable.show_budget_table()
    total = total_db_results[2]
    value_sum = round(total_db_results[1],2)

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page
    pagination = Pagination(page=page, per_page=per_page, total=total)

    paged_db_results = ShowBudgetTable.show_budget_table(limit=per_page, offset=offset)
    table = paged_db_results[0]  

    return render_template("budget_table.html", table=table, value_sum=value_sum, pagination=pagination, \
        input_form_buttom="nav-link", current_budget_button="nav-link active", categories_button = "nav-link", analytics_button = "nav-link", assignment_rules_button = "nav-link", \
            date_from = "", date_to = "", category_filter = "Nothing Selected", sub_category_filter = "Nothing Selected", type_filter = "Nothing Selected", \
                types=types, categories=categories, sub_categories=sub_categories)

@login_required
@app.route("/db_state", methods=['GET', 'POST'])
def return_to_input():
    if request.form.get("delete_record"):
        db.BudgetDB.delete_record(request.form.get("delete_record"))
        return succesfull_message_budget('delete')
    
    elif request.form.get("modify_record"):
        id = request.form.get("modify_record")
        return redirect(url_for('modify_record', id=id))
        
    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form") == "bulk_input_form":
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))

    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))
    
    elif request.form.get("apply_filters"):
        date_from = request.form.get("date_from")
        date_to = request.form.get("date_to")
        category_filter = request.form.getlist("category_filter_value")
        sub_category_filter = request.form.getlist("sub_category_filter_value")
        type_filter = request.form.getlist("type_filter_value")
        return redirect(url_for('show_db_state_filters', filters=({"date_from": date_from, "date_to" : date_to, "category_filter" : category_filter, \
            "sub_category_filter" : sub_category_filter, "type_filter" : type_filter})))

    elif request.form.get("btn") == "charts":
        return redirect(url_for('pie'))

@login_required
@app.route("/db_state/<filters>", methods=['GET', 'POST'])
def show_db_state_filters(filters):
    types = ShowBudgetTable.show_types_table()
    categories = ShowBudgetTable.show_categories_table()
    sub_categories = ShowBudgetTable.show_sub_categories_table()

    filters = json.loads(filters.replace("'",'"'))
    date_from = filters["date_from"]
    date_to =  filters["date_to"]

    optional_filters = Filters.define_optional_filters(filters)
    category_filter = optional_filters[0]
    sub_category_filter = optional_filters[1]
    type_filter = optional_filters[2]

    active_filters = Filters.get_active_filters(filters)

    #validate filters conditions
    if Filters.budget_filters(active_filters) is True:
        total_db_results = ShowBudgetTable.show_budget_table(active_filters=active_filters)
        total = total_db_results[2]
        value_sum = round(total_db_results[1],2)

        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 10
        offset = (page - 1) * per_page
        pagination = Pagination(page=page, per_page=per_page, total=total)

        paged_db_results = ShowBudgetTable.show_budget_table(limit=per_page, offset=offset, active_filters=active_filters)
        table = paged_db_results[0] 

        if request.form.get("delete_record"):
            db.BudgetDB.delete_record(request.form.get("delete_record"))
            return succesfull_message_budget('delete')
        
        elif request.form.get("modify_record"):
            id = request.form.get("modify_record")
            return redirect(url_for('modify_record_with_filters', id=id, filters=active_filters))

        elif request.form.get("menu_input_form") == "my_input_form":
            return redirect(url_for('expenses_main'))

        elif request.form.get("menu_input_form") == "bulk_input_form":
            return redirect(url_for('upload_file'))

        elif request.form.get("menu_current_budget") == "my_current_budget":
            return redirect(url_for('show_db_state'))

        elif request.form.get("menu_categories") == "my_categories":
            return redirect(url_for('show_db_types'))

        elif request.form.get("analytics_menu") == "my_analytics":
            return redirect(url_for('show_main_analytics'))
        
        elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
            return redirect(url_for('show_db_assignment_rules'))
    
        elif request.form.get("apply_filters"):
            date_from = request.form.get("date_from")
            date_to = request.form.get("date_to")
            category_filter = request.form.getlist("category_filter_value")
            sub_category_filter = request.form.getlist("sub_category_filter_value")
            type_filter = request.form.getlist("type_filter_value")
            return redirect(url_for('show_db_state_filters', filters=({"date_from": date_from, "date_to" : date_to, "category_filter" : category_filter, \
            "sub_category_filter" : sub_category_filter, "type_filter" : type_filter})))

        elif request.form.get("clear_filters") == 'my_clear_filters':
            return redirect(url_for('show_db_state'))

        elif request.form.get("btn") == "charts":
            return redirect(url_for('filtered_pie', filters=active_filters))

        else:
            succesfull_filters(active_filters)
            return render_template("budget_table.html", table=table, value_sum=value_sum, pagination=pagination, \
                input_form_buttom="nav-link", current_budget_button="nav-link active", categories_button = "nav-link", analytics_button = "nav-link", assignment_rules_button = "nav-link", \
                date_from=date_from, date_to=date_to, category_filter=category_filter, sub_category_filter=sub_category_filter, type_filter=type_filter, \
                types=types, categories=categories, sub_categories=sub_categories)
    else:
        return redirect(url_for('show_db_state'))


#Modify record
@login_required
@app.route("/modify_record/<id>", methods=['GET', 'POST'])
def modify_record(id):

    types = ShowBudgetTable.show_types_table()

    if request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form") == "bulk_input_form":
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))
    
    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))
    
    elif request.form.get("return_to_budget") == "my_return_to_budget":
        return redirect(url_for('show_db_state'))
    
    elif request.form.get("modify_record") == "my_modify_record":
        id = id
        name = request.form.get("record_name")
        value = request.form.get("record_value")
        category = request.form.get("expense_category")
        sub_category = request.form.get("expense_sub_category")
        expense_type = request.form.get("expense_type")
        date = request.form.get("expense_date")
        try:
            db.BudgetDB.modify_record(id,name,value,category,sub_category,expense_type,date)
            succesfull_message_budget("modify")
        except:
            flash("There was a problem with record modification. Please try again.")
        return redirect(url_for('show_db_state'))
    
    else:
        record_details = db.BudgetDB.get_record_details(id)
        record_details_table = ShowBudgetTable.show_record_details(record_details[0])
        return render_template("modify_record.html", record_details_table=record_details_table, types=types,\
                    input_form_buttom="nav-link", current_budget_button="nav-link active", categories_button = "nav-link", analytics_button = "nav-link", assignment_rules_button = "nav-link")

@login_required
@app.route('/modify_record/<id>&<filters>', methods=['GET', 'POST'])
def modify_record_with_filters(id, filters):

    types = ShowBudgetTable.show_types_table()

    if request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form") == "bulk_input_form":
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))
    
    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))
    
    elif request.form.get("return_to_budget") == "my_return_to_budget":
        return redirect(url_for('show_db_state_filters', filters=filters))
    
    elif request.form.get("modify_record") == "my_modify_record":
        id = id
        name = request.form.get("record_name")
        value = request.form.get("record_value")
        category = request.form.get("expense_category")
        sub_category = request.form.get("expense_sub_category")
        expense_type = request.form.get("expense_type")
        date = request.form.get("expense_date")
        try:
            db.BudgetDB.modify_record(id,name,value,category,sub_category,expense_type,date)
            succesfull_message_budget("modify")
        except:
            flash("There was a problem with record modification. Please try again.")
        return redirect(url_for('show_db_state_filters', filters=filters))
    
    else:
        record_details = db.BudgetDB.get_record_details(id)
        record_details_table = ShowBudgetTable.show_record_details(record_details[0])
        return render_template("modify_record.html", record_details_table=record_details_table, types=types,\
                    input_form_buttom="nav-link", current_budget_button="nav-link active", categories_button = "nav-link", analytics_button = "nav-link", assignment_rules_button = "nav-link")


#display unfiltered pie charts
@login_required
@app.route('/db_state/pie')
def pie():
    types = ShowBudgetTable.show_types_table()
    categories = ShowBudgetTable.show_categories_table()
    sub_categories = ShowBudgetTable.show_sub_categories_table()

    pie_chart_data = ShowChartsData.show_pie_chart()
    labels = []
    values = []
    for row in pie_chart_data:
        labels.append(row[0])
        values.append(row[1])

    number_of_colors = len(labels)
    colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                for i in range(number_of_colors)]

    return render_template('charts.html', title='test_charts', labels=labels, values=values, colors=colors, \
        input_form_buttom="nav-link", current_budget_button="nav-link active", categories_button = "nav-link", analytics_button = "nav-link", assignment_rules_button = "nav-link", \
            date_from = "", date_to = "", category_filter = "Nothing Selected", sub_category_filter = "Nothing Selected", type_filter = "Nothing Selected", \
                types=types, categories=categories, sub_categories=sub_categories)


@login_required
@app.route('/db_state/pie', methods=['GET', 'POST'])
def pie_charts():
    if request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form") == "bulk_input_form":
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))

    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))
        
    elif request.form.get("btn") == "return_to_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("apply_filters"):
        updated_date_from = request.form.get("date_from")
        updated_date_to = request.form.get("date_to")
        updated_category_filter = request.form.getlist("category_filter_value")
        updated_sub_category_filter = request.form.getlist("sub_category_filter_value")
        updated_type_filter = request.form.getlist("type_filter_value")
        updated_filters = {"date_from": updated_date_from, "date_to" : updated_date_to, "category_filter" : updated_category_filter, \
            "sub_category_filter" : updated_sub_category_filter, "type_filter" : updated_type_filter}
        if Filters.budget_filters(updated_filters) is True:
            return redirect(url_for('filtered_pie', filters=updated_filters))         
        else:
            return redirect(url_for('pie'))



#display filtered pie charts
@login_required
@app.route('/pie/<filters>', methods=['GET', 'POST'])
def filtered_pie(filters):
    types = ShowBudgetTable.show_types_table()
    categories = ShowBudgetTable.show_categories_table()
    sub_categories = ShowBudgetTable.show_sub_categories_table()

    filters = json.loads(filters.replace("'",'"'))
    date_from = filters["date_from"]
    date_to =  filters["date_to"]

    optional_filters = Filters.define_optional_filters(filters)
    category_filter = optional_filters[0]
    sub_category_filter = optional_filters[1]
    type_filter = optional_filters[2]

    active_filters = Filters.get_active_filters(filters)

    succesfull_filters(active_filters)
    
    if request.form.get("menu_input_form") == "my_input_form":
        session['_flashes'].clear()
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form") == "bulk_input_form":
        session['_flashes'].clear()
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        session['_flashes'].clear()
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        session['_flashes'].clear()
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))

    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))
    
    elif request.form.get("apply_filters"):
        updated_date_from = request.form.get("date_from")
        updated_date_to = request.form.get("date_to")
        updated_category_filter = request.form.getlist("category_filter_value")
        updated_sub_category_filter = request.form.getlist("sub_category_filter_value")
        updated_type_filter = request.form.getlist("type_filter_value")
        updated_filters = {"date_from": updated_date_from, "date_to" : updated_date_to, "category_filter" : updated_category_filter, \
            "sub_category_filter" : updated_sub_category_filter, "type_filter" : updated_type_filter}

        session['_flashes'].clear()
        if Filters.budget_filters(updated_filters) is True:
            return redirect(url_for('filtered_pie', filters=updated_filters))
        else:
            return redirect(url_for('filtered_pie', filters=active_filters))

    elif request.form.get("clear_filters") == 'my_clear_filters':
        session['_flashes'].clear()
        return redirect(url_for('pie'))

    elif request.form.get("btn") == "return_to_budget":
            session['_flashes'].clear()
            return redirect(url_for('show_db_state_filters', filters=active_filters))

    else:
        pie_chart_data = ShowChartsData.show_pie_chart(active_filters=active_filters)
        labels = []
        values = []
        for row in pie_chart_data:
            labels.append(row[0])
            values.append(row[1])

        number_of_colors = len(labels)
        colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                    for i in range(number_of_colors)]
        return render_template('charts_filtered.html', title='test_charts', labels=labels, values=values, colors=colors, \
            input_form_buttom="nav-link", current_budget_button="nav-link active", categories_button = "nav-link", analytics_button = "nav-link", assignment_rules_button = "nav-link", \
                date_from=date_from, date_to=date_to, category_filter=category_filter, sub_category_filter=sub_category_filter, type_filter=type_filter, \
                types=types, categories=categories, sub_categories=sub_categories)



#read sub-category pie chart data - AJAX
@login_required
@app.route('/sub_category_chart', methods=['GET', 'POST'])
def sub_category_chart():
        category = [name for name, value in request.form.to_dict().items()]
        sub_cat_chart_data = ShowChartsData.sub_cat_chart_data(category)
        dict_without_colors = {}

        #pack data into dict
        for row in sub_cat_chart_data:
            dict_without_colors.update({row[0]:row[1]})

        return(dict_without_colors)

@login_required
@app.route('/sub_category_data_table', methods=['GET', 'POST'])
def get_sub_cat_data_table():
    posted_data = []
    sub_cat_data_table_dict = {}
    for name, value in request.form.items():
        posted_data.append(value)
    category = posted_data[0]
    sub_category = posted_data[1]

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page

    total_count = ShowBudgetTable.show_sub_category_data_table(category, sub_category)[1]
    sub_category_data = ShowBudgetTable.show_sub_category_data_table(category, sub_category)[0]
    pagination = Pagination(page=page, per_page=per_page, total=total_count)

    #pack data into dict
    for i, row in enumerate(sub_category_data):
        sub_cat_data_table_dict.update({i:row})

    return(sub_cat_data_table_dict)



#read sub-category filtered pie chart data - AJAX
@login_required
@app.route('/filtered_sub_category_chart', methods=['GET', 'POST'])
def filtered_sub_category_chart():
    posted_data = []
    for name,value in request.form.items():
        posted_data.append(value)
    category = posted_data[0]
    date_from = posted_data[1]
    date_to = posted_data[2]
    category_filter =  posted_data[3].split(',')
    sub_category_filter =  posted_data[4].split(',')
    type_filter =  posted_data[5].split(',')
    active_filters = Filters.get_active_filters({"date_from": date_from, "date_to" : date_to, "category_filter" : category_filter, \
        "sub_category_filter" : sub_category_filter, "type_filter" : type_filter})
    sub_cat_chart_data = ShowChartsData.sub_cat_chart_data(category, active_filters=active_filters)
    dict_without_colors = {}

    #pack data into dict
    for row in sub_cat_chart_data:
        dict_without_colors.update({row[0]:row[1]})

    return(dict_without_colors)

@login_required
@app.route('/filtered_sub_category_data_table', methods=['GET', 'POST'])
def get_filtered_sub_cat_data_table():
    posted_data = []
    sub_cat_data_table_dict = {}
    for name, value in request.form.items():
        posted_data.append(value)
    category = posted_data[0]
    sub_category = posted_data[1]
    date_from = posted_data[2]
    date_to = posted_data[3]
    category_filter =  posted_data[4].split(',')
    sub_category_filter =  posted_data[5].split(',')
    type_filter =  posted_data[6].split(',')
    active_filters = Filters.get_active_filters({"date_from": date_from, "date_to" : date_to, "category_filter" : category_filter, \
        "sub_category_filter" : sub_category_filter, "type_filter" : type_filter})

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page

    total_count = ShowBudgetTable.show_sub_category_data_table(category, sub_category, active_filters=active_filters)[1]
    sub_category_data = ShowBudgetTable.show_sub_category_data_table(category, sub_category, active_filters=active_filters)[0]
    pagination = Pagination(page=page, per_page=per_page, total=total_count)

    #pack data into dict
    for i, row in enumerate(sub_category_data):
        sub_cat_data_table_dict.update({i:row})

    return(sub_cat_data_table_dict)



#types endpoints
@login_required
@app.route("/types")
def show_db_types():
    table = ShowBudgetTable.show_types_table()
    return render_template("types_table.html", table=table, \
        input_form_buttom="nav-link", current_budget_button="nav-link", categories_button = "nav-link active", analytics_button = "nav-link", assignment_rules_button = "nav-link")

@login_required
@app.route('/types', methods=['GET', 'POST'])
def types_actions():
    if request.form.get("add_type") == "my_type":
        return InputForm.type_input_form()

    elif request.form.get("delete_type_record"):
        db.TypesDB.delete_record(request.form.get("delete_type_record"))
        return succesfull_message_types('delete', request.form.get("delete_type_record"))

    elif request.form.get("show_categories"):
        type = request.form.get("show_categories")
        return redirect(url_for('show_db_categories', type=type))

    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form") == "bulk_input_form":
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))

    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))


#categories endpoints
@login_required
@app.route("/categories/<type>")
def show_db_categories(type):
    table = ShowBudgetTable.show_categories_table(type=type)
    return render_template("categories_table.html", table=table, type=type, \
        input_form_buttom="nav-link", current_budget_button="nav-link", categories_button = "nav-link active", analytics_button = "nav-link", assignment_rules_button = "nav-link",)

@login_required
@app.route('/categories/<type>', methods=['GET', 'POST'])
def categories_actions(type):
    if request.form.get("add_category") == "my_category":
        return InputForm.category_input_form(type)

    elif request.form.get("delete_category_record"):
        db.CategoriesDB.delete_record(request.form.get("delete_category_record"), type)
        return succesfull_message_categories('delete', request.form.get("delete_category_record"), type)

    elif request.form.get("show_subcategories"):
        category = request.form.get("show_subcategories")
        return redirect(url_for('show_db_sub_categories', category=category, type=type))

    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form") == "bulk_input_form":
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))

    elif request.form.get("btn") == "return_to_types":
        return redirect(url_for('show_db_types'))
    
    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))



#sub_categories endpoints
@login_required
@app.route("/sub_categories/<category>, <type>")
def show_db_sub_categories(category, type):
    table = ShowBudgetTable.show_sub_categories_table(type=type, category=category)
    return render_template("sub_categories_table.html", table=table, category=category, type=type, \
        input_form_buttom="nav-link", current_budget_button="nav-link", categories_button = "nav-link active", analytics_button = "nav-link", assignment_rules_button = "nav-link")

@login_required
@app.route('/sub_categories/<category>, <type>', methods=['GET', 'POST'])
def sub_categories_actions(category, type):
    if request.form.get("add_sub_category") == "my_sub_category":
        return InputForm.sub_category_input_form(category, type)

    elif request.form.get("delete_sub_category_record"):
        db.SubCategoriesDB.delete_record(type, category, request.form.get("delete_sub_category_record"))
        return succesfull_message_sub_categories('delete', request.form.get("delete_sub_category_record"), category, type)

    elif request.form.get("btn") == "return_to_categories":
        return redirect(url_for('show_db_categories', type=type))

    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form") == "bulk_input_form":
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))
    
    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))


#assignment rules endpoints
@login_required
@app.route("/AssignmentRules")
def show_db_assignment_rules():
    assignment_rules_table = ShowBudgetTable.show_assignment_type_table()
    types_table = ShowBudgetTable.show_types_table()
    return render_template("assignment_rules.html", assignment_rules_table=assignment_rules_table, types_table=types_table, \
        input_form_buttom="nav-link", current_budget_button="nav-link", categories_button = "nav-link", analytics_button = "nav-link", assignment_rules_button = "nav-link active", \
            months_filter_value = "", my_content_types=[""], my_content_categories=[""])

@login_required
@app.route("/AssignmentRules", methods=['GET', 'POST'])
def assignment_rules_actions():
    if request.form.get("add_assignment_rule") == "my_assignment_rule":
        return InputForm.assignment_rule_input_form()
    
    elif request.form.get("delete_assignment_rule_record"):
        db.CategoriesAssignment.delete_record(request.form.get("delete_assignment_rule_record"))
        return succesfull_message_assignment_rule('delete', request.form.get("delete_assignment_rule_record"))
    
    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form")== "bulk_input_form":
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))
    
    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))

#analytics endpoints
@login_required
@app.route("/M2Manalytics")
def show_main_analytics():
    return render_template("month_to_month.html", \
        input_form_buttom="nav-link", current_budget_button="nav-link", categories_button = "nav-link", analytics_button = "nav-link active", assignment_rules_button = "nav-link", \
            months_filter_value = "", my_content_types=[""], my_content_categories=[""])

@login_required
@app.route('/M2Manalytics', methods=['GET', 'POST'])
def main_analytics():
    if request.form.get("btn") == "submit_form":
        return InputForm.main_input_form()

    elif request.form.get("clear_month_to_month_filters") == 'my_clear_filters':
        return redirect(url_for('show_main_analytics'))

    elif request.form.get("apply_month_to_month_filters") == "my_apply_filters":
        months_filter_value = request.form.get("months_filter")
        m2m_data = month_to_month.MonthsComparison(months_filter_value)
        months_data_grouped_by_date_and_type = m2m_data.get_months_data_grouped_by_date_and_type()
        return render_template("month_to_month.html", \
            input_form_buttom="nav-link", current_budget_button="nav-link", categories_button = "nav-link", analytics_button = "nav-link active", assignment_rules_button = "nav-link", \
                months_filter_value = months_filter_value, my_content_types = months_data_grouped_by_date_and_type)
    
    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_input_form") == "bulk_input_form":
        return redirect(url_for('upload_file'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))

    elif request.form.get("menu_categories") == "my_categories":
        return redirect(url_for('show_db_types'))

    elif request.form.get("analytics_menu") == "my_analytics":
        return redirect(url_for('show_main_analytics'))
    
    elif request.form.get("menu_assignment_rules") == "my_assignment_rules":
        return redirect(url_for('show_db_assignment_rules'))

@login_required
@app.route('/get_categories_section_in_analytics', methods=['GET', 'POST'])
def get_categories_section_in_analytics():
    accepted_data = [value for name, value in request.form.to_dict().items()]
    months_filter_value = accepted_data[0]
    type_filter_value = accepted_data[1]

    m2m_categories_data = month_to_month.MonthsComparison(months_filter_value, type=type_filter_value)
    months_data_grouped_by_date_type_and_category = m2m_categories_data.get_months_data_grouped_by_date_type_and_category()
    working_months_data_grouped_by_date_type_and_category = []
    for value in months_data_grouped_by_date_type_and_category:
        if isinstance(value[0], list):
            for sub_value in value:
                working_months_data_grouped_by_date_type_and_category.append(sub_value)
                
    months_data_grouped_by_date_type_and_category_json = json.dumps(working_months_data_grouped_by_date_type_and_category, cls=NpEncoder)


    return(months_data_grouped_by_date_type_and_category_json)

@login_required
@app.route('/get_sub_categories_section_in_analytics', methods=['GET', 'POST'])
def get_sub_categories_section_in_analytics():

    accepted_data = [value for name, value in request.form.to_dict().items()]
    months_filter_value = accepted_data[0]
    type_filter_value = accepted_data[1]
    category_filter_value = accepted_data[2]

    m2m_categories_data = month_to_month.MonthsComparison(months_filter_value, type=type_filter_value, category=category_filter_value)
    months_data_grouped_by_date_type_category_and_sub_category = m2m_categories_data.get_months_data_grouped_by_date_type_category_and_sub_category()
    working_months_data_grouped_by_date_type_category_and_sub_category = []
    for value in months_data_grouped_by_date_type_category_and_sub_category:
        if isinstance(value[0], list):
            for sub_value in value:
                working_months_data_grouped_by_date_type_category_and_sub_category.append(sub_value)
                
    months_data_grouped_by_date_type_category_and_sub_category_json = json.dumps(working_months_data_grouped_by_date_type_category_and_sub_category, cls=NpEncoder)

    return(months_data_grouped_by_date_type_category_and_sub_category_json)



class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


#flash messages handler
def succesfull_message_budget(action, **kwargs):
    if action == 'submit':
        flash("Request submitted succesfully with \n\n name: " + kwargs["name"] + "\n\n and value: " + str(kwargs["value"] + " PLN."))
        return redirect(url_for('expenses_main'))
    elif action == 'delete':
        flash("Record deleted succesfully.")
        return redirect(url_for('show_db_state'))
    elif action == 'modify':
        flash("Record modified succesfully.")

def succesfull_message_types(action, name):
    if action == 'submit':
        flash("Request submitted succesfully with \n\n name: " + name)
        return redirect(url_for('show_db_types'))
    elif action == 'delete':
        flash("Record deleted succesfully")
        return redirect(url_for('show_db_types'))

def succesfull_message_categories(action, name, type):
    if action == 'submit':
        flash("Request submitted succesfully with \n\n name: " + name)
        return redirect(url_for('show_db_categories', type=type))
    elif action == 'delete':
        flash("Record deleted succesfully")
        return redirect(url_for('show_db_categories', type=type))

def succesfull_message_sub_categories(action, name, category, type):
    if action == 'submit':
        flash("Request submitted succesfully with \n\n name: " + name)
        return redirect(url_for('show_db_sub_categories', category=category, type=type))
    elif action == 'delete':
        flash("Record deleted succesfully")
        return redirect(url_for('show_db_sub_categories', category=category, type=type))

def succesfull_message_assignment_rule(action, keyword):
    if action == 'submit':
        flash("Request submitted succesfully with \n\n keyword: " + keyword)
        return redirect(url_for('show_db_assignment_rules'))
    elif action == 'delete':
        flash("Record deleted succesfully")
        return redirect(url_for('show_db_assignment_rules'))
    
def succesfull_filters(active_filters):
    filters_message = 'Filters, '
    for key, value in active_filters.items():
        filters_message += key + ": " + str(value) + ", "
    filters_message = filters_message[:-1] + " have been applied"
    flash(filters_message)




#insert records to DB
def insert_to_budget_db(input_uuid, expense_name, expense_value, expense_category, expense_sub_category, expense_type, expense_date):
    db.BudgetDB.insert_row(input_uuid, expense_name, expense_value, expense_category, expense_sub_category, expense_type, expense_date, clear_db='N')

def insert_to_types_db(type_name):
    db.TypesDB.insert_row(type_name, clear_db='N')

def insert_to_categories_db(category_name, type):
    db.CategoriesDB.insert_row(category_name, type, clear_db='N')

def insert_to_sub_categories_db(type, category, sub_category_name):
    db.SubCategoriesDB.insert_row(type, category, sub_category_name, clear_db='N')


class InputForm:

    #budget input form
    def main_input_form():
        expense_name =  request.form.get("expense_name")
        expense_value_type = str(request.form.get("expense_value_type"))
        expense_value = expense_value_type + request.form.get("expense_value")
        expense_category = request.form.get("expense_category")
        expense_sub_category = request.form.get("expense_sub_category")
        expense_type = request.form.get("expense_type") 
        expense_date = request.form.get("expense_date")
        input_uuid = str(uuid.uuid4())

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
            insert_to_budget_db(input_uuid, expense_name, expense_value, expense_category, expense_sub_category, expense_type, expense_date)
            return succesfull_message_budget('submit', name=expense_name, value=expense_value)
        else:
            return render_template("single_input_from.html", validity_class_name="form-control is-invalid", validity_class_value="form-control is-invalid", \
                invalid_feedback_name=invalid_feedback_name, invalid_feedback_value=invalid_feedback_value, \
                    input_form_buttom="nav-link active", current_budget_button="nav-link", categories_button = "nav-link", analytics_button = "nav-link", assignment_rules_button = "nav-link", \
                        categories=[], sub_categories=[])

    #type input form
    def type_input_form():
        type_name =  request.form.get("type_name")
        typeValidator = InputFormValidation(type_name, "type_name")

        # name field validation
        if typeValidator.check_length() is False:
            invalid_feedback_category = "Category needs to have at least 3 characters."
            category_boolean = False
        else:
            invalid_feedback_category = ""
            category_boolean = True

        if typeValidator.check_name_existance() is False:
            invalid_feedback_category = "Type name already exists - duplicated names are not allowed."
            category_boolean = False

        # summary validation condition    
        if category_boolean is True:
            insert_to_types_db(type_name)
            return succesfull_message_types('submit', type_name)
        else:
            flash("Type hasn't been submitted. " + invalid_feedback_category + " Please re-submit the type.")
            return redirect(url_for('show_db_types'))


    #category input form
    def category_input_form(type):
        category_name =  request.form.get("category_name")
        categoryValidator = InputFormValidation(category_name, "category_name", type=type)

        # name field validation
        if categoryValidator.check_length() is False:
            invalid_feedback_category = "Category needs to have at least 3 characters."
            category_boolean = False
        else:
            invalid_feedback_category = ""
            category_boolean = True

        if categoryValidator.check_name_existance() is False:
            invalid_feedback_category = "Category name already exists - duplicated names are not allowed."
            category_boolean = False

        # summary validation condition    
        if category_boolean is True:
            insert_to_categories_db(category_name, type)
            return succesfull_message_categories('submit', category_name, type)
        else:
            flash("Category hasn't been submitted. " + invalid_feedback_category + " Please re-submit the category.")
            return redirect(url_for('show_db_categories', type=type))
            
    #sub_category input form
    def sub_category_input_form(category, type):
        sub_category_name =  request.form.get("sub_category_name")
        sub_categoryValidator = InputFormValidation(sub_category_name, "sub_category_name", category=category, type=type)

        # name field validation
        if sub_categoryValidator.check_length() is False:
            invalid_feedback_sub_category = "Sub-category needs to have at least 3 characters."
            sub_category_boolean = False
        else:
            invalid_feedback_sub_category = ""
            sub_category_boolean = True

        if sub_categoryValidator.check_name_existance() is False:
            invalid_feedback_sub_category = "Sub-category name already exists - duplicated names are not allowed."
            sub_category_boolean = False

        # summary validation condition    
        if sub_category_boolean is True:
            insert_to_sub_categories_db(type, category, sub_category_name)
            return succesfull_message_sub_categories('submit', sub_category_name, category, type)
        else:
            flash("Sub-category hasn't been submitted. " + invalid_feedback_sub_category + " Please re-submit the sub-category.")
            return redirect(url_for('show_db_sub_categories', category=category, type=type))

    #assignment_rule input form
    def assignment_rule_input_form():
        assignment_rule_uuid = str(uuid.uuid4())
        keyword = request.form.get('key_word_name')
        type = request.form.get('expense_type')
        category = request.form.get('expense_category')
        sub_category = request.form.get('expense_sub_category')

        assignment_rule_validator = AssignmentRuleValidator(keyword, type, category, sub_category)
        invalid_feedback_assignment_rule = []

        #keyword validation
        if not assignment_rule_validator.check_name_existance():
            invalid_feedback_assignment_rule.append("Assignment rule keyword already exists - duplicated keywords are not allowed.")

        if not assignment_rule_validator.check_type_existance():
            invalid_feedback_assignment_rule.append("Assignment rule type doesn't exists - rule needs to be created on existing type.")

        if not assignment_rule_validator.check_category_existance():
            invalid_feedback_assignment_rule.append("Assignment rule category doesn't exists - rule needs to be created on existing category.")

        if not assignment_rule_validator.check_sub_category_existance():
            invalid_feedback_assignment_rule.append("Assignment rule sub_category doesn't exists for category " + category + " - rule needs to be created on existing category & sub_category.")
                
        if not assignment_rule_validator.check_length(keyword):
            invalid_feedback_assignment_rule.append("Keyword needs to have at least 3 characters.")

        if not assignment_rule_validator.check_length(type):
            invalid_feedback_assignment_rule.append("Type needs to have at least 3 characters.")

        if not assignment_rule_validator.check_length(category):
            invalid_feedback_assignment_rule.append("Category needs to have at least 3 characters.")

        if not assignment_rule_validator.check_length(sub_category):
            invalid_feedback_assignment_rule.append("Sub_category needs to have at least 3 characters.")

        if len(invalid_feedback_assignment_rule) == 0:
            db.CategoriesAssignment.insert_row(assignment_rule_uuid, keyword, type, category, sub_category)
            return succesfull_message_assignment_rule('submit', keyword)
        else:
            flash("Assignment rule hasn't been submitted. " + str(invalid_feedback_assignment_rule) + " Please re-submit the assignment rule.")
            return redirect(url_for('show_db_assignment_rules'))

class Filters:

    #budget filters
    def budget_filters(active_filters):
        budgetFiltersValidator = BudgetFiltersValidation(active_filters)
        # dates filters field validation
        if active_filters['date_from']:
            if budgetFiltersValidator.compare_dates() is False:
                invalid_feedback_category = ("'Date From' needs to be smaller or equal 'Date To'")
                budget_filters_boolean = False
            else:   
                invalid_feedback_category = ""
                budget_filters_boolean = True
        else:   
                invalid_feedback_category = ""
                budget_filters_boolean = True

        # summary validation condition    
        if budget_filters_boolean is True:
            return True
        else:
            flash("Filters haven't been applied. " + invalid_feedback_category + ". Please correct filters.")


    def get_active_filters(filters):
        active_filters = {}
        for key, value in filters.items():
            if isstring(value):
                if value != '':
                    active_filters.update({key : value})
            elif isinstance(value, list):
                if len(value) > 0 and value[0] != 'Nothing selected':
                    active_filters.update({key : value})
        return(active_filters)


    def define_optional_filters(filters):

        if "category_filter" in filters.keys():
            if len(filters["category_filter"]) > 0:
                category_filter = str(filters["category_filter"])[1:-1].replace(" ", "").replace("'", "")
            else:
                category_filter = 'Nothing selected'
        else: 
            category_filter = 'Nothing selected'

        if "sub_category_filter" in filters.keys():
            if len(filters["sub_category_filter"]) > 0:
                sub_category_filter = str(filters["sub_category_filter"])[1:-1].replace(" ", "").replace("'", "")
            else:
                sub_category_filter = 'Nothing selected'
        else: 
            sub_category_filter = 'Nothing selected'

        if "type_filter" in filters.keys():
            if len(filters["type_filter"]) > 0:
                type_filter = str(filters["type_filter"])[1:-1].replace(" ", "").replace("'", "")
            else:
                type_filter = 'Nothing selected'
        else: 
            type_filter = 'Nothing selected'
        
        return([category_filter, sub_category_filter, type_filter])

#main application handler
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
