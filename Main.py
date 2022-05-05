from multiprocessing import Queue
from threading import*
import re
import json,requests
import urllib.request
from PyQt5.QtGui import QPixmap,QFont
from PyQt5.QtWidgets import QApplication,QWidget,QSplashScreen,\
    QStackedLayout,QFrame,QFormLayout,QLineEdit,QPushButton,QLabel,QComboBox,QDateEdit,QMessageBox,QErrorMessage,\
    QMainWindow,QMenuBar,QGridLayout,QFileDialog
from PyQt5.QtCore import Qt,QTimer
from PyQt5 import QtGui
from qtwidgets import PasswordEdit
from FaultCodes import FaultCodes
import os
import sys
import time

import requests
import urllib.request
import time
import webbrowser
from datetime import datetime
import Resources

import cv2
import mediapipe as mp


mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose(enable_segmentation=True,model_complexity=2)


#CALCULATE SWING 
def SWING(VideoFilepath):
    cap = cv2.VideoCapture(VideoFilepath)
    count=0
    print('Working on : '+VideoFilepath)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count/fps
    cnt = duration/frame_count

    width = int(cap. get(cv2. CAP_PROP_FRAME_WIDTH ))
    height = int(cap. get(cv2. CAP_PROP_FRAME_HEIGHT))

    frame_number=0
    prev_frame_number=0
    step_count=0

    left_previous = 0
    right_previous = 0
    initial_left_frame = 0
    initial_right_frame = 0
    final_left_frame=0
    final_right_frame=0

    SWING=0

    while True:
        success, img = cap.read()
        frame_number+=1
        if not success:
            break
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        # print(results.pose_landmarks)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            h, w, c = img.shape
            rightheel = results.pose_landmarks.landmark[30].x*w
            leftheel = results.pose_landmarks.landmark[29].x*w

            RDIFF = int(rightheel-right_previous)
            LDIFF = int(leftheel-left_previous )
            
            if LDIFF>1:
                count+=1
                initial_left_frame=frame_number
                
            left_previous=leftheel  
            
            if RDIFF>1:
                count+=1
                initial_right_frame=frame_number
                
            right_previous=rightheel
            SWING = round(count*cnt,2)
        # cv2.putText(img, str('Swing : ')+str(SWING) +str('s'), (50, 50), cv2.FONT_HERSHEY_PLAIN, 2,(255, 0, 0), 3)
        # result.write(img)
        cv2.imshow("Image", img)
        cv2.waitKey(1)

    print('Swing : '+str(SWING) +' s')
    cap.release()
    # result.release()
    cv2.destroyAllWindows()
    return SWING




#CALCULATE VELOCITY
def VELOCITY(VideoFilepath):

    cap = cv2.VideoCapture(VideoFilepath)
    # 170cms is the person height, 10cms is the height from eye to tip of head  
    PERSON_HEIGHT = float(170)-10

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count/fps

    # result = cv2.VideoWriter('StepLength2.mp4', 
    #                          cv2.VideoWriter_fourcc(*'mp4v'),
    #                          10, (1200,600))

    frame_number=0
    init_pos_left_ankle = 0
    init_pos_right_ankle = 0

    print('Working on : '+VideoFilepath)

    height_eyetofoot=0

    while True:
        success, img = cap.read()
        if not success:
            break
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        # print(results.pose_landmarks)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            h, w, c = img.shape
            right_ankle = results.pose_landmarks.landmark[30]
            left_ankle = results.pose_landmarks.landmark[29]

            init_right = int(right_ankle.y*h)
            init_left = int(left_ankle.y*h)
            init_pos_left_ankle = int(left_ankle.x*w)
            init_pos_right_ankle = int(right_ankle.x*w)

            rightheel = results.pose_landmarks.landmark[30]
            right_eye_outer =  results.pose_landmarks.landmark[6]
            height_eyetofoot = abs(rightheel.y-right_eye_outer.y)*h
            break


    while True:
        success, img = cap.read()
        if not success:
            break
        frame_number+=1
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        # print(results.pose_landmarks)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            h, w, c = img.shape
            right_ankle = results.pose_landmarks.landmark[30]
            left_ankle = results.pose_landmarks.landmark[29]

            right_step_length=abs(right_ankle.x*w - init_pos_right_ankle)
            right_step_length_incms = round((right_step_length*PERSON_HEIGHT)/height_eyetofoot,2)
            right_velocity = right_step_length_incms/(frame_number*duration/frame_count)
            right_velocity = round(right_velocity/100,2)

            left_step_length=abs(left_ankle.x*w - init_pos_left_ankle)
            left_step_length_incms = round((left_step_length*PERSON_HEIGHT)/height_eyetofoot,2)
            left_velocity = left_step_length_incms/(frame_number*duration/frame_count)
            left_velocity = round(left_velocity/100,2)

            cv2.putText(img,'L Velocity:'+ str(left_velocity)+'m/s', (70, 100), cv2.FONT_HERSHEY_PLAIN, 2,
                    (255, 0, 0), 3)   

            cv2.putText(img,'R Velocity:'+ str(right_velocity)+'m/s', (70, 50), cv2.FONT_HERSHEY_PLAIN, 2,
                    (255, 0, 0), 3)   

        # result.write(img)
        cv2.imshow("Image", img)
        cv2.waitKey(1)

    print('Duration : '+str(duration))
    print('Left Velocity : '+str(left_velocity)+'m/s')
    print('Right Velocity : '+str(right_velocity)+'m/s')

    cap.release()
    # result.release()
    cv2.destroyAllWindows()

    return (left_velocity,right_velocity)



