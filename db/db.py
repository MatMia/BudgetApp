import sqlite3

class LoginDB:

    def __init__(self) -> None:
        pass

    def authenticate_login(username: str, password: str) -> bool:
        
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        
        cur.execute('''SELECT * FROM users WHERE 
                    username = ? and password = ?''', (username, password))
        
        if not cur.fetchone():
            return False
        else:
            return True
        
    def add_new_user(self, username: str, password: str) -> bool:

        con = sqlite3.connect('users.db')
        cur = con.cursor()
        
        cur.execute('''INSERT INTO users VALUES (?,?)''', (username, password))
        con.commit()
        con.close()

        return self.authenticate_login(username, password)
    
    def validate_new_user_credentials(self, username: str, password: str) -> bool:
        if 6 < len(password) < 20:
            return True
        else:
            return False
        
    def check_user_existance(self,username: str) -> bool:
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        
        cur.execute('''SELECT * FROM users WHERE 
                    username = ?''', (username,))
        
        if cur.fetchone():
            return False
        else:
            return True

        
 
class BudgetDB:

    def insert_row(input_uuid, name, value, category, sub_category, expense_type, date, **kwargs):

        con = sqlite3.connect('budget.db')
        cur = con.cursor()

        if 'clear_db' in kwargs and kwargs['clear_db'] == 'Y':
            cur.execute('''DROP TABLE IF EXISTS budget''')

            cur.execute('''CREATE TABLE budget
                        (id TEXT, name TEXT, value REAL, category TEXT, sub_category TEXT, expense_type TEXT, date TEXT)''')

        cur.execute("INSERT INTO budget VALUES (?, ?, ?, ?, ?, ?, strftime(?))", (input_uuid, name, value, category, sub_category, expense_type, date))
        con.commit()
        con.close()

    def clear_db():
        con = sqlite3.connect('budget.db')
        cur = con.cursor()

        cur.execute('''DROP TABLE IF EXISTS budget''')

        cur.execute('''CREATE TABLE budget
                    (id TEXT, name TEXT, value REAL, category TEXT, sub_category TEXT, expense_type TEXT, date TEXT)''')
                    
        con.commit()
        con.close()


    def get_filters_parameters(active_filters):
        where_criteria = ' WHERE '

        if 'date_from' in active_filters:
            where_criteria += "date between '" + active_filters['date_from'] + "' and '" + active_filters['date_to'] + "' "

        if 'category_filter' in active_filters:
            category_filters = str(active_filters['category_filter'])[1:-1]
            if where_criteria == ' WHERE ':
                where_criteria += "category in (" + category_filters + ") "
            else:
                where_criteria += "and category in (" + category_filters + ") "

        if 'sub_category_filter' in active_filters:
            sub_category_filters = str(active_filters['sub_category_filter'])[1:-1]
            if where_criteria == ' WHERE ':
                where_criteria += "sub_category in (" + sub_category_filters + ") "
            else:
                where_criteria += "and sub_category in (" + sub_category_filters + ") "

        if 'type_filter' in active_filters:
            type_filters = str(active_filters['type_filter'])[1:-1]
            if where_criteria == ' WHERE ':
                where_criteria += "expense_type in (" + type_filters + ") "
            else:
                where_criteria += "and expense_type in (" + type_filters + ") "

        print(where_criteria)
        return(where_criteria)

    def show_db(**kwargs):
        con = sqlite3.connect('budget.db')
        cur = con.cursor()

        db_results = []

        if 'limit' in kwargs:
            if 'active_filters' in kwargs:
                where_criteria = BudgetDB.get_filters_parameters(kwargs['active_filters'])
                for row in cur.execute('''SELECT * FROM budget'''
                    + where_criteria + 
                    '''ORDER BY date LIMIT ? OFFSET ?''', (kwargs['limit'], kwargs['offset'])):
                    db_results.append(row)
            else:
                for row in cur.execute('''SELECT * FROM budget
                    ORDER BY date LIMIT ? OFFSET ?''', (kwargs['limit'], kwargs['offset'])):
                    db_results.append(row)

        elif 'pie_chart' in kwargs:
            if 'active_filters' in kwargs:
                where_criteria = BudgetDB.get_filters_parameters(kwargs['active_filters'])
                for row in cur.execute('''SELECT category, round(sum(value),2) FROM budget'''
                    + where_criteria + 
                    '''GROUP BY category'''):
                    db_results.append(row)
            else:
                for row in cur.execute('''SELECT category, round(sum(value),2) FROM budget
                    GROUP BY category'''):
                    db_results.append(row)

        elif 'sub_cat_pie_chart' in kwargs:
            category = kwargs['sub_cat_pie_chart']

            if 'active_filters' in kwargs:
                where_criteria = BudgetDB.get_filters_parameters(kwargs['active_filters'])
                for row in cur.execute('''SELECT sub_category, round(sum(value),2) FROM budget'''
                    + where_criteria + 
                    ''' and category = ?
                    GROUP BY sub_category''', (category,)):
                    db_results.append(row)    
            else:
                for row in cur.execute('''SELECT sub_category, round(sum(value),2) FROM budget
                    WHERE category = ?
                    GROUP BY sub_category''', (str(category[0]),)):
                    db_results.append(row)
           

        elif 'active_filters' in kwargs:
            where_criteria = BudgetDB.get_filters_parameters(kwargs['active_filters'])
            for row in cur.execute('''SELECT * FROM budget'''
                + where_criteria + 
                '''ORDER BY date'''):
                db_results.append(row)

        else:
            for row in cur.execute('''SELECT * FROM budget
                ORDER BY date'''):
                db_results.append(row)

        con.close()
        return db_results


    def sub_category_data_table(category, sub_category, **kwargs):
        con = sqlite3.connect('budget.db')
        cur = con.cursor()

        db_results = []
        
        if 'limit' in kwargs:
            if 'active_filters' in kwargs:
                where_criteria = BudgetDB.get_filters_parameters(kwargs['active_filters'])
                for row in cur.execute('''SELECT * FROM budget'''
                    + where_criteria + 
                    ''' and category = ? and sub_category = ?
                    ORDER BY date LIMIT ? OFFSET ?''', (category, sub_category, kwargs['limit'], kwargs['offset'])):
                    db_results.append(row[1:])
            else:
                for row in cur.execute('''SELECT * FROM budget
                    WHERE category = ? and sub_category = ?
                    ORDER BY date LIMIT ? OFFSET ?''', (category, sub_category, kwargs['limit'], kwargs['offset'])):
                        db_results.append(row[1:])   

        elif 'active_filters' in kwargs:
            where_criteria = BudgetDB.get_filters_parameters(kwargs['active_filters'])
            for row in cur.execute('''SELECT * FROM budget'''
                + where_criteria + 
                ''' and category = ? and sub_category = ?
                ORDER BY date''', (category, sub_category)):
                    db_results.append(row)
        else:
            for row in cur.execute('''SELECT * FROM budget
                WHERE category = ? and sub_category = ? 
                ORDER BY date''', (category, sub_category)):
                    db_results.append(row)

        con.close()
        return db_results



    def delete_record(delete_id):
        print(delete_id)
        con = sqlite3.connect('budget.db')
        cur = con.cursor()

        cur.execute('''DELETE FROM budget 
        WHERE id = ?''', (delete_id,))
        con.commit()
        con.close()


