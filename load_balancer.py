from threading import Timer
from flask import Flask, request
import json
import requests
from flask_apscheduler import APScheduler

interval = 10  # 10s
threshold = 5


class LoadBalancer(object):
    def __init__(self):
        # server list
        self.nodes = []
        self.threshold = threshold

    def add_node(self, sr):
        for n in self.nodes:
            if n.ip == sr.ip:
                return
        self.nodes.append(sr)

    def update(self):
        # print(self.nodes[:])
        nodes = []
        for sr in self.nodes:
            try:
                # update current load
                url = "http://" + sr.ip + ":" + str(sr.port) + "/loadinfo"
                print(url)
                data = requests.get(url).json()
                print(data)
                nodes.append(Node(data["ip"], data["port"], data["load"]))
            except:
                # dead
                print("error")
                nodes.append(Node(sr.ip, sr.port, 0, False))
        self.nodes = list(filter(lambda x: x.alive, nodes))

    def match(self):
        res = Node("", 90, 1000)
        for sr in self.nodes:
            if sr.load < res.load:
                res = sr
        return res


class Config(object):
    SCHEDULER_API_ENABLED = True


scheduler = APScheduler()


@scheduler.task('interval', id='do_job_1', seconds=10, misfire_grace_time=900)
def task():
    lb.update()


class Node:
    def __init__(self, ip, port, load=0, alive=True):
        self.ip = ip
        self.port = port
        self.load = load
        self.alive = alive


app = Flask(__name__)
app.config.from_object(Config())


@app.route("/createRoom")
def create_room():
    print(request.remote_addr)
    sr = lb.match()
    return {
        "ip": sr.ip,
        "port": sr.port
    }


@app.route("/mountNode", methods=["POST"])
def mount_node():
    try:
        data = json.loads(str(request.get_data(), encoding="utf-8"))
        print(data)
        for sr in lb.nodes:
            print("=======" + sr.ip)
            if sr.ip == data["ip"]:
                return {"code": 0}
        lb.add_node(Node(data["ip"], data["port"]))
        # print(data)
        # print(len(lb.nodes))
    except:
        return {"code": 0}
    return {"code": 1}


@app.route("/allInfo", methods=["GET"])
def get_all_info():
    return {"data": [{"ip": node.ip, "port": node.port, "load": node.load, "alive": node.alive} for node in lb.nodes],
            "length": len(lb.nodes)}


if __name__ == '__main__':
    lb = LoadBalancer()
    # lb.add_node(Node("ec2-3-83-175-42.compute-1.amazonaws.com", 9001))
    # lb.add_node(Node("0.0.0.1", 90))
    # lb.add_node(Node("0.0.0.2", 90))
    # lb.add_node(Node("0.0.0.3", 90))
    for sr in lb.nodes:
        print(sr.load)

    scheduler.init_app(app)
    scheduler.start()
    app.run(host="0.0.0.0", port=5001)
    # lb.update()
