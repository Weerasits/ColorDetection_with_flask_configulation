import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import numpy as np
import fins.udp
import time
from PIL import Image, ImageFilter, ImageEnhance
from numpy import asarray
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import socket
import pickle
import json


# PLC Connection Config
plc_address = '192.168.250.1'
plc_last_address = 1
server_last_address = 66

Modelnum=""
CheckOk=""
CheckOkY=""
CheckOkW=""
CheckOkB=""
CheckOkG=""
CamStatus=""


Camport=0
interval = 1
previousMillis=0
State = False
color=""
nbin = 200
Readtrig=0

Current_trig = 'False'


# Server Connection
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,1000000)
server_ip = "127.0.0.1"
server_port = 6667

#Json Loader

#-Load Json Config
config_path = os.path.join('templates', 'config.json')
with open(config_path, 'r') as config_file:
    config_data = json.load(config_file)

#-Load Json Data
data_path = os.path.join('templates','data.json')
with open(data_path,'r') as data_file:
    data = json.load(data_file)
    
def ReadVariable():
    global y_start,y_end,x_start,x_end,Yellow_R_min,Yellow_R_max,Yellow_G_min,Yellow_G_max,Yellow_B_min,Yellow_B_max,White_R_min,White_R_max,White_G_min,White_G_max,White_B_min,White_B_max,Blue_R_min,Blue_R_max,Blue_G_min,Blue_G_max,Blue_B_min,Blue_B_max,Gray_R_min,Gray_R_max,Gray_G_min,Gray_G_max,Gray_B_min,Gray_B_max

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


#-import Json Value
    
#Config Variable
ReadVariable()

y_start = config_data["y_start"]
y_end = config_data["y_end"]
x_start  = config_data["x_start"]
x_end = config_data["x_end"]


#Draw Rectangle variable
Click = False 
p1 = (0,0)
p2 = (0,0)

class Connectomron:
    def MemAdd(DesAdd):
        bytes_val = DesAdd.to_bytes(2,'big')
        return bytes_val+b'\x00'

    def MemDataWrt(dataW):
        bytes_data= dataW.to_bytes(2,'big')
        return bytes_data

    def MemDataRd(dataR):
        val=int.from_bytes(dataR[-2:],'big')
        return val

    def MembitAdd(DesAdd,Desbit):
        bytes_val = DesAdd.to_bytes(2,'big')
        bytesbit_val = Desbit.to_bytes(1,'big')
        return bytes_val+bytesbit_val

    def MemDatabitWrt(databit:bool):
        bytes_data= databit.to_bytes(1,'big')
        return bytes_data

    def MemDatabitRd(databitR):
        val=bool.from_bytes(databitR[-1:],'big')
        return val

