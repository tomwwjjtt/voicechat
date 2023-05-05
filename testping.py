import time
from datetime import datetime
import socketio
import uuid
import requests
from threading import Thread
import matplotlib.pyplot as plt

SERVER_URL = "http://ec2-54-159-52-220.compute-1.amazonaws.com:5001/createRoom"


def rtt(sio, result, idx):
    start = datetime.now()
    try:
        # sio.emit("test_ping", data, callback=func(result, idx, start))
        sio.call("test_ping", data, timeout=2)
        end = datetime.now()
        result[idx] = (end-start).total_seconds()
        # time.sleep(1)
    except:
        result[idx] = -1
        return
    # end = datetime.now()
    # diff = (end - start).microseconds
    # print(end)
    # result[idx] = diff


if __name__ == '__main__':
    server_data = requests.get(SERVER_URL).json()
    server_url = server_data["ip"] + ":" + str(server_data["port"])
    count = 0
    total = 0  # microsecond
    print(server_data)

    num_list = range(1, 20)
    avg_rtt = []
    loss_rate = []
    throughput = []
    data = "".join(["a"] * 512)
    sio = socketio.Client()
    sio.connect("http://" + server_url)
    for num in num_list:
        # sio.connect("http://" + server_url)
        threads = [0] * num
        results = [0] * num
        # for i in range(num):
        #     rtt(sio, results, i)
        for i in range(num):
            threads[i] = Thread(target=rtt, args=(sio, results, i))
            threads[i].start()

        for i in range(len(threads)):
            threads[i].join()

        # time.sleep(2)
        a = list(filter(lambda x: x > 0, results))
        print(results)
        thres_list = list(filter(lambda x: x < 20, a))
        throughput.append(len(thres_list))
        loss_rate.append((num - len(a)) * 1.0 / num)
        avg_rtt.append(sum(a) * 1.0 / len(a))
        # sio.disconnect()
        print(len(thres_list), num)
        # time.sleep(2)

    print(loss_rate)
    print(avg_rtt)
    print(throughput)
    sio.disconnect()

    # data_len_list = range(1, 10000, 200)
    # req = 2000
    # rtt_list = []
    # end = None
    # for l in data_len_list:
    #     data = "a"*l
    #     sio = None
    #     try:
    #         sio = socketio.Client()
    #         sio.connect("http://" + server_url)
    #
    #         res = [0] * req
    #         threads = [0] * req
    #         for i in range(req):
    #             threads[i] = Thread(target=rtt, args=(sio, res, i))
    #             threads[i].start()
    #
    #         for i in range(len(threads)):
    #             threads[i].join()
    #
    #         rtt_list.append(sum(res)*1.0/req)
    #         print(rtt_list)
    #         sio.disconnect()
    #     except:
    #         end = l
    #         break
    #     finally:
    #         sio.disconnect()
    # print(end)
    # print(rtt_list)