def STRIDE_DURATION(VideoFilepath):

    cap = cv2.VideoCapture(VideoFilepath)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count/fps
    cnt = duration/frame_count
    width = int(cap. get(cv2. CAP_PROP_FRAME_WIDTH ))
    height = int(cap. get(cv2. CAP_PROP_FRAME_HEIGHT))

    #result = cv2.VideoWriter(VideoFilepath[-10:],cv2.VideoWriter_fourcc(*'mp4v'),10, (width,height))

    print('Working on : '+VideoFilepath)

    LCOUNT=0
    RCOUNT=0
    right_prev_step=0
    left_prev_step=0
    frame_number=0
    prev_frame_number=0
    left_previous = 0
    right_previous = 0
    initial_left_frame = 0
    initial_right_frame = 0
    final_left_frame=0
    final_right_frame=0
    LSTRIDE_DURATION= 0
    RSTRIDE_DURATION=0


    while True:
        success, img = cap.read()
        frame_number+=1
        if not success:
            break
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            h, w, c = img.shape
            rightheel = results.pose_landmarks.landmark[30].x*w
            leftheel = results.pose_landmarks.landmark[29].x*w
            left_prev_step=leftheel
            right_prev_step=rightheel
            break

    while True:
        success, img = cap.read()
        frame_number+=1
        if not success:
            break
        
            
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            h, w, c = img.shape
            rightheel = results.pose_landmarks.landmark[30].x*w
            leftheel = results.pose_landmarks.landmark[29].x*w
            
            RDIFF = int(rightheel-right_previous)
            LDIFF = int(leftheel-left_previous )
            step_count = LCOUNT+RCOUNT
            
            
            if LDIFF==0 and frame_number-initial_left_frame>10 and leftheel-left_prev_step>20:
                LCOUNT+=1
               # cv2.waitKey(500)
                # if LCOUNT==RCOUNT+1:
                LSTRIDE_DURATION = ((frame_number-initial_left_frame)*cnt)
                LSTRIDE_DURATION= round(LSTRIDE_DURATION,4)

                print('LCOUNT: '+str(LCOUNT)+'  LSTRIDE_DURATION: '+str(LSTRIDE_DURATION))
                
                initial_left_frame=frame_number
                left_prev_step=leftheel    
            left_previous=leftheel  
            
        
            if RDIFF==0 and frame_number-initial_right_frame>10 and rightheel-right_prev_step>20:
                RCOUNT+=1
                # if RCOUNT==LCOUNT+1:

                RSTRIDE_DURATION = ((frame_number-initial_right_frame)*cnt)
                RSTRIDE_DURATION= round(RSTRIDE_DURATION,4)
                
                print('RCOUNT: '+str(RCOUNT)+'  RSTRIDE_DURATION: '+str(RSTRIDE_DURATION))
                initial_right_frame=frame_number
                right_prev_step=rightheel
            right_previous=rightheel


        cv2.putText(img, str('LSTRIDE_DURATION: ') + str(LSTRIDE_DURATION)+'s', (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), 3)
        cv2.putText(img, str('RSTRIDE_DURATION: ') + str(RSTRIDE_DURATION)+'s', (70, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), 3)
        #result.write(img)
        #img = cv2.resize(img, (1200,600))
        cv2.imshow("Image", img)
        cv2.waitKey(1)

    cap.release()
    #result.release()
    cv2.destroyAllWindows()

    return (LSTRIDE_DURATION,RSTRIDE_DURATION)


