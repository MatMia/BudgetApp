from datetime import datetime
import sqlite3

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

    def show_db(**kwargs):
        con = sqlite3.connect('budget.db')
        cur = con.cursor()

        db_results = []

        if 'limit' in kwargs:
            if 'date_from' in kwargs:
                for row in cur.execute('''SELECT * FROM budget
                    WHERE date BETWEEN ? and ?
                    ORDER BY date LIMIT ? OFFSET ?''', (kwargs['date_from'], kwargs['date_to'], kwargs['limit'], kwargs['offset'])):
                    db_results.append(row)
            else:
                for row in cur.execute('''SELECT * FROM budget
                    ORDER BY date LIMIT ? OFFSET ?''', (kwargs['limit'], kwargs['offset'])):
                    db_results.append(row)

        elif 'pie_chart' in kwargs:
            if 'date_from' in kwargs:
                for row in cur.execute('''SELECT category, round(sum(value),2) FROM budget
                    WHERE date BETWEEN ? and ?
                    GROUP BY category''', (kwargs['date_from'], kwargs['date_to'])):
                    db_results.append(row)
            else:
                for row in cur.execute('''SELECT category, round(sum(value),2) FROM budget
                    GROUP BY category'''):
                    db_results.append(row)

        elif 'sub_cat_pie_chart' in kwargs:
            category = kwargs['sub_cat_pie_chart']

            if 'date_from' in kwargs:
                for row in cur.execute('''SELECT sub_category, round(sum(value),2) FROM budget
                    WHERE category = ? and date BETWEEN ? and ?
                    GROUP BY sub_category''', (category,kwargs['date_from'], kwargs['date_to'])):
                    db_results.append(row)    
            else:
                for row in cur.execute('''SELECT sub_category, round(sum(value),2) FROM budget
                    WHERE category = ?
                    GROUP BY sub_category''', (str(category[0]),)):
                    db_results.append(row)
           

        elif 'date_from' in kwargs:
                for row in cur.execute('''SELECT * FROM budget
                    WHERE date between ? and ?
                    ORDER BY date''', (kwargs['date_from'], kwargs['date_to'])):
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
            if 'date_from' in kwargs:
                for row in cur.execute('''SELECT * FROM budget
                    WHERE category = ? and sub_category = ? and date BETWEEN ? and ?
                    ORDER BY date LIMIT ? OFFSET ?''', (category, sub_category, kwargs['date_from'], kwargs['date_to'], kwargs['limit'], kwargs['offset'])):
                        db_results.append(row[1:])
            else:
                for row in cur.execute('''SELECT * FROM budget
                    WHERE category = ? and sub_category = ?
                    ORDER BY date LIMIT ? OFFSET ?''', (category, sub_category, kwargs['limit'], kwargs['offset'])):
                        db_results.append(row[1:])      
        elif 'date_from' in kwargs:
            for row in cur.execute('''SELECT * FROM budget
                WHERE category = ? and sub_category = ? and date BETWEEN ? and ?
                ORDER BY date''', (category, sub_category, kwargs['date_from'], kwargs['date_to'])):
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

    def show_db(type, category):
        con = sqlite3.connect('sub_categories.db')
        cur = con.cursor()

        db_results = []

        for row in cur.execute('''SELECT sub_category FROM sub_categories
            WHERE type = ? and category = ?
            ORDER BY sub_category''', (type, category)):
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