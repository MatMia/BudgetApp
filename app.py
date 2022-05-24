from flask import Flask, flash, request, render_template, session, redirect, url_for
from markupsafe import escape
from wtforms import Form, validators, StringField
from db import BudgetDB
from flask_table import Table, Col, ButtonCol

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def expenses_main():
    form = InputFormValidation(request.form)
    form.expense_name.data = ''
    form.expense_value.data = ''
    return render_template("index.html", form=form)

@app.route('/', methods=['GET', 'POST'])
def expense_input():
    if request.form["btn"] == "submit_form":
        InputForm.main_input_form()
        return succesfull_message('submit')

    elif request.form["btn"] == "show_db":
        return redirect(url_for('show_db_state'))

@app.route("/db_state")
def show_db_state():
    table = ShowBudgetTable.show_budget_table()
    return render_template("budget_table.html", table=table)

@app.route('/db_state', methods=['GET', 'POST'])
def return_to_input():
        if request.form["btn"] == "return_to_input":
            return redirect(url_for('expenses_main'))

@app.route("/remove_record/<name>", methods=['GET', 'POST'])
def delete_record(name):
        BudgetDB.delete_record(name)
        return succesfull_message('delete')

def succesfull_message(action):
    if action == 'submit':
        flash("Request submitted succesfully")
        return redirect(url_for('expenses_main'))
    elif action == 'delete':
        flash("Record deleted succesfully")
        return redirect(url_for('show_db_state'))

def insert_to_db(expense_name, expense_value):
    BudgetDB.insert_row(expense_name, expense_value, clear_db='N')

class InputForm():
        def main_input_form():
            form = InputFormValidation(request.form)
            expense_name = escape(form.expense_name.data)
            expense_value = escape(form.expense_value.data)
            insert_to_db(expense_name, expense_value)

class InputFormValidation(Form):
    expense_value = StringField('expense_value', [validators.Length(min=4, max=25), validators.DataRequired()])
    expense_name = StringField('expense_name', [validators.Length(min=4, max=25), validators.DataRequired()])

class ItemTable(Table):
    name = Col('expense_name')
    value = Col('expense_value')
    delete_button = ButtonCol('Delete', 'delete_record', url_kwargs=dict(name='name'))

class Item(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class ShowBudgetTable():
    def show_budget_table():
        db_results = BudgetDB.show_db()
        table_results = []
        for record in db_results:
            table_results.append(Item(record[0],record[1]))
        table = ItemTable(table_results)
        return table

if __name__ == "__main__":
    app.debug = True
    app.run()