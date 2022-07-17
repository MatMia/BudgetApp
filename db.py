import sqlite3

class BudgetDB:

    def insert_row(name, value, **kwargs):

        con = sqlite3.connect('example.db')
        cur = con.cursor()

        if 'clear_db' in kwargs and kwargs['clear_db'] == 'Y':
            cur.execute('''DROP TABLE IF EXISTS budget''')

            cur.execute('''CREATE TABLE budget
                        (name, value)''')

        cur.execute("INSERT INTO budget VALUES (?, ?)", (name,value))
        con.commit()

        # for row in cur.execute('SELECT * FROM budget'):
        #     print(row)

        con.close()

    def show_db():
        con = sqlite3.connect('example.db')
        cur = con.cursor()

        db_results = []

        for row in cur.execute('''SELECT * FROM budget
            ORDER BY name'''):
            db_results.append(row)

        con.close()
        
        return db_results

    def delete_record(name):
        print(name)
        con = sqlite3.connect('example.db')
        cur = con.cursor()

        cur.execute('''DELETE FROM budget 
        WHERE name = ?''', (name,))
        con.commit()
        con.close()