class TypesDB:
    def insert_row(type, **kwargs):

        con = sqlite3.connect('types.db')
        cur = con.cursor()

        if 'clear_db' in kwargs and kwargs['clear_db'] == 'Y':
            cur.execute('''DROP TABLE IF EXISTS types''')

            cur.execute('''CREATE TABLE types
                        (name)''')

        cur.execute("INSERT INTO types VALUES (?)", (type,))
        con.commit()
        con.close()

    def show_db():
        con = sqlite3.connect('types.db')
        cur = con.cursor()

        db_results = []

        for row in cur.execute('''SELECT * FROM types
            ORDER BY name'''):
            db_results.append(row)

        con.close()
        
        return db_results

    #delete required type and all connected categories
    def delete_record(type):

        #delete type
        con = sqlite3.connect('types.db')
        cur = con.cursor()

        cur.execute('''DELETE FROM types 
        WHERE name = ?''', (type,))
        con.commit()
        con.close()

        #delete corresponding categories

        con = sqlite3.connect('categories.db')
        cur = con.cursor()

        cur.execute('''DELETE FROM categories 
        WHERE type = (?)''', (type,))
        con.commit()
        con.close()

        #delete corresponding sub_categories

        con = sqlite3.connect('sub_categories.db')
        cur = con.cursor()

        cur.execute('''DELETE FROM sub_categories 
        WHERE type = (?)''', (type,))
        con.commit()
        con.close()

