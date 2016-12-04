from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import random
import traceback
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

EASY = 0
MEDIUM = 1
HARD = 2


app = Flask(__name__)


mysql = MySQL(app)
app.config['MYSQL_USER'] = 'wcrasta2'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'SpeedSearch'
app.config['MYSQL_HOST'] = 'fa16-cs411-10.cs.illinois.edu'
app.secret_key = '\x9f\x10{\x9aK>\xd39oUBZhB\x11))/\x05J\xf5?\x1f\x80'

score = 0


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


@app.route('/creategame', methods=['GET'])
def createGame():
    # return in the raw unicode
    session['score'] = 0
    start = getStartPage()
    end = getEndPage(start, dist=5)

    start_title = getPageTitle(start)
    end_title = getPageTitle(end)

    session['start_id'] = start
    session['end_id'] = end
    session['start_title'] = start_title
    session['end_title'] = end_title

    return render_template('createGame.html', start_game=start_title.encode('utf-8'), end_game=end_title.encode('utf-8'), s=start)

# getting endpage with difficulty parameter
def getEndPageHelper(start, difficulty):
    if difficulty == EASY:
        return getEndPage(start, dist = 3)
    elif difficulty == MEDIUM:
        return getEndPage(start, dist = 5)
    elif difficulty == HARD:
        return getEndPage(start, dist = 7)
    else:
        return getEndPage(start, dist = 3)


def insertGameIfNew(start,end, difficulty):
    cur = mysql.connection.cursor()
    query = """ SELECT COUNT(*) FROM Games WHERE source = %s AND end = %s """ % (start, end)
    cur.execute(query)
    num = cur.fetchone()[0]
    cur.close()
    if int(num) == 0:
        insertGame(start, end, difficulty)

def insertGame(start, end, difficulty):
    cur = mysql.connection.cursor()
    dist = 3
    if difficulty == EASY: dist = 3
    elif difficulty == MEDIUM: dist = 5
    elif difficulty == HARD: dist = 7
    insert_query = """INSERT INTO Games(source,destination,difficulty,optimal_score,rating) VALUES (%s,%s,%s,%s,%s,%s)"""
    insert_query = query % (start,end,difficulty,dist,5)
    cur.execute(insert_query)
    cur.close()


def fetch_page(page_title):
    next_page = 0
    valid = True
    try:
        cur = mysql.connection.cursor()
        page_query = """ Select page_id from page where page_title = \"%s\" """ % (page_title)
        cur.execute(page_query)
        print "fetched page " + str(page_title)
        print "fetched pages: " + str(cur.rowcount)
        result = cur.fetchone()
        if result is None:
            return (0, True, True)  # deadend, page not in table
        next_page = result[0]
    except Exception:
        next_page = -1
        valid = False
        traceback.print_exc()
    finally:
        cur.close()
        return (next_page, valid, False)


@app.route('/chooseDifficulty', methods=['GET', 'POST'])
def chooseDifficulty():
    if request.method == 'POST':
        difficulty = request.form['difficulty']
        session['difficulty'] = int(difficulty)
        return redirect(url_for('createGame'))
    else:
        return render_template('chooseDifficulty.html')


@app.route('/play', methods=['GET', 'POST'])
def play():
    if request.method == 'POST':
        cur = mysql.connection.cursor()

        if request.form['starting'] == '1':
            next_page = session['start_id']
            next_page_title = session['start_title']
        else:
            next_page_title = request.form['next_page_title']
            session['score'] = session['score'] + 1
            # get next page id
            next_page, valid, deadend = fetch_page(next_page_title)
            if not valid:
                return "page not valid - db error todo"
            if deadend:
                return deadEnd()

        print "next page: " + str(next_page)
        print next_page_title
        print "end_id: " + str(session['end_id'])
        print session['end_title']

        # game is over, create a new game - replace this later
        if next_page == session['end_id']:
            return endGame()

        curr_page = request.form['curr_page']
        curr_page_title = request.form['curr_page_title']

        prev_page = request.form['prev_page']
        prev_page_title = request.form['prev_page_title']

        # get links for next page
        links = getNeighbors(next_page)
        cur.close()

        if len(links) == 0:
            return deadEndGen(next_page_title)

        return render_template('play.html', curr_page=next_page, curr_page_title=next_page_title.encode('utf-8'), prev_page=curr_page, prev_page_title=curr_page_title.encode('utf-8'), links=links)

    else:
        return game()


