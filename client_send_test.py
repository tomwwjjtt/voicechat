import time
from datetime import datetime
from time import  sleep
import socketio
import uuid
import requests
from threading import Thread
# import matplotlib.pyplot as plt

SERVER_URL = "http://ec2-54-144-247-45.compute-1.amazonaws.com:5001/createRoom"
url="http://172.31.1.34:9001"
connect_time=[]


def rtt(sio, idx):
    # start = datetime.now()
    # data={"UUID":idx, "DATA":"a"*512, "ROOMID":1}
    count=0
    while True:
        start=datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        data = {"UUID": idx, "DATA": "a" * 100, "ROOMID": 1, "TIME": start, "POSI":count}
        try:
            sio.emit("voice_chat", data)
            # result=sio.call("voice_chat", data)
            # print("success")
        except:
            # try:
            #     sio.disconnect()
            #     sio.connect(url)
            # except:
            #     print("error")
            #     return
            print("error")
            return
        sleep(0.0001)
        count+=1
        # result = sio.call("voice_chat", data)
        # print(result)
    # end = datetime.now()
    # diff = (end - start).microseconds
    # result[idx] = diff


if __name__ == '__main__':

    thread_num=2

    threads=[0]*thread_num
    for i in range(thread_num):
        connect_start=datetime.now()
        sio=socketio.Client(reconnection_attempts=5)
        sio.connect(url)
        connect_time.append((datetime.now()-connect_start).microseconds)
        sio.emit("join_room_num", {"ROOMID":1, "UUID":1, "A": b"abcd"})
        threads[i]=Thread(target=rtt, args=(sio, i))
        threads[i].start()
        sleep(1)

    print("start!")

    for i in range(thread_num):
        threads[i].join()




    # this_time=datetime.now().strftime()
    # print(this_time)

    # sio = socketio.Client()
    # data=sio.connect(url)
    # print(data)
    # sio.disconnect()



    # data = {"UUID": 1, "DATA": "a" * 512, "ROOMID": 1, "TIME": 00}
    # # result=sio.call("voice_chat", data)
    # # print(result)
    # # result = sio.call("voice_chat", data)
    # # print(result)
    # for i in range(1000):
    #     result=sio.call("voice_chat", data)
    #     print(result)
    # sio.disconnect()
    # for i in range()


# if __name__ == '__main__':
#     server_data = requests.get(SERVER_URL).json()
#     server_url = server_data["ip"] + ":" + str(server_data["port"])
#     count = 0
#     total = 0  # microsecond
#     print(server_data)
#
#     # num_list = range(1, 50000, 100)
#     # avg_rtt = []
#     # loss_rate = []
#     # throughput = []
#     # data = "".join(["a"] * 512)
#     # for num in num_list:
#     #     sio = socketio.Client()
#     #     sio.connect("http://" + server_url)
#     #     threads = [0] * num
#     #     results = [0] * num
#     #     # for i in range(num):
#     #     #     rtt(sio, results, i)
#     #     for i in range(num):
#     #         threads[i] = Thread(target=rtt, args=(sio, results, i))
#     #         threads[i].start()
#     #
#     #     for i in range(len(threads)):
#     #         threads[i].join()
#     #
#     #     a = list(filter(lambda x: x > 0, results))
#     #     thres_list = list(filter(lambda x: x < 20, a))
#     #     throughput.append(len(thres_list))
#     #     loss_rate.append((num - len(a)) * 1.0 / num)
#     #     avg_rtt.append(sum(a) * 1.0 / len(a))
#     #     sio.disconnect()
#     #     print(len(thres_list), num)
#     #     # time.sleep(2)
#     # print(loss_rate)
#     # print(avg_rtt)
#     # print(throughput)
#
#     data_len_list = range(1, 10000, 200)
#     req = 2000
#     rtt_list = []
#     end = None
#     for l in data_len_list:
#         data = "a"*l
#         sio = None
#         try:
#             sio = socketio.Client()
#             sio.connect("http://" + server_url)
#
#             res = [0] * req
#             threads = [0] * req
#             for i in range(req):
#                 threads[i] = Thread(target=rtt, args=(sio, res, i))
#                 threads[i].start()
#
#             for i in range(len(threads)):
#                 threads[i].join()
#
#             rtt_list.append(sum(res)*1.0/req)
#             print(rtt_list)
#             sio.disconnect()
#         except:
#             end = l
#             break
#         finally:
#             sio.disconnect()
#     print(end)
#     print(rtt_list)