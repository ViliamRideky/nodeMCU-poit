from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect
import time
import configparser as ConfigParser
import serial

async_mode = None

app = Flask(__name__)


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 

data_switch = "Temperature" #or Humidity


ser = serial.Serial('/dev/ttyUSB0', 115200)


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
        
        nodemcu_data = ser.readline().decode('utf-8').strip().split();
        if (nodemcu_data[0] == data_switch):
            sensor_data = nodemcu_data[1]
        else:
            continue
            
        print(dbV)
        if dbV == 'start':
            count += 1
            dataCounter +=1
            
            
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
                fuj = str(dataList).replace("'", "\"")
                print(fuj)
                
            dataList = []
            dataCounter = 0
            count = 0
            

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