def colordetect():
    #input_img = cv2.imread("BL2.jpg")
    cap = cv2.VideoCapture(Camport)
    #imgre = cv2.resize(input_img, (640, 480))
    #img = imgre[50:300, 290:390]
    #img=imgre
    #Connect to Omron

    global CheckOk
    global CheckOkY
    global CheckOkW
    global CheckOkB
    global CheckOkG
    global CamStatus
    global Modelnum
    global previousMillis
    global State
    global color
    global Readtrig
    global Click
    global detection_status
    detection_status = False


    # Crop Position Variable
    while True:
        try:
            global R_avg,G_avg,B_avg,config_data

            # Read Config Data while loop
            config_path = os.path.join('templates', 'config.json')
            with open(config_path, 'r') as config_file:
                config_data = json.load(config_file)
            ReadVariable()
            
            # Call Camera
            CamStatus=True
            ret, input_img = cap.read()
            imgre=input_img

            def Distance():
                global x_start, x_end, y_start, y_end
                if p1[0] < p2[0] and p1[1] < p2[1]:
                    x_start = p1[0]
                    x_end = p2[0]
                    y_start = p1[1]
                    y_end = p2[1]
                if p1[0] > p2[0] and p1[1] < p2[1]:
                    x_start = p2[0]
                    x_end = p1[0]
                    y_start = p1[1]
                    y_end = p2[1]
                if p1[0] > p2[0] and p1[1] > p2[1]:
                    x_start = p2[0]
                    x_end = p1[0]
                    y_start = p2[1]
                    y_end = p1[1]
                if p1[0] < p2[0] and p1[1] > p2[1]:
                    x_start = p1[0]
                    x_end = p2[0]
                    y_start = p2[1]
                    y_end = p1[1]

                return x_start,x_end,y_start,y_end
    

            ## Image Processing Part
            img = input_img[y_start:y_end, x_start:x_end]
            height,widght, _ = img.shape
            cx=int(widght/2)
            cy=int(height/2)
            pixelcenter=img[cy,cx]
            cv2.circle(img,(cx,cy),5,(255, 0, 0),2)
            ret, buffer = cv2.imencode(".jpg", imgre, [int(cv2.IMWRITE_JPEG_QUALITY),30])

            x_as_bytes = pickle.dumps(buffer)
            s.sendto((x_as_bytes),(server_ip,server_port)) #Sent Data from camera to server
            np_data = asarray(img) # เป็น array ขนาด (393, 993)
            w = np_data.shape[0]
            h = np_data.shape[1]
            total_pixel = w*h
            np_data = np_data.flatten().reshape(total_pixel, 3)
            R = np_data[:,2]
            G = np_data[:,1]
            B = np_data[:,0]
            avg = np.average(np_data, axis=0)
            R_avg = avg[2]
            G_avg = avg[1]
            B_avg = avg[0]
            cv2.rectangle(imgre,(x_start,y_start),(x_end,y_end),(0,0,255),2) # Draw Rectangle
            R_avg_str = '{:.3f}'.format(R_avg)
            G_avg_str = '{:.3f}'.format(G_avg)
            B_avg_str = '{:.3f}'.format(B_avg)
            SentDataToServer()
            cv2.putText(
                img=imgre,
                text="Red : " + R_avg_str,
                org=(50,60),
                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                fontScale=0.9,
                color=(0,0,255),
                thickness=2
                )
            cv2.putText(
                    img=imgre,
                    text="Green : " + G_avg_str,
                    org=(50,100),
                    fontFace=cv2.FONT_HERSHEY_COMPLEX,
                    fontScale=0.9,
                    color=(0,255,0),
                    thickness=2
                )
            cv2.putText(
                    img=imgre,
                    text="Blue : " + B_avg_str,
                    org=(50,140),
                    fontFace=cv2.FONT_HERSHEY_COMPLEX,
                    fontScale=0.9,
                    color=(255,0,0),
                    thickness=2
                )
            
            def drawfunction(event, x, y, flags, param):
                global Click,p1,p2
                if event == cv2.EVENT_LBUTTONDOWN:
                    Click = True
                    cv2.circle(imgre, (x, y), 20, (255, 255, 255), -1)
                    p1 = (x,y)
                    # print("X = " , x , "Y= ", y)

                if Click == True:
                    # print(Click)
                    cv2.circle(imgre, (x, y), 20, (255, 255, 255), -1)
                    p2 = (x,y)
                    # print("X = " , x , "Y= ", y)
                    Distance()
                if event == cv2.EVENT_LBUTTONUP:
                    Click = False
                    # print("Release")
        except:
            CamStatus=False
            print("No Camera Connected")
            cap = cv2.VideoCapture(Camport)

        # loop through the yellow contours and draw a rectangle around them
        if CamStatus and Readtrig:
            #color = 'Undefined Color'
            if (Yellow_R_min <= R_avg <= Yellow_R_max) and (Yellow_G_min <= G_avg<= Yellow_G_max)and (Yellow_B_min <= B_avg <= Yellow_B_max) and ((G_avg-B_avg) >= 20) and Modelnum==1:
                color ='Yellow'
                CheckOkY="ok"
                detection_status = True
                print(color)
                print('R_avg:', "%0.1f" % R_avg)
                print('G_avg:', "%0.1f" % G_avg)
                print('B_avg:', "%0.1f" % B_avg)
                # print(color)
        else:
            CheckOkY="ng"
            
        # loop through the white contours and draw a rectangle around them
        if CamStatus and Readtrig:
            #color = 'Undefined Color'
            if (White_R_min <= R_avg<= White_R_max) and (White_G_min <= G_avg<= White_G_max)and (White_B_min <= B_avg<= White_B_max) and (abs(B_avg-R_avg) <= 30) and Modelnum==2:
   
                color ='White'
                CheckOkW="ok"
                detection_status = True
                print('R_avg:', "%0.1f" % R_avg)
                print('G_avg:', "%0.1f" % G_avg)
                print('B_avg:', "%0.1f" % B_avg)
                # print(color)
        else:
            CheckOkW="ng"
            
        # loop through the blue contours and draw a rectangle around them
        if CamStatus and Readtrig:
            #color = 'Undefined Color'
            if (Blue_R_min <= R_avg <= Blue_R_max) and (Blue_G_min <= G_avg <= Blue_G_max)and (Blue_B_min <= B_avg <= Blue_B_max) and (abs(R_avg-G_avg) >= 30) and Modelnum==3:
            
                color ='Blue'
                CheckOkB="ok"
                detection_status = True
                print('R_avg:', "%0.1f" % R_avg)
                print('G_avg:', "%0.1f" % G_avg)
                print('B_avg:', "%0.1f" % B_avg)
                # print(color)
        else:
            CheckOkB="ng"
            
        
        # loop through the grey contours and draw a rectangle around them
        if CamStatus and Readtrig:
            #color = 'Undefined Color'
            if (Gray_R_min <= R_avg <= Gray_R_max) and (Gray_G_min <= G_avg <= Gray_G_max) and (Gray_B_min <= B_avg <= Gray_B_max) and (abs(R_avg-G_avg) <= 20) and (abs(B_avg-G_avg) > 20) and Modelnum==4 :
                color ='Gray'
                CheckOkG="ok"
                detection_status = True
                print('R_avg:', "%0.1f" % R_avg)
                print('G_avg:', "%0.1f" % G_avg)
                print('B_avg:', "%0.1f" % B_avg)
                # print(color)
        else:
            CheckOkG="ng"      
        
        #print(color)   
            
        try:
            fins_instance = fins.udp.UDPFinsConnection()
            fins_instance.connect('plc_address')
            fins_instance.dest_node_add= plc_last_address
            fins_instance.srce_node_add= server_last_address


            # print("Link Omron Done")
        #RW Data Mem
            #Read Select Model Color from Omron D2000 1=yellow 2=white 3=blue 4=grey
            getModeldata = fins_instance.memory_area_read(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD,Connectomron.MemAdd(4000))
            Modelnum=Connectomron.MemDataRd(getModeldata)
            #fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD,Connectomron.MemAdd(500),Connectomron.MemDataWrt(1234),1)
            
        #RW Bit Mem
            #Send Fins Status Ok D3002.0   
            
            currentMillis = time.time()
            if (currentMillis - previousMillis >= interval):
                if (State == False):
                    fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_BIT,Connectomron.MembitAdd(3002,0),Connectomron.MemDatabitWrt(True),1)
                    #print('R_avg:', "%0.1f" % R_avg)
                    #print('G_avg:', "%0.1f" % G_avg)
                    #print('B_avg:', "%0.1f" % B_avg)
                    State = True
                else :
                    fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_BIT,Connectomron.MembitAdd(3002,0),Connectomron.MemDatabitWrt(False),1)
                    State = False
                previousMillis = currentMillis
            #Send Cam Status Ok D3002.1 
            fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_BIT,Connectomron.MembitAdd(3002,1),Connectomron.MemDatabitWrt(CamStatus),1)   
            #Read Trigger D3000.0
            getTrigger = fins_instance.memory_area_read(fins.FinsPLCMemoryAreas().DATA_MEMORY_BIT,Connectomron.MembitAdd(3000,0))
            Readtrig = Connectomron.MemDatabitRd(getTrigger)

            if Readtrig:
                global Current_trig
                if (CheckOkY=="ok") or (CheckOkW=="ok") or (CheckOkB=="ok") or (CheckOkG=="ok")  :
                    #Send OK D3001.1
                    fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_BIT,Connectomron.MembitAdd(3001,1),Connectomron.MemDatabitWrt(True),1)
                    fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_BIT,Connectomron.MembitAdd(3001,2),Connectomron.MemDatabitWrt(False),1)
                    Current_trig = "oK"
                else:
                #Send NG D3001.2
                    # print('R_avg:', "%0.1f" % R_avg)
                    # print('G_avg:', "%0.1f" % G_avg)
                    # print('B_avg:', "%0.1f" % B_avg)
                    color='NG'
                    # print(color)
                    fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_BIT,Connectomron.MembitAdd(3001,1),Connectomron.MemDatabitWrt(False),1)
                    fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_BIT,Connectomron.MembitAdd(3001,2),Connectomron.MemDatabitWrt(True),1)
                    Current_trig = "NG"
            else:
                fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_BIT,Connectomron.MembitAdd(3001,1),Connectomron.MemDatabitWrt(False),1)
                fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_BIT,Connectomron.MembitAdd(3001,2),Connectomron.MemDatabitWrt(False),1)
                Current_trig = "False"
            #print(MemDataRd(mem_area))
            #print(Connectomron.MemDatabitRd(mem_areabit))
            #time.sleep(0.1)
        except:
            Modelnum=0
            Readtrig=False
            print("Cannot Connected ...") 

        try:
            # Display final output for multiple color detection opencv python
            cv2.imshow("Original",imgre)
            cv2.imshow('image', img)
            cv2.setMouseCallback("Original", drawfunction)
            if cv2.waitKey(1) == ord('q'):
                print("Save Data!")
                saveConfig()
                time.sleep(0.5)
                break
        except:
            if cv2.waitKey(1) == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()

