from flask import Flask, render_template
#from flask_mysqldb import MySQL

app = Flask(__name__)

'''
mysql = MySQL(app)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'SpeedSearch'
app.config['MYSQL_HOST'] = 'fa16-cs411-10.cs.illinois.edu'
'''

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<name>')
def user(name):
    return render_template('user.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