def STEP_DURATION(VideoFilepath):

    cap = cv2.VideoCapture(VideoFilepath)
    print('Working on : '+VideoFilepath)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count/fps
    cnt = duration/frame_count
    width = int(cap. get(cv2. CAP_PROP_FRAME_WIDTH ))
    height = int(cap. get(cv2. CAP_PROP_FRAME_HEIGHT))

    LSTEP_DURATION=0
    RSTEP_DURATION=0
    frame_number=0
    prev_frame_number=0
    height_eyetofoot=0
    left_previous = 0
    right_previous = 0
    initial_left_frame = 0
    initial_right_frame = 0
    right_prev_step=0
    left_prev_step=0

    while True:
        success, img = cap.read()
        frame_number+=1
        if not success:
            break
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            h, w, c = img.shape
            rightheel = results.pose_landmarks.landmark[30].x*w
            leftheel = results.pose_landmarks.landmark[29].x*w
            left_prev_step=leftheel
            right_prev_step=rightheel
            break


    while True:
        success, img = cap.read()
        frame_number+=1
        if not success:
            break
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            h, w, c = img.shape
            rightheel = int(results.pose_landmarks.landmark[30].x*w)
            leftheel = int(results.pose_landmarks.landmark[29].x*w)
            step_length = abs(rightheel-leftheel)

            RDIFF = int(rightheel-right_previous)
            LDIFF = int(leftheel-left_previous )
            
            if LDIFF==0 and frame_number-initial_left_frame>10 and leftheel-left_prev_step>20:
                LSTEP_DURATION = round((frame_number-initial_left_frame)*cnt,2)
                print('LSTEP_DURATION : '+str(LSTEP_DURATION)+'s')
                initial_left_frame=frame_number
                left_prev_step=leftheel    
                
            left_previous=leftheel  

            if RDIFF==0 and frame_number-initial_right_frame>10 and rightheel-right_prev_step>20:
                RSTEP_DURATION = round((frame_number-initial_right_frame)*cnt,2)
                print('RSTEP_DURATION : '+str(RSTEP_DURATION)+'s')
                initial_right_frame=frame_number
                right_prev_step=rightheel
                
            right_previous=rightheel

        cv2.putText(img, str('L STEP DURATION: ') + str(LSTEP_DURATION), (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), 3)
        cv2.putText(img, str('R STEP DURATION: ') + str(RSTEP_DURATION), (70, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), 3)
        # result.write(img)
        # img = cv2.resize(img, (1200,600))
        cv2.imshow("Image", img)
        cv2.waitKey(1)


    cap.release()
    # result.release()
    cv2.destroyAllWindows()



def SST_DST_STANCE(VideoFilepath):

    cap = cv2.VideoCapture(VideoFilepath)
    right_count=0
    left_count=0
    count=0

    print('Working on : '+VideoFilepath)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count/fps
    cnt = duration/frame_count

    width = int(cap. get(cv2. CAP_PROP_FRAME_WIDTH ))
    height = int(cap. get(cv2. CAP_PROP_FRAME_HEIGHT))

    # result = cv2.VideoWriter('SST with '+VideoFilepath[-9:], cv2.VideoWriter_fourcc(*'mp4v'),20, (width,height))
    frame_number=0
    prev_frame_number=0
    step_count=0

    left_previous = 0
    right_previous = 0
    initial_left_frame = 0
    initial_right_frame = 0
    right_prev_step=0
    left_prev_step=0

    while True:
        success, img = cap.read()
        frame_number+=1
        if not success:
            break
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        # print(results.pose_landmarks)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            h, w, c = img.shape
            rightheel = int(results.pose_landmarks.landmark[30].x*w)
            leftheel = int(results.pose_landmarks.landmark[29].x*w)

            RDIFF = int(rightheel-right_previous)
            LDIFF = int(leftheel-left_previous )
            
            # if LDIFF<5 and leftheel-left_prev_step>20:
            if LDIFF<=0.5:
                left_count+=1
                initial_left_frame=frame_number
                
            left_previous=leftheel  
            if RDIFF<=0.5:
            # if RDIFF<5 and rightheel-right_prev_step>20:
                # print(RDIFF)
                # print(rightheel,right_previous, RDIFF)
                right_count+=1
                initial_right_frame=frame_number
                
            right_previous=rightheel

            if LDIFF<=1 and RDIFF<=1:
                count+=1

            SSTRIGHT = round(right_count*cnt,2)
            SSTLEFT = round(left_count*cnt,2)
            DST = round(count*cnt,2)
            STANCE=max(SSTRIGHT,SSTLEFT)
        cv2.putText(img, str('SST Right : ')+str(SSTRIGHT) +str('s'), (70, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), 3)
        cv2.putText(img, str('SST Left : ')+str(SSTLEFT) +str('s'), (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), 3)
        cv2.putText(img, str('DST : ')+str(DST) +str('s'), (70, 150), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), 3)
        cv2.putText(img, str('STANCE : ')+str(STANCE) +str('s'), (70, 200), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), 3)

        # result.write(img)
        cv2.imshow("Image", img)
        cv2.waitKey(1)

    print('Video Duration : '+str(duration))
    print('SST Right : '+str(SSTRIGHT))
    print('SST Left : '+str(SSTLEFT))
    print('DST : '+str(DST))
    print('STANCE : '+str(STANCE))
    cap.release()
    # result.release()
    cv2.destroyAllWindows()




