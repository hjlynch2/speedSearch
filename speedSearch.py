from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

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


@app.route('/Admin', methods=['GET', 'POST'])
def admin():
    return render_template('admin.html')


@app.route('/select')
def select():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM testing''')
    rv = cur.fetchall()
    cur.close()
    return str(rv)


if __name__ == '__main__':
    app.run(debug=True)
