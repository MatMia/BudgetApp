from flask import Flask, flash, request, render_template, session, redirect, url_for
from markupsafe import escape
from .db import BudgetDB
from flask_table import Table, Col


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def expenses_main():
    validity_class_name = "form-control is-invalid"
    validity_class_value = "form-control is-invalid"
    invalid_feedback_name = ""
    invalid_feedback_value = ""
    input_form_buttom = "nav-link active"
    current_budget_button = "nav-link"
    return render_template("index.html", validity_class_name=validity_class_name, validity_class_value=validity_class_value, \
        invalid_feedback_name=invalid_feedback_name, invalid_feedback_value=invalid_feedback_value, \
            input_form_buttom=input_form_buttom, current_budget_button=current_budget_button)

@app.route('/', methods=['GET', 'POST'])
def expense_input():
    if request.form.get("btn") == "submit_form":
        return InputForm.main_input_form()

    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))


@app.route("/db_state")
def show_db_state():
    db_results = ShowBudgetTable.show_budget_table()
    table = db_results[0]
    value_sum = round(db_results[1],2)

    input_form_buttom = "nav-link"
    current_budget_button = "nav-link active"

    return render_template("budget_table.html", table=table, value_sum=value_sum, \
        input_form_buttom=input_form_buttom, current_budget_button=current_budget_button)


@app.route('/db_state', methods=['GET', 'POST'])
def return_to_input():
    if request.form.get("delete_record"):
        BudgetDB.delete_record(request.form.get("delete_record"))
        return succesfull_message('delete')

    elif request.form.get("menu_input_form") == "my_input_form":
        return redirect(url_for('expenses_main'))

    elif request.form.get("menu_current_budget") == "my_current_budget":
        return redirect(url_for('show_db_state'))


def succesfull_message(action, **kwargs):
    if action == 'submit':
        flash("Request submitted succesfully with \n\n name: " + kwargs["name"] + "\n\n and value: " + str(kwargs["value"] + " PLN."))
        return redirect(url_for('expenses_main'))
    elif action == 'delete':
        flash("Record deleted succesfully")
        return redirect(url_for('show_db_state'))


def insert_to_db(expense_name, expense_value):
    BudgetDB.insert_row(expense_name, expense_value, clear_db='N')


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

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
        else:
            return True

    def check_length(self):
        if self.name == "expense_name":
            if len(self.key) > 2:
                return True
            else:
                return False
        else:
            return True

    def validation_summary(self):
        if InputFormValidation.check_type(self) is False:
            invalid_feedback_value = "Value needs to be numeric."
            summary_boolean = False
        else:
            invalid_feedback_value = ""
            summary_boolean = True

        if InputFormValidation.check_length(self) is False:
            invalid_feedback_name = "Name needs to have at least 3 characters."
            summary_boolean = False
        else:
            invalid_feedback_name = ""
        
        return (summary_boolean, invalid_feedback_name, invalid_feedback_value)


class InputForm():

    def main_input_form():
        expense_name =  request.form.get("expense_name")
        expense_value = request.form.get("expense_value")

        nameValidator = InputFormValidation(expense_name, "expense_name")
        valueValidator = InputFormValidation(expense_value, "expense_value")

        validated_name = nameValidator.validation_summary()
        validated_value = valueValidator.validation_summary()

        invalid_feedback_name = validated_name[1]
        invalid_feedback_value = validated_value[2]

        if validated_name[0] is True and validated_value[0] is True:
            insert_to_db(expense_name, expense_value)
            validity_class_name = "form-control is-valid"
            validity_class_value = "form-control is-valid"
            return succesfull_message('submit', name=expense_name, value=expense_value)
        else:
            validity_class_name = "form-control is-invalid"
            validity_class_value = "form-control is-invalid"
            input_form_buttom = "nav-link active"
            current_budget_button = "nav-link"
            return render_template("index.html", validity_class_name=validity_class_name, validity_class_value=validity_class_value, \
                invalid_feedback_name=invalid_feedback_name, invalid_feedback_value=invalid_feedback_value, \
                    input_form_buttom=input_form_buttom, current_budget_button=current_budget_button)


class ItemTable(Table):

    name = Col('expense_name')
    value = Col('expense_value')


class Item(object):

    def __init__(self, name, value):
        self.name = name
        self.value = value

class ShowBudgetTable():

    def show_budget_table():
        db_results = BudgetDB.show_db()
        table_results = []
        value_sum = 0
        for record in db_results:
            value_sum += float(record[1])
            table_results.append(Item(record[0],record[1]))
        table = ItemTable(table_results)
        return (table, value_sum)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)