def NUM_STEPS_AND_STEP_LENGTH(VideoFilepath):
    cap = cv2.VideoCapture(VideoFilepath)

    # 185cms is the person height, 10cms is the height from eye to tip of head 
    PERSON_HEIGHT = float(185)-10

    print('Working on : '+VideoFilepath)

    cap = cv2.VideoCapture(VideoFilepath)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count/fps
    cnt = duration/frame_count
    width = int(cap. get(cv2. CAP_PROP_FRAME_WIDTH ))
    height = int(cap. get(cv2. CAP_PROP_FRAME_HEIGHT))

    ANS_ARRAY = []

    LCOUNT=0
    RCOUNT=0
    cadence = 0
    frame_number=0
    prev_frame_number=0
    step_count=0
    height_eyetofoot=0
    left_previous = 0
    right_previous = 0
    initial_left_frame = 0
    initial_right_frame = 0
    final_left_frame=0
    final_right_frame=0
    right_prev_step=0
    left_prev_step=0

    while True:
        success, img = cap.read()
        frame_number+=1
        if not success:
            break
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            h, w, c = img.shape
            rightheel = results.pose_landmarks.landmark[30]
            leftheel = results.pose_landmarks.landmark[29].x*w
            right_eye_outer =  results.pose_landmarks.landmark[6]
            left_prev_step=leftheel
            right_prev_step=rightheel.x*w
            height_eyetofoot = abs(rightheel.y-right_eye_outer.y)*h
            break


    while True:
        success, img = cap.read()
        frame_number+=1
        if not success:
            break
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            h, w, c = img.shape
            rightheel = int(results.pose_landmarks.landmark[30].x*w)
            leftheel = int(results.pose_landmarks.landmark[29].x*w)
            step_length = abs(rightheel-leftheel)

            RDIFF = int(rightheel-right_previous)
            LDIFF = int(leftheel-left_previous )
            
            if LDIFF==0 and frame_number-initial_left_frame>10 and leftheel-left_prev_step>20:
                LCOUNT+=1
                initial_left_frame=frame_number
                step_length = abs(leftheel-left_prev_step)
                left_prev_step=leftheel    
                
                step_length_incms = round((step_length*PERSON_HEIGHT)/height_eyetofoot,2)
                ANS_ARRAY.append(step_length_incms)
                print(step_length_incms)
            left_previous=leftheel  

            if RDIFF==0 and frame_number-initial_right_frame>10 and rightheel-right_prev_step>20:
                RCOUNT+=1
                initial_right_frame=frame_number
                step_length = abs(rightheel-right_prev_step)
                right_prev_step=rightheel
                
                step_length_incms = round((step_length*PERSON_HEIGHT)/height_eyetofoot,2)
                ANS_ARRAY.append(step_length_incms)
                print(step_length_incms)
            right_previous=rightheel

            step_count=LCOUNT+RCOUNT
        
        cadence = int(((step_count)*60)/duration)

        cv2.putText(img, str('STEPS: ') + str(round(step_count)), (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), 3)
        cv2.putText(img, str('CADENCE: ') + str(cadence)+str('steps/min'), (70, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), 3)
        # result.write(img)
        img = cv2.resize(img, (1200,600))
        cv2.imshow("Image", img)
        cv2.waitKey(1)

    plt.plot(ANS_ARRAY)

    #PLEASE MENTION THE CUSTOM FOLDER PATH WHERE YOU WANT TO SAVE THE PLOTS 

    plt.savefig('./'+VideoFilepath.split('.m')[0][-5:] +'.png')    
    plt.show()

    AVERAGE_STEP_LENGTH = sum(ANS_ARRAY)/len(ANS_ARRAY)

    print('step_count : '+str(step_count))
    print('cadence : '+str(cadence))
    print('AVERAGE_STEP_LENGTH : '+str(AVERAGE_STEP_LENGTH))

    cap.release()
    # result.release()
    cv2.destroyAllWindows()


# SWING(VideoFilepath)
# SST_DST_STANCE(VideoFilepath)
# VELOCITY(VideoFilepath)
# NUM_STEPS_AND_STEP_LENGTH(VideoFilepath)
# STEP_DURATION(VideoFilepath)
# STRIDE_DURATION(VideoFilepath)



FUNCTIONS_DICTIONARY = {
    'GET_SWING' : SWING,
    'GET_SST_DST_STANCE' : SST_DST_STANCE,
    'GET_NUM_STEPS_AND_STEP_LENGTH' : NUM_STEPS_AND_STEP_LENGTH,
    'GET_STEP_DURATION' : STEP_DURATION,
    'GET_STRIDE_DURATION' : STRIDE_DURATION

}