def saveConfig():
    save_config = {
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
        "Gray_R_min" : Gray_R_min,
        "Gray_R_max" : Gray_R_max,
        "Gray_G_min" : Gray_G_min,
        "Gray_G_max" : Gray_G_max,
        "Gray_B_min" : Gray_B_min,
        "Gray_B_max" : Gray_B_max
    }
    with open(config_path, 'w') as config_file:
        json.dump(save_config, config_file)

def SentDataToServer():
    if Modelnum == 1:
        sent_data = {
            "r" : R_avg,
            "g" : G_avg,
            "b" : B_avg,
            "current_model" : "Yellow",
            "current_trig" : Current_trig
        }
        with open(data_path,'w') as data_file:
            json.dump(sent_data,data_file)
    if Modelnum == 2:
        sent_data = {
            "r" : R_avg,
            "g" : G_avg,
            "b" : B_avg,
            "current_model" : "White",
            "current_trig" : Current_trig
        }
        with open(data_path,'w') as data_file:
            json.dump(sent_data,data_file)
    if Modelnum == 3:
        sent_data = {
            "r" : R_avg,
            "g" : G_avg,
            "b" : B_avg,
            "current_model" : "Blue",
            "current_trig" : Current_trig
        }
        with open(data_path,'w') as data_file:
            json.dump(sent_data,data_file)
    if Modelnum == 4:
        sent_data = {
            "r" : R_avg,
            "g" : G_avg,
            "b" : B_avg,
            "current_model" : "Gray",
            "current_trig" : Current_trig
        }
        with open(data_path,'w') as data_file:
            json.dump(sent_data,data_file)
    if Modelnum > 4 or Modelnum < 1:
        sent_data = {
            "r" : R_avg,
            "g" : G_avg,
            "b" : B_avg,
            "current_model" : "null",
            "current_trig" : Current_trig
        }
        print(Modelnum)
        with open(data_path,'w') as data_file:
            json.dump(sent_data,data_file)

if __name__ == "__main__":
    colordetect()
