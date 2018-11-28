from flask import Flask, jsonify, request, json
from flask_cors import CORS
from flaskext.mysql import MySQL
app = Flask(__name__)

mysql = MySQL()
app = Flask(__name__)

CORS(app)

app.config['MYSQL_DATABASE_USER'] = 'decidr'
app.config['MYSQL_DATABASE_PASSWORD'] = 'decidrpass'
app.config['MYSQL_DATABASE_DB'] = 'decidr'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/test', methods=['GET'])
def submit():
    cursor.execute("INSERT INTO rooms VALUES(null, %s)", "test_room")
    conn.commit()
    return jsonify({"insertID": cursor.lastrowid}), 200

@app.route('/joinRoom')
def join_room():
    pass

@app.route('/createRoom', methods=['POST'])
def create_room():
    data = request.get_json() # get json data from post request
    if data == None:
        return '', 500
    cursor.execute("INSERT INTO rooms VALUES(null, %s)", data['roomName'])
    roomID = cursor.lastrowid
    cursor.execute("INSERT INTO users VALUES(null, %s, %s)", (data['name'], str(roomID)))
    conn.commit()
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')
