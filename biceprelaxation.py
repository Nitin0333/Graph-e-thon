import cv2
import mediapipe as mp
import numpy as np
import math
mp_drawing=mp.solutions.drawing_utils
mp_pose=mp.solutions.pose

def anglecal(a,b,c):
    a=np.array(a)
    b=np.array(b)
    c=np.array(c)
    radians=np.arctan2(c[1]-b[1],c[0]-b[0])-np.arctan2(a[1]-b[1],a[0]-b[0])
    angle=np.abs(radians*180.0/np.pi)
    if angle>180.0:
        angle=360-angle
    return angle

counter=0
hold=5
def initialize(fps):
    global hold
    hold=fps*5

def left(landmarks):
    return landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility>=0.4 and landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].visibility>=0.4 

def right(landmarks):
    return  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility>=0.4 and  landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].visibility>=0.4

def repcounter(a,b,c,d,e,f,image,fps):
    angle1=anglecal(a,b,c)
    angle2=anglecal(d,e,f)
    global counter
    global hold
    if  (angle1>=30.0 and angle1<130.0) or (angle2>=30.0 and angle2<130.0):
        if(hold==0):
            counter+=1
        initialize(fps)
    elif hold==0:
        cv2.putText(image,'relax your arms',(10,50),font,1,(0,0,0),2,cv2.LINE_4)
    elif(angle1<30.0 or angle2<30.0) and hold!=0:
        cv2.putText(image,'hold for '+str(math.ceil(hold/fps))+' sec',(10,50),font,1,(0,0,0),2,cv2.LINE_4)
        hold-=1
    return

font = cv2.FONT_HERSHEY_SIMPLEX 
c=0
cap=cv2.VideoCapture(0)
with mp_pose.Pose(min_detection_confidence=0.4,min_tracking_confidence=0.4) as pose:
    while(cap.isOpened()):
        
        ret,frame=cap.read()
        image=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        fps=cap.get(cv2.CAP_PROP_FPS)
        if c==0:
            initialize(fps)
        c+=1
        results=pose.process(image)
        mp_drawing.draw_landmarks(image,results.pose_landmarks,mp_pose.POSE_CONNECTIONS)
        try:
            landmarks=results.pose_landmarks.landmark
        except:
            pass

        leftshoulder=[landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        rightshoulder=[landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x]
        leftelbow=[landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        rightelbow=[landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        leftwrist=[landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        rightwrist=[landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        if left(landmarks) or right(landmarks):
            repcounter(leftshoulder,leftelbow,leftwrist,rightshoulder,rightelbow,rightwrist,image,fps)
        else:
            cv2.putText(image,'please bring your arms in frame',(10,50),font,1,(0,0,0),2,cv2.LINE_4)
        cv2.putText(image,'total reps: '+str(counter),(10,100),font,1,(0,0,0),2,cv2.LINE_4)
        newimage=cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
        cv2.imshow('far',newimage)
        if cv2.waitKey(10) & 0xFF==ord('q'):
            break
for lnd in mp_pose.PoseLandmark:
    print(lnd)
cap.release()
cv2.destroyAllWindows()
