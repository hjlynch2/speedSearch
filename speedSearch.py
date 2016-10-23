from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL
import sys

app = Flask(__name__)


mysql = MySQL(app)
app.config['MYSQL_USER'] = 'wcrasta2'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'SpeedSearch'
app.config['MYSQL_HOST'] = 'fa16-cs411-10.cs.illinois.edu'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/LogIn', methods=['GET', 'POST'])
def login():
    invalid = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        query = 'SELECT * FROM Users WHERE username = "' + \
            username + '" AND password = "' + password + '" LIMIT 1'
        cur = mysql.connection.cursor()
        cur.execute(query)
        validLogin = cur.rowcount
        cur.close()
        if validLogin:  # valid credentials
            return redirect(url_for('game', username=username))
        else:
            invalid = True
    return render_template('login.html', invalid=invalid)


@app.route('/CreateAccount', methods=['GET', 'POST'])
def createAccount():
    alreadyExists = False
    invalidPassword = False
    cur = mysql.connection.cursor()
    conn = mysql.connection
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(password) < 6:
            invalidPassword = True
        query = 'SELECT * FROM Users WHERE username = "' + username + '"'
        cur.execute(query)
        alreadyExists = cur.rowcount
        if not (alreadyExists or invalidPassword):
            query = 'INSERT INTO Users (username, password, admin) VALUES ("' + \
                username + '","' + password + '",0)'
            cur.execute(query)
            conn.commit()
            cur.close()
            return redirect(url_for('game', username=username))
    cur.close()
    return render_template('createAccount.html', alreadyExists=alreadyExists, invalidPassword=invalidPassword)


@app.route('/Game', methods=['GET', 'POST'])
def game():
    username = request.args['username']
    query = """SELECT admin FROM Users WHERE username='{}'""".format(username)
    cur = mysql.connection.cursor()
    cur.execute(query)
    results = cur.fetchone()
    admin = results[0]
    cur.close()
    return render_template('game.html', username=username, admin=admin)


@app.route('/Users')
def get_users():
    cur = mysql.connection.cursor()
    query = 'SELECT user_id, username FROM Users'
    cur.execute(query)
    users = cur.fetchall()
    print users
    cur.close()
    return users

@app.route('/Users/getUserInfo')
def get_user_info(user_id):
    cur = mysql.connection.cursor()
    query = 'SELECT username, password, admin FROM Users WHERE user_id = ' + user_id
    cur.execute(query)
    userInfo = cur.fetchall()
    cur.close()
    return userInfo

@app.route('/Admin', methods=['GET','POST'])
@app.route('/Admin', methods=['GET', 'POST'])
def admin():
    users = get_users()
    return render_template('admin.html', users = users)


@app.route('/Admin/Select', methods=['GET','POST'])
def adminSelect():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        operation = request.form['operationSelection']
        user_id = request.form['userSelection']
        if operation == "delete":
            cur.close()
            return redirect(url_for('adminDelete', user_id=user_id))
        else:
            return redirect(url_for('adminUpdate', user_id = user_id))
    else:
        cur.close()
        users = get_users()
        return redirect(url_for('admin', users = users))


@app.route('/Admin/Delete', methods=['GET','POST'])
def adminDelete():
    user_id = request.args['user_id']
    return render_template('deleteUser.html', user_id = user_id)


@app.route('/Admin/Update', methods=['GET','POST'])
def adminUpdate():
    # if request = post
    # else
    '''
    user_id = request.args['user_id']
    userInfo = get_user_info(user_id)
    return render_template('updateUser.html', userInfo = userInfo)

    cur.execute(SELECT * FROM testing)
    rv = cur.fetchall()
    cur.close()
    return str(rv)
    '''
    return None


@app.route('/SampleQuery', methods=['GET','POST'])
def sampleQuery():
    cur = mysql.connection.cursor()
    conn = mysql.connection
    admins = None
    query = ""
    if request.method == 'POST':
        username = request.form['username']
        query = 'SELECT user_id, username FROM Users WHERE username LIKE "%' + username + '%" AND admin = 1'
        cur.execute(query)
        admins = cur.fetchall()
        cur.close()
    return render_template('sampleQuery.html', admins = admins, query=query)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
