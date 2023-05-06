from threading import Thread, Lock, Condition
import sounddevice as sd
from time import sleep
import numpy as np
import socketio
from uuid import uuid1
import requests
from config import load_balance_server

# url="http://172.31.1.34:9001"
sio=socketio.Client(reconnection_attempts=5)


MAX_BYTES_SEND = 512  # Must be less than 1024 because of networking limits
MAX_HEADER_LEN = 20  # allocates 20 bytes to store length of data that is transmitted

my_uuid=uuid1().hex
room_id=1

# SERVER_IP = "172.31.0.1" # Change this to the external IP of the server

# SERVER_PORT = 9001
BUFMAX = 512
running = True
mutex_t = Lock()
item_available = Condition()
SLEEPTIME = 0.0001  # amount of time CPU sleeps between sending recordings to the server
# SLEEPTIME = 0.000001
audio_available = Condition()

sdstream = sd.Stream(samplerate=44100, channels=1, dtype='float32')
sdstream.start()



def split_send_bytes(s, inp):
    s.emit("voice_chat", {"UUID": my_uuid, "ROOMID": room_id, "DATA": inp})


class SharedBuf:
    def __init__(self):
        self.buffer = np.array([], dtype='float32')

    def clearbuf(self):
        self.buffer = []

    def addbuf(self, arr):
        self.buffer = np.append(self.buffer, arr)

    def extbuf(self, arr):
        self.buffer = np.append(self.buffer, arr)

    def getlen(self):
        return len(self.buffer)

    def getbuf(self):
        return self.buffer

    def getx(self, x):
        data = self.buffer[0:x]
        self.buffer = self.buffer[x:]
        return data

rbuf = SharedBuf()

# record t seconds of audio
def record(t):
    global running
    if running:
        return sdstream.read(t)[0]

def transmit(buf, socket):
    global running
    pickled = buf.tobytes()
    split_send_bytes(socket, pickled)

def record_transmit_thread(serversocket):
    print("***** STARTING RECORD TRANSMIT THREAD *****")
    tbuf = SharedBuf()
    global running

    def recorder_producer(buf):
        global running
        while running:
            sleep(SLEEPTIME)
            data = record(32)
            with item_available:
                item_available.wait_for(lambda: buf.getlen() <= BUFMAX)
                buf.extbuf(data)
                item_available.notify()

        print("RECORDER ENDS HERE")

    def transmitter_consumer(buf, serversocket):
        global running
        while running:
            sleep(SLEEPTIME)
            with item_available:
                item_available.wait_for(lambda: buf.getlen() >= 32)
                transmit(buf.getx(32), serversocket)
                item_available.notify()

        print("TRANSMITTER ENDS HERE")

    rec_thread = Thread(target=recorder_producer, args=(tbuf,))
    tr_thread = Thread(target=transmitter_consumer, args=(tbuf, serversocket))

    rec_thread.start()
    tr_thread.start()

    rec_thread.join()
    tr_thread.join()
    return

# use a sound library to play the buffer
def play(buf):
    # print("playing_audio")
    global running
    if running:
        sdstream.write(buf)



def play_thread(serversocket):
    print("***** STARTING RECEIVE PLAY THREAD *****")
    global rbuf
    def player_consumer(buff):
        while running:
            sleep(SLEEPTIME)
            with audio_available:
                audio_available.wait_for(lambda: buff.getlen() >= 32)
                play(buff.getx(buff.getlen()))
                audio_available.notify()

        print("PLAYER ENDS HERE")

    global running
    play_thread = Thread(target=player_consumer, args=(rbuf,))
    play_thread.start()
    play_thread.join()
    return



@sio.event
def receive_voice_data(data):
    global rbuf
    if data["UUID"]!=my_uuid:
        dat=data["DATA"]
        rbuf.extbuf(np.fromstring(dat))

def main(roomid, url):
    # serversocket = connect()
    sio.connect(url)
    sio.emit("join_room_num", {"ROOMID": roomid, "UUID": my_uuid})
    global running
    t_thread = Thread(target=record_transmit_thread, args=(sio,))
    p_thread = Thread(target=play_thread, args=(sio,))
    t_thread.start()
    p_thread.start()
    input("press enter to exit")
    running = False
    sdstream.stop()
    t_thread.join()
    p_thread.join()
    sio.disconnect()

if __name__ == '__main__':
    status=input("1 for create, 2 for join")
    if status==1:
        get_server_url="http://"+load_balance_server+":5001/createRoom"
        server_info=requests.get(get_server_url)
        server_ip=server_info["ip"]
        server_port=server_info["port"]
        server="http://"+server_ip+":"+server_port
        print("server:", server)
        ask_for_room="http://"+server_ip+"/createRoom"
        room_info=requests.get(ask_for_room)
        if room_info["CODE"]==0:
            print("no room")
            exit()
        else:
            room_id=room_info["ROOMID"]
    else:
        server=input("server: ")
        room_id=int(input("room id:"))
    main(room_id, server)