from flask import Flask
# from config import mount_server
from flask_socketio import SocketIO, join_room, send, emit
import requests
from config import load_balance_server, current_server

app=Flask(__name__)

socketio=SocketIO(async_mode="threading")
socketio.init_app(app)



room_ids=[i for i in range(300)]

LOCK=0

LOAD=0
# SELF_IP="ec2-54-152-18-235.compute-1.amazonaws.com"
SELF_IP=current_server
SOCK_PORT = 9001
SOCK_IP="0.0.0.0"


def getLoad():
    global LOAD
    return LOAD

@app.route("/loadinfo")
def send_load_info():
    return{
        "ip":SELF_IP,
        "port":SOCK_PORT,
        "load":getLoad()
    }


@socketio.on("connect")
def connect():
    global LOAD
    LOAD+=1



@socketio.on("voice_chat")
def client_commute(voice_data):
    if voice_data["UUID"]==0:
        print("send data:", voice_data)
    emit("receive_voice_data", voice_data, to=voice_data["ROOMID"])


@socketio.on("join_room_num")
def join_room_num(room_data):
    # print("data: ", data)
    group_id=room_data["ROOMID"]
    # print("data2:", room_data)
    join_room(group_id)
    # print("join room: ", data)
    #emit("receive_voice_data", {"ROOMID": room_data["ROOMID"], "DATA": "some one come in", "UUID" : room_data["UUID"]}, to=group_id)
    #emit("receive_voice_data", "someone joining group...", to=group_id)


@socketio.on("disconnect")
def disconnect_client():
    global LOAD
    LOAD-=1


@socketio.on("room_close")
def close_room(close_data):
    global LOCK
    room_id=close_data["ROOMID"]
    socketio.close_room(room_id)
    room_ids.append(room_id)
    emit("one_message", {"CODE":1})

@socketio.on("test_ping")
def test_ping(test_data):
    emit("test_ping", test_data)



@app.route("/createRoom")
def create_room(methods=["get"]):
    global room_ids
    try:
        room_id=room_ids.pop(0)
        return {
            "CODE":1,
            "ROOMID":room_id
        }
    except:
        return {
            "CODE":0,
            "ROOMID":-1
        }









if __name__ == '__main__':
    my_data={"ip": SELF_IP,
             "port": 9001}
    connect_in_lbs="http://"+load_balance_server+":5001/mountNode"
    # requests.post("http://ec2-34-228-21-189.compute-1.amazonaws.com:5001/mountNode", json=my_data)
    requests.post(connect_in_lbs, json=my_data)
    socketio.run(app, debug=True, host=SOCK_IP, port=SOCK_PORT)
    #socketio.run(app, debug=True, host=SOCK_IP, port=9002)