def UserRegistratiion(data):
    #try:

        user_detail = open('user_detail.json')
        DatabaseData = json.load(user_detail)
        for UID in DatabaseData:
            if data["UserID"] == UID['UserID']:
                return "100"

        # check the userid contains any special characters.
        if data["UserID"].isalnum() == False:
            return "101"

        # checks the Name is empty or not
        if not data["UserName"]:
            return "102"

        # checks the Name contains any numbers or characters.
        if data["UserName"].isalpha() == False:
            return "103"

        # Validates the mail id format
        pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        if not re.match(pattern, data["UserEmail"]):
            return "104"

        # validates the mail id is empty or not.
        if not data["UserEmail"]:
            return "105"

        # checks the Gender is selected or not.
        if not data["UserGender"]:
            return "106"

        # checks the valid DOB is given or not.
        day, month, year = data["UserDoB"].split('/')

        isValidDate = True
        try:
            datetime.datetime(int(year), int(month), int(day))

        except ValueError:
            isValidDate = False
        if isValidDate == False:
            return "107"

        # Validate the password is empty or not.
        if not data["UserPswd"]:
            return "108"

        # validate the password is valid or not.
        lower, upper, special, digit = 0, 0, 0, 0
        pwd = data["UserPswd"]
        if (len(pwd) >= 6):
            for i in pwd:
                for word in pwd.split():
                    if (word[0].isupper()):
                        upper += 1
                    if (i.islower()):
                        lower += 1
                    if (i.isdigit()):
                        digit += 1
                    if (i == '@' or i == '$' or i == '_' or i == '#'):
                        special += 1
        else:
            return "109"
        if not (lower >= 1 and upper >= 1 and special >= 1 and digit >= 1):
            return "110"

        if str(UserCnfPswd.text()).strip() != data["UserPswd"]:
            return "112"

        # updating the json file with details
        with open("user_detail.json", "w") as databaseFile:
            DatabaseData.append(data)
            json.dump(DatabaseData, databaseFile)
            return "000"
    #except Exception as error: return str(error)



def showUserInfo(message):
   msgBox = QMessageBox()
   msgBox.setIcon(QMessageBox.Information)
   msgBox.setText(message)
   msgBox.setWindowTitle("Status Update")
   msgBox.setStandardButtons(QMessageBox.Ok)
   msgBox.show()
   returnValue = msgBox.exec()
   if returnValue == QMessageBox.Ok: pass
   else: pass

