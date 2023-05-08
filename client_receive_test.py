import time
from datetime import datetime
from time import  sleep
import socketio
import asyncio
import uuid
import requests
import json
from threading import Thread
from config import current_server
url="http://"+current_server+":9001"
sio=socketio.Client(reconnection_attempts=5)


sending_time=[]

@sio.event
def receive_voice_data(data):
    global sending_time
    if data["UUID"]==0:
        print(data["POSI"])
        start_time=datetime.strptime(data["TIME"], "%Y-%m-%d %H:%M:%S:%f")
        end_time=datetime.now()
        sending_time.append([data["POSI"],(end_time-start_time).total_seconds()])
    # print(data)

async def main():
    await sio.connect(url)
    await sio.emit("join_room_num", {"ROOMID": 1, "UUID": 1})
    await sio.wait()

if __name__ == '__main__':
    sio.connect(url)
    sio.emit("join_room_num", {"ROOMID": 1, "UUID": 1, "data":b"asdsdsa"})
    # asyncio.run(main())
    a = input()
    with open("D:\\cs553\\project\\data.json", 'w') as f:
        save_data = {"DATA": sending_time}
        json.dump(save_data, f)
    sio.disconnect()