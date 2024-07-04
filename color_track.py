# program currently takes a long time to actually start working after running, don't be concerned by the long wait time

import numpy as np
from collections import deque
import serial
import cv2

# comment out along with other serial commands when only testing camera, otherwise program will give error
ser = serial.Serial('COM3', 9800, timeout=1)

a= [] # list that keeps track of # of bounding boxes on screen
X = deque(maxlen=3) # special type of list that keeps track of x positions, max length is set to 3 and overwrites oldest value when appending new ones

# I found a deque to be an efficient way to store/remove position values without needing to write code to constantly clear the list
# I assume that continuing to extend a list of data values without clearing will eventually slow down program

# not super familiar with opencv, feel free to use a different setup if its more efficient
# much of this was borrowed from online, some steps I cannot explain fully

# initial values set for color mask
#hueLow=90
#hueHigh=100

hueLow=0
hueHigh=20

hueLow2=90
hueHigh2=100

#satLow=20
#satHigh=200

satLow=113
satHigh=255

#valLow=20
#valHigh=200

valLow=243
valHigh=255

def onTrack1(val):
    global hueLow
    hueLow=val
    #print('Low Hue: ',val)
def onTrack2(val):
    global hueHigh
    hueHigh=val
    #print('High Hue: ',val)
def onTrack3(val):
    global satLow
    satLow=val
    #print('Low Sat: ',val)
def onTrack4(val):
    global satHigh
    satHigh=val
    #print('High Sat: ',val)
def onTrack5(val):
    global valLow
    valLow=val
    #print('Low Val: ',val)
def onTrack6(val):
    global valHigh
    valHigh=val
    #print('High Val: ',val)

width=640
height=360
cam=cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) 
cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
success, frame = cam.read()

cv2.namedWindow('myTracker')
cv2.moveWindow('myTracker',width,0)
cv2.resizeWindow('myTracker',400,400)
cv2.createTrackbar('Hue Low','myTracker',15,180,onTrack1)
cv2.createTrackbar('Hue High','myTracker',30,180,onTrack2)
cv2.createTrackbar('Sat Low','myTracker',10,255,onTrack3)
cv2.createTrackbar('Sat High','myTracker',255,255,onTrack4)
cv2.createTrackbar('Val Low','myTracker',10,255,onTrack5)
cv2.createTrackbar('Val High','myTracker',255,255,onTrack6)

while True:
    ignore,  frame = cam.read()
    frameHSV=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    lowerBound=np.array([hueLow,satLow,valLow])
    upperBound=np.array([hueHigh,satHigh,valHigh])

    lowerBound2=np.array([hueLow2,satLow,valLow])
    upperBound2=np.array([hueHigh2,satHigh,valHigh])

    myMask=cv2.inRange(frameHSV,lowerBound,upperBound)
    myMask2=cv2.inRange(frameHSV,lowerBound2,upperBound2)

    myMask=myMask | myMask2
    contours,junk=cv2.findContours(myMask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area=cv2.contourArea(contour)
        if area>=400:
            x,y,w,h=cv2.boundingRect(contour)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),3)
            x1=w/2
            y1=h/2
            cx=x+x1
            cy=y+y1
            a.append(x)
    
    # displaying x-coordinate and # of bounding boxes on frame
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame,str(x),(50,25),font,0.7,(0,255,0),2)
    cv2.putText(frame,str(len(a)),(50,50),font,0.7,(0,255,0),2)

    # program only runs fully when only 1 bounding box is currently present
    # constantly running check to ensure list "a" only has a length of 1
    if len(a) == 1:
        X.append(x)
        a.clear()  
        
        if X[-1] is not None:
            dX = X[-1] - X[0]
            
            if abs(dX) > 10:
                cv2.putText(frame,'blue',(125,50),font,0.7,(0,255,0),2) if np.sign(dX) == 1 else cv2.putText(frame,'red',(125,50),font,0.7,(0,255,0),2)
                ser.write(b'B') if np.sign(dX) == 1 else ser.write(b'R')
                
            else:
                cv2.putText(frame,'white',(125,50),font,0.7,(0,255,0),2)
                ser.write(b'W')
            
        else:
            continue
    
    else:
        dX = 'none'
        ser.write(b'O') # turn led off when theres more than one object being tracked
    
    cv2.putText(frame,str(dX),(125,25),font,0.7,(0,255,0),2)
    
    a.clear()

    myMaskSmall=cv2.resize(myMask,(int(width/2),int(height/2)))
    mySelection=cv2.bitwise_and(frame,frame, mask=myMask)
    mySelection=cv2.resize(mySelection,(int(width/2),int(height/2)))
    cv2.imshow('My Selection', mySelection)
    cv2.moveWindow('My Selection',int(width/2),520)

    cv2.imshow('My Mask', myMaskSmall)
    cv2.moveWindow('My Mask',0,520)
    cv2.imshow('my WEBcam',frame)
    cv2.moveWindow('my WEBcam',0,0)
    if cv2.waitKey(1) & 0xff ==ord('q'):
        break

# turn off led, close serial port, and close windows on quitting
ser.write(b'O')
ser.close() # important to ensure all ports are closed when finished with program, may cause problems if left out when using arduino
cam.release()
cv2.destroyAllWindows()

