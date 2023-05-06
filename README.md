# voicechat

## Requirements
### For server
    pip install flask-socketio
    pip install flask
### For client
    python3 -m pip install sounddevice --user
    pip install numpy
    pip install python-socketio
    pip install uuid

## Deployment Method
    1. First open a server (EC2 in AWS)
    2. Run load_balancer.py on that server
    3. Run several servers (EC2 in AWS)
    4. Change config file. Change the file as follow. Do the same thing one each server. 
        Set load_balance_server as load balance server's IP.
        Set current_server as the server's own IP.
    5. Run server.py
    6. Run client.py on local computer. Or, run test file locally. 
        
