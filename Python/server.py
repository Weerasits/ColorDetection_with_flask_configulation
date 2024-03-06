import cv2
import socket
import pickle
import numpy as np
from flask import Flask, render_template, Response, jsonify, Request, request
import json
import os

app = Flask(__name__)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = "127.0.0.1"
port = 6667
s.bind((ip, port))

def ReadData():
    global current_trig,current_model,y_start,y_end,x_start,x_end,R_avg,G_avg,B_avg,Yellow_R_min,Yellow_R_max,Yellow_G_min,Yellow_G_max,Yellow_B_min,Yellow_B_max,White_R_min,White_R_max,White_G_min,White_G_max,White_B_min,White_B_max,Blue_R_min,Blue_R_max,Blue_G_min,Blue_G_max,Blue_B_min,Blue_B_max,Gray_R_min,Gray_R_max,Gray_G_min,Gray_G_max,Gray_B_min,Gray_B_max
    global data_path,config_path
    data_path = os.path.join('templates', 'data.json') # Read Data.json from templates
    with open(data_path,'r') as data_file:
        data = json.load(data_file)
    
    config_path = os.path.join('templates', 'config.json') # Read Config.json from templates
    with open(config_path,'r') as config_file:
        config_data = json.load(config_file)

    R_avg = data["r"]
    G_avg = data["g"]
    B_avg = data["b"]
    current_model = data["current_model"]
    current_trig = data["current_trig"]

    y_start = config_data["y_start"]
    y_end = config_data["y_end"]
    x_start  = config_data["x_start"]
    x_end = config_data["x_end"]
    Yellow_R_min = config_data["Yellow_R_min"]
    Yellow_R_max = config_data["Yellow_R_max"]
    Yellow_G_min = config_data["Yellow_G_min"]
    Yellow_G_max = config_data["Yellow_G_max"]
    Yellow_B_min = config_data["Yellow_B_min"]
    Yellow_B_max = config_data["Yellow_B_max"]
    White_R_min = config_data["White_R_min"]
    White_R_max = config_data["White_R_max"]
    White_G_min = config_data["White_G_min"]
    White_G_max = config_data["White_G_max"]
    White_B_min = config_data["White_B_min"]
    White_B_max = config_data["White_B_max"]
    Blue_R_min = config_data["Blue_R_min"]
    Blue_R_max = config_data["Blue_R_max"]
    Blue_G_min = config_data["Blue_G_min"]
    Blue_G_max = config_data["Blue_G_max"]
    Blue_B_min = config_data["Blue_B_min"]
    Blue_B_max = config_data["Blue_B_max"]
    Gray_R_min = config_data["Gray_R_min"]
    Gray_R_max = config_data["Gray_R_max"]
    Gray_G_min = config_data["Gray_G_min"]
    Gray_G_max = config_data["Gray_G_max"]
    Gray_B_min = config_data["Gray_B_min"]
    Gray_B_max = config_data["Gray_B_max"]


try:
    ReadData()
except:
    print("Read data Error")

def gen_frames():
    global x,clientip
    while True:
        try:
            ReadData()

            x = s.recvfrom(1000000)
            clientip = x[1][0]
            data = x[0]
            data = pickle.loads(data)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            
            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                break
            else:
                ret, buffer = cv2.imencode('.jpg', img)
                img = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
        except:
            print('Recall to Server')
            
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(gen_frames(), mimetype = 'multipart/x-mixed-replace; boundary=frame')

@app.route('/get_color_values')
def get_color_values():
    return jsonify({'R_avg': R_avg, 'G_avg': G_avg, 'B_avg': B_avg})

@app.route('/get_config_data')
def get_config_data():
    return jsonify({'current_model' : current_model ,'current_trig' : current_trig})

@app.route('/get_color_config')
def get_color_config():
    ReadData()
    return jsonify({'Yellow_R_min' : Yellow_R_min, 'Yellow_R_max' : Yellow_R_max, 'Yellow_G_min' : Yellow_G_min, 'Yellow_G_max' : Yellow_G_max, 'Yellow_B_min': Yellow_B_min, 'Yellow_B_max' : Yellow_B_max,
                    'White_R_min' : White_R_min, 'White_R_max' : White_R_max, 'White_G_min' : White_G_min, 'White_G_max' : White_G_max, 'White_B_min' : White_B_min, 'White_B_max' : White_B_max,
                    'Blue_R_min' : Blue_R_min, 'Blue_R_max' : Blue_R_max, 'Blue_G_min' : Blue_G_min, 'Blue_G_max' : Blue_G_max, 'Blue_B_min' : Blue_B_min, 'Blue_B_max' : Blue_B_max,
                    'Gray_R_min' : Gray_R_min, 'Gray_R_max' : Gray_R_max, 'Gray_G_min' : Gray_G_min, 'Gray_G_max' : Gray_G_max, 'Gray_B_min' : Gray_B_min, 'Gray_B_max' : Gray_B_max})


