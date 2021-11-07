import time

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_socketio import rooms as iorooms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
rooms = {}
member_data = {}
socketio = SocketIO(app, cors_allowed_origins='*')


@app.route("/")
def index_page():
    return render_template("index.html")


@app.route("/room/<name>")
def room_page(name):
    return render_template("room.html", name=name)


@socketio.on('join', namespace='/room')
def on_join(data):
    username = data['username']
    roomname = data['room']
    join_room(roomname)
    if roomname not in rooms:
        rooms[roomname] = [request.sid]
    else:
        rooms[roomname].append(request.sid)
    member_data[request.sid] = {'room': roomname, 'name': username}
    emit('member join', username, to=roomname)


@socketio.on('disconnect', namespace='/room')
def on_disconnect():
    person = member_data[request.sid]
    leave_room(person['room'])
    rooms[person['room']] = [sid for sid in rooms[person['room']] if sid != request.sid]
    del member_data[request.sid]
    emit('member leave', person['name'], to=person['room'])


@socketio.on('message', namespace='/room')
def send_message(data):
    username = data['username']
    message = data['message']
    emit('message', {"username": username, "message": message}, to=member_data[request.sid]['room'],
         include_self=False)


@socketio.on('requestMembers', namespace='/room')
def room_members(data):
    members = [member_data[sid]['name'] for sid in rooms[data]]
    emit('memberResponse', members, to=member_data[request.sid]['room'])


@socketio.on('changeName', namespace='/room')
def change_name(data):
    member_data[request.sid]['name'] = data


if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", debug=True, use_reloader=True)