class CategoriesDB:

    def insert_row(category, type, **kwargs):

        con = sqlite3.connect('categories.db')
        cur = con.cursor()

        if 'clear_db' in kwargs and kwargs['clear_db'] == 'Y':
            cur.execute('''DROP TABLE IF EXISTS categories''')

            cur.execute('''CREATE TABLE categories
                        (name TEXT, type TEXT)''')

        cur.execute("INSERT INTO categories VALUES (?,?)", (category,type))
        con.commit()
        con.close()

    def show_db(**kwargs):
        con = sqlite3.connect('categories.db')
        cur = con.cursor()

        db_results = []

        if 'type' in kwargs:
            for row in cur.execute('''SELECT * FROM categories
                WHERE type = (?)
                ORDER BY name''', (kwargs['type'],)):
                db_results.append(row)
        else:
            for row in cur.execute('''SELECT * FROM categories
                ORDER BY name'''):
                db_results.append(row) 

        con.close()
        
        return db_results

    #delete required category and all connected sub-categories
    def delete_record(category, type):

        #delete category
        con = sqlite3.connect('categories.db')
        cur = con.cursor()

        cur.execute('''DELETE FROM categories 
        WHERE name = ? and type = ?''', (category, type))
        con.commit()
        con.close()

        con = sqlite3.connect('sub_categories.db')
        cur = con.cursor()

        #delete sub-categories
        cur.execute('''DELETE FROM sub_categories 
        WHERE category = (?)''', (category,))
        con.commit()
        con.close()

class SubCategoriesDB:

    def insert_row(type, category, sub_category, **kwargs):

        con = sqlite3.connect('sub_categories.db')
        cur = con.cursor()

        if 'clear_db' in kwargs and kwargs['clear_db'] == 'Y':
            cur.execute('''DROP TABLE IF EXISTS sub_categories''')

            cur.execute('''CREATE TABLE sub_categories
                        (category, sub_category, type)''')

        cur.execute("INSERT INTO sub_categories VALUES (?, ?, ?)", (category, sub_category, type))
        con.commit()
        con.close()

    def show_db(**kwargs):
        con = sqlite3.connect('sub_categories.db')
        cur = con.cursor()

        db_results = []

        if "type" in kwargs:
            for row in cur.execute('''SELECT sub_category FROM sub_categories
                WHERE type = ? and category = ?
                ORDER BY sub_category''', (kwargs["type"], kwargs["category"])):
                db_results.append(row)
        else:
            for row in cur.execute('''SELECT sub_category FROM sub_categories
                ORDER BY sub_category'''):
                db_results.append(row)

        con.close()
        
        return db_results

    def delete_record(type, category, sub_category):
        con = sqlite3.connect('sub_categories.db')
        cur = con.cursor()

        cur.execute('''DELETE FROM sub_categories 
        WHERE type = ? and category = ? and sub_category = ?''', (type, category, sub_category))
        con.commit()
        con.close()


class Analytics():

    def get_grouped_data_by_date_and_type(required_months_where_criteria):
        con = sqlite3.connect('budget.db')
        cur = con.cursor()

        required_data = []

        for row in cur.execute('''SELECT strftime('%Y-%m', date) as formatted_date, expense_type, round(sum(value),2) FROM budget
        WHERE ''' + required_months_where_criteria + ''' GROUP BY formatted_date, expense_type'''):
            required_data.append(row)

        con.commit()
        con.close()

        return(required_data)


    def get_grouped_data_by_date_type_and_category(required_months_where_criteria):
        con = sqlite3.connect('budget.db')
        cur = con.cursor()

        required_data = []

        for row in cur.execute('''SELECT strftime('%Y-%m', date) as formatted_date, expense_type, category, round(sum(value),2) FROM budget
        WHERE ''' + required_months_where_criteria + ''' GROUP BY formatted_date, expense_type, category'''):
            required_data.append(row)

        con.commit()
        con.close()

        return(required_data)

    def get_grouped_data_by_date_type_category_and_sub_category(required_months_where_criteria):
        con = sqlite3.connect('budget.db')
        cur = con.cursor()

        required_data = []
        print(required_months_where_criteria)
        for row in cur.execute('''SELECT strftime('%Y-%m', date) as formatted_date, expense_type, category, sub_category, round(sum(value),2) FROM budget
        WHERE ''' + required_months_where_criteria + ''' GROUP BY formatted_date, expense_type, category, sub_category'''):
            required_data.append(row)

        con.commit()
        con.close()

        return(required_data)