try:
    if __name__ == "__main__":

        def Authenticate_Login():
            UserID = UserIDInput.text().upper().strip()
            UserPswd = UserPassword.text().strip()

            if UserID == "ADMIN" and UserPswd == "admin123":
                Switch_Screenpage(2)
            else : error_dialog.showMessage("Invalid Credentials , Please re-try")


        Aplication = QApplication(sys.argv)
        MainWindowGUI = QWidget()
        #MainWindowGUI.setFixedSize(1600, 800)
        MainWindowGUI.setWindowTitle('GAIT AiMA')
        MainWindowGUI.setStyleSheet("background-color: black;")
        MainWindowGUI.setObjectName("MainMenu");
        IconFilepath = ":/resources/AI_Volved.ico"
        MainWindowGUI.setStyleSheet("QWidget#MainMenu{background-image: url(:/resources/Wallpaper6.jpg);}");
        MainWindowGUI.setWindowIcon(QtGui.QIcon(IconFilepath))
        splash = QSplashScreen(QPixmap(':/resources/Splashscreen.jpg'))
        splash.show()
        splash.showMessage('<h1 style="color:white; font-size: 1px;font-family: "Times New Roman", Times, serif;">Loading ..</h1>',
                           Qt.AlignBottom | Qt.AlignRight)
        time.sleep(3)
        QTimer.singleShot(0, splash.close)

        def Switch_Screenpage(pageNum):
            try:
                if pageNum ==1:
                    MainWindowGUI.setStyleSheet("QWidget#MainMenu{background-image: url(:/resources/Wallpaper8.jpg);}");
                elif pageNum==0:
                    MainWindowGUI.setStyleSheet("QWidget#MainMenu{background-image: url(:/resources/Wallpaper6.jpg);}");
                elif pageNum==2:
                    MainWindowGUI.setStyleSheet\
                        ("QWidget#MainMenu{background-image: url(:/resources/Deep Sea Space.jpg);}");

                stackedLayout_MainApp.setCurrentIndex(pageNum)
            except Exception as error : print(error)

        stackedLayout_MainApp = QStackedLayout(MainWindowGUI)

        LoginPage = QFrame(MainWindowGUI)
        LoginPageLayout = QFormLayout()

        UserIDInput = QLineEdit(LoginPage)
        UserIDInput.setFixedSize(280,53)
        UserIDInput.setClearButtonEnabled(True)
        UserIDInput.setPlaceholderText("User ID")
        UserIDInput.setFont(QFont("Segoe UI ", 10, ))
        UserIDInput.setStyleSheet("QLineEdit {border: 1px solid #075691;border-radius: 5px;color: #103560 ;}""QLineEdit:focus{border: 2px solid green;}")
        UserIDInput.move(900,350)


        UserPassword = QLineEdit(LoginPage)
        UserPassword.setFixedSize(280,53)
        UserPassword.move(900, 420)
        UserPassword.setClearButtonEnabled(True)
        UserPassword.setFont(QFont("Segoe UI ", 10))
        UserPassword.setPlaceholderText("User Password")
        UserPassword.setStyleSheet("QLineEdit {border: 1px solid #075691;border-radius: 5px;color: #103560 ;}""QLineEdit:focus{border: 2px solid green;}")
        UserPassword.setEchoMode(QLineEdit.Password)


        SingInButton = QPushButton("Login",LoginPage)
        SingInButton.move(910, 550)
        SingInButton.setFixedSize(250,45)
        SingInButton.setFont(QFont("Segoe UI ", 10, ))
        SingInButton.setStyleSheet("QPushButton {border: 1px blue;border-radius: 5px;  background-color: #075691; color : white;}""QPushButton::hover"
                                 "{"
                                 "background-color : #1a85b4;"
                                 "}")

        SingInButton.pressed.connect(Authenticate_Login)

        ButtonSignINRegisterUser = QPushButton("Register User",LoginPage)
        ButtonSignINRegisterUser.move(910, 610)
        ButtonSignINRegisterUser.setFixedSize(250,45)
        ButtonSignINRegisterUser.setFont(QFont("Segoe UI ", 10, ))
        ButtonSignINRegisterUser.setStyleSheet("QPushButton {border: 1px blue;border-radius: 5px;  background-color: #075691;color : white;}""QPushButton::hover"
                                 "{"
                                 "background-color : #1a85b4;"
                                 "}")
        ButtonSignINRegisterUser.pressed.connect(lambda : Switch_Screenpage(1))



        ForgotPassword = QPushButton("Forgot Password ?", LoginPage)
        ForgotPassword.move(980, 475)
        ForgotPassword.setFixedSize(250, 45)
        ForgotPassword.setFont(QFont("Segoe UI ", 9 ))
        ForgotPassword.setStyleSheet("QPushButton{background: transparent;color : #075691}""QPushButton::hover"
                                 "{"
                                 "color : #1a85b4;"
                                 "}")


        LoggedInPage_Dr = QFrame(MainWindowGUI)
        LoggedInPage_Dr.styleSheet()

        RegistrationPage = QFrame(MainWindowGUI)
        RegistrationPage_RegForm = QFrame(RegistrationPage)
        RegistrationPage_RegForm.move(860, 350)
        RegistrationPage_RegForm.setFixedSize(800, 800)

        RegistrationPageLayout = QFormLayout(RegistrationPage_RegForm)
        RegistrationPageLayout.setHorizontalSpacing(50)

        RegistrationFormStyleSheet = "QLineEdit " \
                                     "{border: 1px solid #075691;" \
                                     "border-radius: 5px;" \
                                     "color: #103560 ;color:#075691;}"\
                                     "QLineEdit:focus" \
                                     "{border: 2px solid green;}"
        def style_RegSheet(element):
            element.setFixedSize(285, 40)
            element.setStyleSheet(RegistrationFormStyleSheet)
            element.setFont(QFont("Segoe UI ", 12, ))


        def style_RegSheetQLabel(text):
            Label = QLabel(text)
            Label.setAlignment(Qt.AlignCenter | Qt.AlignLeft)
            Label.setStyleSheet('color:#075691')
            Label.setFont(QFont("Segoe UI ", 12 ))
            return Label

        UserID = QLineEdit()
        UserID.setClearButtonEnabled(True)
        style_RegSheet(UserID)

        RegistrationPageLayout.addRow(style_RegSheetQLabel("User ID"), UserID)
        UserName = QLineEdit()
        UserName.setClearButtonEnabled(True)
        style_RegSheet(UserName)
        RegistrationPageLayout.addRow(style_RegSheetQLabel("Full Name"), UserName)
        UserEmail = QLineEdit()
        UserEmail.setClearButtonEnabled(True)
        style_RegSheet(UserEmail)
        RegistrationPageLayout.addRow(style_RegSheetQLabel("Email ID"), UserEmail)
        UserGender = QComboBox()
        UserGender.setFont(QFont("Segoe UI ", 12))

        UserGender.setStyleSheet("QComboBox"
                                    "{""border : 1px solid #075691; color : #075691""}"
                                 "QComboBox:focus"
                                    "{" "border : 2px solid green;""}")

        UserGender.setFixedSize(285, 40)
        UserGender.setFont(QFont("Segoe UI ", 12 ))
        UserGender.addItems(["Male" ,"Female","Other"])
        UserGender.setCurrentText(" ")
        RegistrationPageLayout.addRow(style_RegSheetQLabel("Gender"), UserGender)

        UserDoB = QDateEdit(calendarPopup=True)
        UserDoB.setFixedSize(285, 40)
        UserDoB.setFont(QFont("Segoe UI ", 12))
        UserDoB.setStyleSheet("QDateEdit"
                              "{"
                              "border : 1px solid #075691; color : #075691"

                              "}"
                              "QDateEdit:focus"
                              "{"
                              "border : 2px solid green;"
                              "}"  )
        RegistrationPageLayout.addRow(style_RegSheetQLabel("Date of birth"), UserDoB)

        UserPswd = QLineEdit()
        UserPswd.setClearButtonEnabled(True)
        UserPswd.setEchoMode(QLineEdit.Password)
        style_RegSheet(UserPswd)
        RegistrationPageLayout.addRow(style_RegSheetQLabel("Password"), UserPswd)
        UserCnfPswd = PasswordEdit()
        UserCnfPswd.setClearButtonEnabled(True)
        style_RegSheet(UserCnfPswd)
        UserCnfPswd.setEchoMode(QLineEdit.Password)
        RegistrationPageLayout.addRow(style_RegSheetQLabel("Confirm Password"), UserCnfPswd)





        ButtonRegisterUser = QPushButton("Register", RegistrationPage)
        ButtonRegisterUser.move(1080, 720)
        ButtonRegisterUser.setFixedSize(150, 53)
        ButtonRegisterUser.setFont(QFont("Segoe UI ", 10, ))
        ButtonRegisterUser.setStyleSheet(
            "QPushButton {border: 1px blue;border-radius: 5px;  background-color: #075691;color : white;}""QPushButton::hover"
            "{"
            "background-color : #1a85b4;"
            "}")

        error_dialog = QErrorMessage(MainWindowGUI)

        def Call_UserRegistration():
            try:
                UserData = {
                    "UserID": str(UserID.text()).strip().upper(),
                    "UserName": str(UserName.text()).strip().upper(),
                    "UserEmail": str(UserEmail.text()).strip().upper(),
                    "UserGender": str(UserGender.currentText()).strip().upper(),
                    "UserDoB": str(UserDoB.text()).strip().upper(),
                    "UserPswd": str(UserPswd.text()).strip().upper(),
                }
                print(UserData)


                try:
                    Acknowledgment = UserRegistratiion(UserData)
                except Exception as error :
                    Acknowledgment = str(error)

                if Acknowledgment != "000":
                    try:
                        error_dialog.showMessage(FaultCodes[int(Acknowledgment)])
                    except : error_dialog.showMessage(str(Acknowledgment))


            except Exception as error : print(error)


        ButtonRegisterUser.pressed.connect(Call_UserRegistration)

        ButtonRegisterUserCancel = QPushButton("Cancel", RegistrationPage)
        ButtonRegisterUserCancel.move(1260, 720)
        ButtonRegisterUserCancel.setFixedSize(100, 53)
        ButtonRegisterUserCancel.setFont(QFont("Segoe UI ", 10, ))
        ButtonRegisterUserCancel.setStyleSheet(
            "QPushButton {border: 1px blue;border-radius: 5px;  background-color: #075691;color : white;}""QPushButton::hover"
            "{"
            "background-color : #1a85b4;"
            "}"\
            )
        ButtonRegisterUserCancel.pressed.connect(lambda: Switch_Screenpage(0))


        def Arbitrate_loggedInScreensDr(page):
            global stackedLayout_Frm_H_Right_LoggedInPage_Dr
            stackedLayout_Frm_H_Right_LoggedInPage_Dr.setCurrentIndex(page)

        Frm_H_Left_LoggedInPage_Dr = QFrame(LoggedInPage_Dr)
        Frm_H_Left_LoggedInPage_Dr.setFrameShape(QFrame.NoFrame)
        Frm_H_Left_LoggedInPage_Dr.setFixedWidth(280)

        PatientDiagnosisButton = QPushButton("Clinical Diagnosis",Frm_H_Left_LoggedInPage_Dr)
        PatientDiagnosisButton.move(25, 50)
        PatientDiagnosisButton.setFixedSize(220,45)
        PatientDiagnosisButton.setFont(QFont("Segoe UI ", 10, ))
        PatientDiagnosisButton.setStyleSheet("QPushButton \
                                                {border: 1px blue;border-radius: 5px;  \
                                                 background-color: #075691; color : white;}"\
                                             "QPushButton::hover"
                                                "{""background-color : #1a85b4;" "}"
                                             "QPushButton::QPushButton:checked"\
                                             "{"" border: none;" "}" \
                                             "QPushButton::focus" \
                                             "{""background-color : #327A92;" "}"
                                             )
        PatientDiagnosisButton.pressed.connect(lambda: Arbitrate_loggedInScreensDr(0))




        PatientRegButton = QPushButton("Patient registration",Frm_H_Left_LoggedInPage_Dr)
        PatientRegButton.move(25, 120)
        PatientRegButton.setFixedSize(220,45)
        PatientRegButton.setFont(QFont("Segoe UI ", 10, ))
        PatientRegButton.setStyleSheet("QPushButton {border: 1px blue;border-radius: 5px;  background-color: #075691; color : white;}""QPushButton::hover"
                                 "{"
                                 "background-color : #1a85b4;"
                                 "}" \
                                       "QPushButton::focus" \
                                       "{""background-color : #327A92;" "}"
                                       )

        PatientRegButton.pressed.connect(lambda: Arbitrate_loggedInScreensDr(1))

        PatientRepAnlsButton = QPushButton("Reports analysis",Frm_H_Left_LoggedInPage_Dr)
        PatientRepAnlsButton.move(25, 190)
        PatientRepAnlsButton.setFixedSize(220,45)
        PatientRepAnlsButton.setFont(QFont("Segoe UI ", 10, ))
        PatientRepAnlsButton.setStyleSheet("QPushButton {border: 1px blue;border-radius: 5px;  background-color: #075691; color : white;}""QPushButton::hover"
                                 "{"
                                 "background-color : #1a85b4;"
                                 "}" \
                                           "QPushButton::focus" \
                                           "{""background-color : #327A92;" "}"
                                           )

        PatientRepAnlsButton.pressed.connect(lambda: Arbitrate_loggedInScreensDr(2))

        Frm_H_Right_LoggedInPage_Dr = QFrame(LoggedInPage_Dr)
        Frm_H_Right_LoggedInPage_Dr.setFrameShape(QFrame.StyledPanel)
        Frm_H_Left_LoggedInPage_Dr.setStyleSheet("#MainFrame { border: 5px solid black; }")
        Frm_H_Right_LoggedInPage_Dr.setStyleSheet("#MainFrame { border: 5px solid black; }")
        #Frm_H_Right_LoggedInPage_Dr.setFixedSize(100,500)

        grid_layout = QGridLayout(LoggedInPage_Dr)
        grid_layout.setHorizontalSpacing(0)
        grid_layout.setVerticalSpacing(0)
        LoggedInPage_Dr.setLayout(grid_layout)
        grid_layout.addWidget(Frm_H_Left_LoggedInPage_Dr, 0, 0)
        grid_layout.addWidget(Frm_H_Right_LoggedInPage_Dr, 0, 1)

        stackedLayout_Frm_H_Right_LoggedInPage_Dr = QStackedLayout(Frm_H_Right_LoggedInPage_Dr)
        ClinicalDiagPage = QFrame()
        PatientRegPage = QFrame()
        ReportsAnlysPage = QFrame()

        InputVidFeed_Button = QPushButton("Browse...",ClinicalDiagPage)
        InputVidFeed_Button.move(700, 50)
        InputVidFeed_Button.setFixedSize(150,45)
        InputVidFeed_Button.setFont(QFont("Segoe UI ", 10, ))
        InputVidFeed_Button.setStyleSheet("QPushButton {border: 1px blue;border-radius: 5px;  \
        background-color: #206075; color : white;}""QPushButton::hover"
                                 "{"
                                 "background-color : #367A90;"
                                 "}")

        def GetVideoPathLocal():
            global VideoFilepath
            VideoFilepath, checkFlag = QFileDialog.getOpenFileName(None, "Select input Video file",
                                    "", "All Files (*);;Avi(*.avi);;Webm (*.webm);;Mp4 (*.mp4);;mpeg (*.mpeg);;.WMV (* .wmv)")
            if checkFlag: 
                pass
                
                #print(FUNCTIONS_DICTIONARY['GET_STEP_DURATION'](VideoFilepath))

        InputVidFeed_Button.pressed.connect(GetVideoPathLocal)

        stackedLayout_Frm_H_Right_LoggedInPage_Dr.addWidget(ClinicalDiagPage)
        stackedLayout_Frm_H_Right_LoggedInPage_Dr.addWidget(PatientRegPage)
        stackedLayout_Frm_H_Right_LoggedInPage_Dr.addWidget(ReportsAnlysPage)
        stackedLayout_Frm_H_Right_LoggedInPage_Dr.setCurrentIndex(0)

        mainMenu = QMenuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        stackedLayout_MainApp.addWidget(LoginPage)
        stackedLayout_MainApp.addWidget(RegistrationPage)
        stackedLayout_MainApp.addWidget(LoggedInPage_Dr)


        MainWindowGUI.showMaximized()
        sys.exit(Aplication.exec_())
except Exception as error : print(error)

