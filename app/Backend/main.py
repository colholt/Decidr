from flask import Flask, jsonify, request, json, Response
from flask_cors import CORS
from flaskext.mysql import MySQL
import redis
import ast
app = Flask(__name__)

mysql = MySQL()
app = Flask(__name__)
red = redis.StrictRedis()

CORS(app)

app.config['MYSQL_DATABASE_USER'] = 'decidr'
app.config['MYSQL_DATABASE_PASSWORD'] = 'decidrpass'
app.config['MYSQL_DATABASE_DB'] = 'decidr'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()


def event_stream(roomID):
    pubsub = red.pubsub()
    pubsub.subscribe('users')
    pubsub.subscribe('choices')
    pubsub.subscribe('decisions')
    for new_user in pubsub.listen():
        try:
            vals = ast.literal_eval(new_user['data'])
            print 'vals:'
            print vals['roomID']
            print 'rid:', roomID
            if str(roomID) == str(vals['roomID']):
                yield ("data: %s\n\n" % new_user).decode('utf-8')
        except (KeyError, ValueError) as e:
            print 'err:', e
            yield ("data: %s\n\n" % new_user).decode('utf-8')


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/test', methods=['GET'])
def submit():
    cursor.execute("INSERT INTO rooms VALUES(null, %s)", "test_room")
    conn.commit()
    return jsonify({"insertID": cursor.lastrowid}), 200


@app.route('/subscribe')
def sub_scribe():
    rid = request.args.get('roomid')
    return Response(event_stream(rid), mimetype="text/event-stream")


@app.route('/makeDecision', methods=['POST'])
def make_decision():
    data = request.get_json()
    if data == None:
        return '', 500
    roomID = data['roomID']
    userID = data['userID']
    choiceID = data['choiceID']
    decision = data['decision']
    cursor.execute('INSERT INTO decisions VALUES(null, %s, %s, %s, %s)',
                   (choiceID, userID, roomID, decision))
    red.publish('decisions', u'{"type": "decision", "roomID": %s, "choiceID": %s, "decision": %s}' % (
        roomID, choiceID, decision))
    return '', 200


'''
Body Parameters
        name     # the user's name
        roomID   # room user wishes to join
Returns
        good vibes
'''


@app.route('/addChoice', methods=['POST'])
def add_choice():
    data = request.get_json()
    if data == None:
        return '', 500
    roomID = data['roomID']
    choice = data['choice']
    cursor.execute("INSERT INTO choices VALUES(null, %s, %s)",
                   (choice, str(roomID)))
    choiceID = cursor.lastrowid
    conn.commit()
    red.publish('choices', u'{"type": "choice", "roomID": "%s", "choice": "%s", "choiceID": %s}' % (
        str(roomID), choice, choiceID))
    # red.publish('choices', u'RID:%s: CHOICE ADDED: %s' % (str(roomID), choice))
    return '', 200


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
    print 'room: ', room
    if len(room) != 0:
        cursor.execute("INSERT INTO users VALUES(null, %s, %s)",
                       (data['name'], str(room[0][0])))
        userID = cursor.lastrowid
        conn.commit()
        red.publish('users', u'{"type": "", "roomID": "%s", "name": "%s"}' % (
            str(roomID), data['name']))
        # red.publish('users', u'RID:%s: USER JOINED: %s' % (str(roomID), data['name']))
        cursor.execute("SELECT * FROM choices WHERE rid=%s", roomID)
        choices = []
        for i in cursor.fetchall():
            choices.append(list(i))
        return jsonify({"roomID": room[0][0], "roomName": room[0][1], "userID": userID, "choices": choices}), 200
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
    data = request.get_json()  # get json data from post request
    if data == None:
        return '', 500
    cursor.execute("INSERT INTO rooms VALUES(null, %s)", data['roomName'])
    roomID = cursor.lastrowid
    cursor.execute("INSERT INTO users VALUES(null, %s, %s)",
                   (data['name'], str(roomID)))
    conn.commit()
    return jsonify({"userID": cursor.lastrowid, "roomID": roomID}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
