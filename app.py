from flask import Flask, render_template, g, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

# make sure to install flask with pip

# sqlite db instructions
# Install sqlite3 on Windows: winget install -e --id SQLite.SQLite
# Run this if you are on Windows Powershell Terminal to create the DB file: type .\food_tracker.sql | sqlite3 food_log.db 
# On linux this should work: sqlite3 food_log.db < food_tracker.sql
# Need to run above to create the food_log.db database 
# make sure the food_log.db is in the same root folder as app.py
def connect_db():
    sql = sqlite3.connect('food_log.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite3_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['POST', 'GET']) 
def index():
    db = get_db()

    if request.method == 'POST':
        date = request.form['date'] 

        dt = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(dt, '%Y%m%d')

        db.execute('insert into log_date (entry_date) values (?)', [database_date])
        db.commit()

    cur = db.execute('select log_date.entry_date, sum(food.protein) as protein, sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat, sum(food.calories) as calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id group by log_date.id order by log_date.entry_date desc')
    results = cur.fetchall()

    date_results = []

    for i in results:
        single_date = {}

        single_date['entry_date'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carbohydrates'] = i['carbohydrates']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']

        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')
        single_date['pretty_date'] = datetime.strftime(d, '%B %d, %Y')

        date_results.append(single_date)


    return render_template('home.html', results=date_results)

@app.route('/view/<date>', methods=['GET', 'POST']) #date for now is 20230901
def view(date):
    db = get_db()

    cur = db.execute('select id, entry_date from log_date where entry_date = ?', [date])
    date_result = cur.fetchone()

    if request.method == 'POST':
        # return '<h1>The food item added is #{}'.format(request.form['food-select'])
        db.execute('insert into food_date (food_id, log_date_id) values (?,?)', [request.form['food-select'], date_result['id']])
        db.commit()

    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')

    # return '<h1>the date is {}</h1>'.format(result['entry_date'])

    food_cur = db.execute('select id, name from food')
    food_results = food_cur.fetchall()

    # initial code - might delete later
    # log_cur = db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id where log_date.entry_date = ?', [date])
    log_cur = db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id where log_date.entry_date = ?', [date])
    log_results = log_cur.fetchall()

    totals = {}
    totals['protein'] = 0
    totals['carbohydrates'] = 0
    totals['fat'] = 0
    totals['calories'] = 0

    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']



    return render_template('day.html', entry_date=date_result['entry_date'], pretty_date=pretty_date, food_results=food_results, log_results=log_results, totals=totals)



@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()

    if request.method == 'POST':
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])
        
        calories = protein * 4 + carbohydrates * 4 + fat * 9

        
        db.execute('insert into food (name, protein, carbohydrates, fat, calories) values (?, ?, ?, ?, ?)', [name, protein, carbohydrates, fat, calories])
        db.commit()

    cur = db.execute('select name, protein, carbohydrates, fat, calories from food')
    results = cur.fetchall()

        # return "Response!"
    return render_template('add_food.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)












# ARCHIVE

# Note - if you get some kind of error it's because the default date is set to 20230901 temporarily, this will be fixed later
# Might delete this block later - error too detailed
# @app.route('/view/<date>', methods=['GET', 'POST'])
# def view(date):
#     db = get_db()

#     cur = db.execute('select id, entry_date from log_date where entry_date = ?', [date])
#     date_result = cur.fetchone()

#     if date_result is None:
#         # Handle the case where the date doesn't exist in the database.
#         # You can redirect to an error page or display a message.
#         return "Date not found in the database."

#     if request.method == 'POST':
#         db.execute('insert into food_date (food_id, log_date_id) values (?, ?)', [request.form['food-select'], date_result['id']])
#         db.commit()

#     d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
#     pretty_date = datetime.strftime(d, '%B %d, %Y')

#     food_cur = db.execute('select id, name from food')
#     food_results = food_cur.fetchall()

#     return render_template('day.html', date=pretty_date, food_results=food_results)