@app.route('/receive_data', methods=['POST'])
def receive_data():
    data_from_js = request.json
    # Access individual variables from the received data
    R_min = data_from_js.get('R_min')
    R_max = data_from_js.get('R_max')
    G_min = data_from_js.get('G_min')
    G_max = data_from_js.get('G_max')
    B_min = data_from_js.get('B_min')
    B_max = data_from_js.get('B_max')
    model = data_from_js.get('model')

    # Process the received variables in Python
    print("Received variables from JS:")

    # Write the json file
    if model == 1: # Select Yellow
        ReadData()   
        save_json_config = {
                    "y_start" : y_start,
                    "y_end" : y_end,
                    "x_start" : x_start,
                    "x_end" : x_end,
                    "Yellow_R_min" : R_min,
                    "Yellow_R_max" : R_max,
                    "Yellow_G_min" : G_min,
                    "Yellow_G_max" : G_max,
                    "Yellow_B_min" : B_min,
                    "Yellow_B_max" : B_max,
                    "White_R_min" : White_R_min,
                    "White_R_max" : White_R_max,
                    "White_G_min" : White_G_min,
                    "White_G_max" : White_G_max,
                    "White_B_min" : White_B_min,
                    "White_B_max" : White_B_max,
                    "Blue_R_min" : Blue_R_min,
                    "Blue_R_max" : Blue_R_max,
                    "Blue_G_min" : Blue_G_min,
                    "Blue_G_max" : Blue_G_max,
                    "Blue_B_min" : Blue_B_min,
                    "Blue_B_max" : Blue_B_max,
                    "Gray_R_min" : Gray_R_min,
                    "Gray_R_max" : Gray_R_max,
                    "Gray_G_min" : Gray_G_min,
                    "Gray_G_max" : Gray_G_max,
                    "Gray_B_min" : Gray_B_min,
                    "Gray_B_max" : Gray_B_max
                }
        with open(config_path, 'w') as json_file:
            json.dump(save_json_config, json_file)  


    if model == 2: # White 
        ReadData()  
        save_json_config = {
                    "y_start" : y_start,
                    "y_end" : y_end,
                    "x_start" : x_start,
                    "x_end" : x_end,
                    "Yellow_R_min" : Yellow_R_min,
                    "Yellow_R_max" : Yellow_R_max,
                    "Yellow_G_min" : Yellow_G_min,
                    "Yellow_G_max" : Yellow_G_max,
                    "Yellow_B_min" : Yellow_B_min,
                    "Yellow_B_max" : Yellow_B_max,
                    "White_R_min" : R_min,
                    "White_R_max" : R_max,
                    "White_G_min" : G_min,
                    "White_G_max" : G_max,
                    "White_B_min" : B_min,
                    "White_B_max" : B_max,
                    "Blue_R_min" : Blue_R_min,
                    "Blue_R_max" : Blue_R_max,
                    "Blue_G_min" : Blue_G_min,
                    "Blue_G_max" : Blue_G_max,
                    "Blue_B_min" : Blue_B_min,
                    "Blue_B_max" : Blue_B_max,
                    "Gray_R_min" : Gray_R_min,
                    "Gray_R_max" : Gray_R_max,
                    "Gray_G_min" : Gray_G_min,
                    "Gray_G_max" : Gray_G_max,
                    "Gray_B_min" : Gray_B_min,
                    "Gray_B_max" : Gray_B_max
                }
        with open(config_path, 'w') as json_file:
            json.dump(save_json_config, json_file)

    if model == 3: # Select Blue
        ReadData()      
        save_json_config = {
                    "y_start" : y_start,
                    "y_end" : y_end,
                    "x_start" : x_start,
                    "x_end" : x_end,
                    "Yellow_R_min" : Yellow_R_min,
                    "Yellow_R_max" : Yellow_R_max,
                    "Yellow_G_min" : Yellow_G_min,
                    "Yellow_G_max" : Yellow_G_max,
                    "Yellow_B_min" : Yellow_B_min,
                    "Yellow_B_max" : Yellow_B_max,
                    "White_R_min" : White_R_min,
                    "White_R_max" : White_R_max,
                    "White_G_min" : White_G_min,
                    "White_G_max" : White_G_max,
                    "White_B_min" : White_B_min,
                    "White_B_max" : White_B_max,
                    "Blue_R_min" : R_min,
                    "Blue_R_max" : R_max,
                    "Blue_G_min" : G_min,
                    "Blue_G_max" : G_max,
                    "Blue_B_min" : B_min,
                    "Blue_B_max" : B_max,
                    "Gray_R_min" : Gray_R_min,
                    "Gray_R_max" : Gray_R_max,
                    "Gray_G_min" : Gray_G_min,
                    "Gray_G_max" : Gray_G_max,
                    "Gray_B_min" : Gray_B_min,
                    "Gray_B_max" : Gray_B_max
                }
        with open(config_path, 'w') as json_file:
            json.dump(save_json_config, json_file)

    if model == 4: # Select Gray  
        ReadData()      
        save_json_config = {
                    "y_start" : y_start,
                    "y_end" : y_end,
                    "x_start" : x_start,
                    "x_end" : x_end,
                    "Yellow_R_min" : Yellow_R_min,
                    "Yellow_R_max" : Yellow_R_max,
                    "Yellow_G_min" : Yellow_G_min,
                    "Yellow_G_max" : Yellow_G_max,
                    "Yellow_B_min" : Yellow_B_min,
                    "Yellow_B_max" : Yellow_B_max,
                    "White_R_min" : White_R_min,
                    "White_R_max" : White_R_max,
                    "White_G_min" : White_G_min,
                    "White_G_max" : White_G_max,
                    "White_B_min" : White_B_min,
                    "White_B_max" : White_B_max,
                    "Blue_R_min" : Blue_R_min,
                    "Blue_R_max" : Blue_R_max,
                    "Blue_G_min" : Blue_G_min,
                    "Blue_G_max" : Blue_G_max,
                    "Blue_B_min" : Blue_B_min,
                    "Blue_B_max" : Blue_B_max,
                    "Gray_R_min" : R_min,
                    "Gray_R_max" : R_max,
                    "Gray_G_min" : G_min,
                    "Gray_G_max" : G_max,
                    "Gray_B_min" : B_min,
                    "Gray_B_max" : B_max
                }
        with open(config_path, 'w') as json_file:
            json.dump(save_json_config, json_file)    

    return jsonify({'message': 'Data received successfully'})

if __name__ == "__main__":
    try:
        app.run(host='192.168.250.66')
    except:
        print("Error")
    

