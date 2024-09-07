import cv2
import mediapipe as mp
import numpy as np
import math
mp_drawing=mp.solutions.drawing_utils
mp_pose=mp.solutions.pose

# pushup=0
# pushstage="rest"
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
stage="rest"
hold=5
def initialize(fps):
    global hold
    hold=fps*5
# def pushcounter(a,b,c,d,e,f):
#     global pushup
#     global pushstage
#     angle1=anglecal(a,b,c)
#     angle2=anglecal(d,e,f)
#     radians=np.arctan2(c[1]-b[1],c[0]-b[0])-np.arctan2(a[1]-b[1],a[0]-b[0])
#     angle=np.abs(radians*180.0/np.pi)
#     if angle1>=70.0 and angle1<=110.0 and angle2>=70.0 and angle2<=110.0:
#         pushstage="push"
#     elif pushstage=="push" and angle1>=165.0 and angle2>=165.0:
#         pushstage="rest"
#         pushup+=1
#     return 
def left(landmarks):
    return landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].visibility>=0.4 and landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].visibility>=0.4 

def right(landmarks):
    return  landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].visibility>=0.4 and  landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].visibility>=0.4

def repcounter(a,b,c,d,e,f,image,fps):
    angle1=anglecal(a,b,c)
    angle2=anglecal(d,e,f)
    global stage
    global counter
    global hold
    # sub=1/fps
    if  angle1<=110.0 or angle2<=110.0:
        stage="rest"
        if(hold==0):
            counter+=1
        initialize(fps)
    elif hold==0:
        cv2.putText(image,'relax your legs',(10,50),font,1,(0,0,0),2,cv2.LINE_4)
    elif(angle1>=165.0 or angle2>=165.0) and hold!=0:
        stage="up"
        cv2.putText(image,'hold for '+str(math.ceil(hold/fps))+' sec',(10,50),font,1,(0,0,0),2,cv2.LINE_4)
        # print('here')
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
        #image.flags.writeable=False
        if c==0:
            initialize(fps)
        c+=1
        results=pose.process(image)
        mp_drawing.draw_landmarks(image,results.pose_landmarks,mp_pose.POSE_CONNECTIONS)
        # print(results)
        try:
            landmarks=results.pose_landmarks.landmark
        except:
            pass

        lefthip=[landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        righthip=[landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x]
        leftknee=[landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        rightknee=[landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        leftankle=[landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        rightankle=[landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        # leftshoulder=[landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        # rightshoulder=[landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        # leftelbow=[landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        # rightelbow=[landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        # leftwrist=[landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        # rightwrist=[landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        # cv2.putText(image,str(counter), (250, 250), font, 1,  (0, 255, 255),  2, cv2.LINE_4) 
        # pushcounter(leftshoulder,leftelbow,leftwrist,rightshoulder,rightelbow,rightwrist)
        # print(pushup)
        if left(landmarks) or right(landmarks):
            repcounter(lefthip,leftknee,leftankle,righthip,rightknee,rightankle,image,fps)
        else:
            cv2.putText(image,'please bring your legs in frame',(10,50),font,1,(0,0,0),2,cv2.LINE_4)
        cv2.putText(image,'total reps: '+str(counter),(10,100),font,1,(0,0,0),2,cv2.LINE_4)
        newimage=cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
        cv2.imshow('far',newimage)
        # print(counter)
        if cv2.waitKey(10) & 0xFF==ord('q'):
            break

# print(len(landmarks))
# for lnd in mp_pose.PoseLandmark:
#     print(lnd)
# print(len(mp_pose.POSE_CONNECTIONS))
cap.release()
cv2.destroyAllWindows()