def getGames():
    cur = mysql.connection.cursor()

    min_ind_query = """ SELECT MIN(p.pl_from) from pagelinks p"""
    max_ind_query = """ SELECT MAX(p.pl_from) from pagelinks p"""

    cur.execute(min_ind_query)
    min_ind = cur.fetchone()[0]
    cur.execute(max_ind_query)
    max_ind = cur.fetchone()[0] + 1

    start_ind = random.randrange(min_ind, max_ind)
    end_ind = start_ind

    while end_ind == start_ind:
        end_ind = random.randrange(min_ind, max_ind)

    game_query = """ SELECT p.pl_from FROM pagelinks p WHERE p.pl_from >= %d LIMIT 1 """

    cur.execute(game_query % (end_ind))
    end = cur.fetchone()[0]
    cur.close()

    return end

# game generation


def getStartPage():
    cur = mysql.connection.cursor()

    min_ind_query = """ SELECT MIN(pl_from) from eligible_start"""
    max_ind_query = """ SELECT MAX(pl_from) from eligible_start"""
    cur.execute(min_ind_query)
    min_ind = cur.fetchone()[0]
    cur.execute(max_ind_query)
    max_ind = cur.fetchone()[0] + 1
    start_ind = random.randrange(min_ind, max_ind)
    start_query = """ SELECT pl_from FROM eligible_start WHERE pl_from >= {} LIMIT 1 """.format(start_ind)
    cur.execute(start_query)
    start = cur.fetchone()[0]
    cur.close()
    return start


def getEndPage(start_page, dist=10):

    visited = set()

    start_page_title = getPageTitle(start_page)
    stack = [(start_page_title, 0)]

    next = None

    path = {}

    while len(stack) > 0:
        cur_title, distance = stack.pop()

        # convert title to id
        cur_id = getPageID(cur_title)
        if cur_id is None:
            continue

        if distance == dist:
            tracePath(path, start_page_title, cur_title)
            return cur_id

        neighbors = getNeighbors(cur_id)
        if neighbors is None:
            continue

        unvisited_neighbors = [x for x in neighbors if not x in visited]
        if len(unvisited_neighbors) > 0:
            next_page = random.choice(unvisited_neighbors)
            next_distance = distance + 1
            unvisited_neighbors.remove(next_page)
            for neighbor in unvisited_neighbors:
                stack.append((neighbor, next_distance))
                visited.add(neighbor)
                path[neighbor] = cur_title
            stack.append((next_page, next_distance))
            visited.add(next_page)
            path[next_page] = cur_title

    return getEndPage(start_page, dist - 1)


def tracePath(path, start, end):
    runner = end
    while runner != start:
        print runner
        runner = path[runner]


def getPageTitle(page_id):
    cur = mysql.connection.cursor()
    query = """Select page_title from page where page_id = \"%s\"""" % (str(page_id))
    cur.execute(query)
    page_title = cur.fetchone()[0]
    cur.close()
    return page_title


def getPageID(page_title):
    cur = mysql.connection.cursor()
    query = """ SELECT page_id FROM page WHERE page_title = \"%s\" AND page_namespace = 0""" % (page_title)
    cur.execute(query)
    result = cur.fetchone()
    if result is None:
        return None
    page_id = result[0]
    cur.close()
    return page_id


def getNeighbors(start_page):
    cur = mysql.connection.cursor()
    query = """ SELECT pl_title FROM pagelinks WHERE pl_from = %s""" % (start_page)
    cur.execute(query)
    neighbors = [x[0] for x in cur.fetchall()]
    cur.close()
    return neighbors


def deadEndGen(some_page):
    if some_page is None:
        return render_template('deadend.html', active_page=" ")
    return render_template('deadend.html', active_page=' ( ' + some_page + ' ) ')


@app.route('/deadEnd')
def deadEnd():
    return deadEndGen(active_page=None)


@app.route('/endGame', methods=['GET', 'POST'])
def endGame():
    return render_template('endGame.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
