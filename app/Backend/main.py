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

'''
Body Parameters
        name     # the user's name
        roomID   # room user wishes to join
Returns
        roomID
        roomName
        userID
'''
@app.route('/joinRoom', methods=['POST'])
def join_room():
    data = request.get_json()
    if data == None:
        return '', 500
    roomID = data['roomID']
    cursor.execute("SELECT * FROM rooms WHERE id=%s", roomID)
    room = cursor.fetchall()

    if len(room) != 0:
        cursor.execute("INSERT INTO users VALUES(null, %s, %s)", (data['name'], str(room[0][0])))
        userID = cursor.lastrowid
        conn.commit()
        return jsonify({"roomID": room[0][0], "roomName": room[0][1], "userID": userID}), 200
    else:
        return 'RoomID not valid', 500
    return '', 200

'''
Body Parameters
        name       # the user's name
        roomName   # name of the room user wishes to create
Returns
        userID
        roomID
'''
@app.route('/createRoom', methods=['POST'])
def create_room():
    data = request.get_json() # get json data from post request
    if data == None:
        return '', 500
    cursor.execute("INSERT INTO rooms VALUES(null, %s)", data['roomName'])
    roomID = cursor.lastrowid
    cursor.execute("INSERT INTO users VALUES(null, %s, %s)", (data['name'], str(roomID)))
    conn.commit()
    return jsonify({"userID": cursor.lastrowid, "roomID": roomID}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')
