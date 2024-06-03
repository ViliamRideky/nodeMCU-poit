from threading import Lock
from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
import time
import serial
import json
import os

async_mode = None

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

data_switch = "Temperature" # or Humidity

ser = serial.Serial('/dev/ttyUSB0', 115200)

data_file = 'data_archive.json'

def write_data_to_file(data_list):
    if os.path.exists(data_file):
        with open(data_file, 'r') as infile:
            all_data = json.load(infile)
    else:
        all_data = []

    all_data.append(data_list)
    
    with open(data_file, 'w') as outfile:
        json.dump(all_data, outfile)

def background_thread(args):
    count = 0  
    dataCounter = 0 
    dataList = []  
    start_time = time.time()       
    while True:
        if args:
            A = dict(args).get('A')
            dbV = dict(args).get('db_value')
        else:
            A = 1
            dbV = 'try'  
        
        socketio.sleep(1)
        
        nodemcu_data = ser.readline().decode('utf-8').strip().split()
        if nodemcu_data[0] == data_switch:
            sensor_data = nodemcu_data[1]
        else:
            continue
            
        print(dbV)
        if dbV == 'start':
            count += 1
            dataCounter += 1
            
            dataDict = {
                "start_time": start_time,
                "t": time.time(),
                "x": dataCounter,
                "sensor_data": sensor_data,
                "data_switch": data_switch
            }
            dataList.append(dataDict)
            
            socketio.emit('my_response',
                      {'sensor_data': str(sensor_data), 'count': count},
                      namespace='/test') 
        else:
            start_time = time.time()
            if len(dataList) > 0:
                print(str(dataList))
                same = str(dataList).replace("'", "\"")
                print(same)
                write_data_to_file(dataList)
                
            dataList = []
            dataCounter = 0
            count = 0

@app.route('/get_data/<int:data_id>', methods=['GET'])
def get_data(data_id):
    with open(data_file, 'r') as infile:
        all_data = json.load(infile)
    if data_id < len(all_data):
        return jsonify({'data': all_data[data_id]})
    else:
        return jsonify({'error': 'Invalid ID'}), 404

@app.route('/list_data', methods=['GET'])
def list_data():
    with open(data_file, 'r') as infile:
        all_data = json.load(infile)
    data_ids = list(range(len(all_data)))
    return render_template('list_data.html', data_ids=data_ids)

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    

@socketio.on('db_event', namespace='/test')
def db_message(message):   
    print("db event")
    session['db_value'] = message['value']   
    print("running"+ message['value'])

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('initialize', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

@socketio.on('switch_data', namespace='/test')
def switch_data(message):
    global data_switch
    print(data_switch)
    data_switch = message['value']
    print(data_switch)
    
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
