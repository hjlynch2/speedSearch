from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)


mysql = MySQL(app)
app.config['MYSQL_USER'] = 'wcrasta2'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'SpeedSearch'
app.config['MYSQL_HOST'] = 'fa16-cs411-10.cs.illinois.edu'
app.secret_key = '\x9f\x10{\x9aK>\xd39oUBZhB\x11))/\x05J\xf5?\x1f\x80'


@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return redirect(url_for('game'))


@app.route('/login', methods=['GET', 'POST'])
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
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('game'))
        else:
            invalid = True
    return render_template('login.html', invalid=invalid)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signUp():
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
            return redirect(url_for('game'))
    cur.close()
    return render_template('createAccount.html', alreadyExists=alreadyExists, invalidPassword=invalidPassword)


@app.route('/game', methods=['GET', 'POST'])
def game():
    username = session.get('username')
    query = """SELECT admin FROM Users WHERE username='{}'""".format(username)
    cur = mysql.connection.cursor()
    cur.execute(query)
    results = cur.fetchone()
    admin = None
    if results:
        admin = results[0]
    cur.close()
    return render_template('game.html', username=username, admin=admin, logged_in=session.get('logged_in'))


@app.route('/users')
def get_users():
    cur = mysql.connection.cursor()
    query = 'SELECT user_id, username FROM Users'
    cur.execute(query)
    users = cur.fetchall()
    cur.close()
    return users


@app.route('/users/getuserinfo')
def get_user_info(user_id):
    cur = mysql.connection.cursor()
    query = 'SELECT user_id, username, admin FROM Users WHERE user_id = ' + user_id
    cur.execute(query)
    userInfo = cur.fetchall()
    cur.close()
    return userInfo


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    users = get_users()
    cur = mysql.connection.cursor()
    username = session.get('username')
    admin = 0
    if username:
        query = """SELECT admin FROM Users WHERE username='{}'""".format(username)
        cur.execute(query)
        result = cur.fetchone()
        if result:
            admin = result[0]
        cur.close()
    if admin:
        return render_template('admin.html', users=users)
    else:
        return redirect(url_for('index'))


@app.route('/admin/select', methods=['GET', 'POST'])
def adminSelect():
    if request.method == 'POST':
        operation = request.form['operation']
        user_id = request.form['user']
        if operation == "delete":
            return redirect(url_for('adminDelete', user_id=user_id))
        else:
            return redirect(url_for('adminEdit', user_id=user_id))
    else:
        users = get_users()
        return redirect(url_for('admin', users=users))


@app.route('/admin/delete', methods=['GET', 'POST'])
def adminDelete():
    if request.method == 'POST':
        toDelete = request.form['delete']
        if toDelete == 'no':
            return redirect(url_for('admin'))
        else:
            user_id = request.form['user_id']
            cur = mysql.connection.cursor()
            conn = mysql.connection
            query = 'DELETE FROM Users Where user_id = ' + user_id
            cur.execute(query)
            conn.commit()
            cur.close()
            return redirect(url_for('admin'))
    else:
        user_id = request.args['user_id']
        user_info = get_user_info(user_id)
        return render_template('deleteUser.html', user_info=user_info[0])


@app.route('/admin/edit', methods=['GET', 'POST'])
def adminEdit():
    if request.method == 'POST':
        newAdmin = request.form['adminRights']
        user_id = request.form['user_id']
        cur = mysql.connection.cursor()
        conn = mysql.connection
        if newAdmin == 'no':
            query = 'UPDATE Users SET admin = 0 WHERE user_id = ' + user_id
            cur.execute(query)
            conn.commit()
            cur.close()
            return redirect(url_for('admin'))
        else:
            query = 'UPDATE Users SET admin = 1 WHERE user_id = ' + user_id
            cur.execute(query)
            conn.commit()
            cur.close()
            return redirect(url_for('admin'))
    else:
        user_id = request.args['user_id']
        user_info = get_user_info(user_id)
        return render_template('updateUser.html', user_info=user_info[0])


@app.route('/samplequery', methods=['GET', 'POST'])
def sampleQuery():
    cur = mysql.connection.cursor()
    admins = None
    query = ""
    if request.method == 'POST':
        username = request.form['username']
        query = 'SELECT user_id, username FROM Users WHERE username LIKE "%' + username + '%" AND admin = 1'
        cur.execute(query)
        admins = cur.fetchall()
        cur.close()
    return render_template('sampleQuery.html', admins=admins, query=query)


@app.route('/highscores', methods=['GET'])
def highscores():
    cur = mysql.connection.cursor()
    query = """ SELECT u.username, score, s.game_id
                FROM Scores s
                JOIN Users u ON s.user_id = u.user_id
                ORDER BY s.score ASC;"""
    cur.execute(query)
    scores = cur.fetchall()
    cur.close()
    return render_template('highscores.html', scores=scores)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
