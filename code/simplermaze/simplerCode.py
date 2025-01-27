import numpy as np
import cv2 as cv
import pandas as pd
import supFun as sf
import time
import serial


#set variable for defining if this is an habituation run:
habituation = True


#set variable for defining if animal should be rewarded in the case
#a wrong location is visited before visiting a correct location:
considerWrongLocations = False


#create a serial object and connect to it
#ser = Serial.serial("/dev/ttyACM0")

drawRois = False
if drawRois:

    sf.define_rois(roiNames = ["entrance1","entrance2",
                            "rew1","rew2","rew3","rew4"],
                    outputName = "rois1.csv")

#load ROI information
rois = pd.read_csv("rois1.csv",index_col=0)

#load the trials file (description of each trial)
trialsIDs = pd.read_csv("trials_2columns.csv")

#set number of trials
nTrials = len(trialsIDs)

#get the identification of each grating
gratingID = [match for match in list(trialsIDs.keys()) if "motor" in match]


#get the number of reward areas
nRewAreas = trialsIDs.ra1.max()


#the maze only uses servo motors. To simplify their control, we are relying on
# an adafruit board (based on the PCA9685 IC), which allows us to flexibly
#increase/decrease the number of motors, without using more ports on a microcontroller,
#since the Adafruit board communicates with a microcontroller using two digital lines, but is
#able to control more than 100 servo motors.

#The board also has C++ and micropython libraries, which makes it easy for users to control them.


# set the port/address for each motor
gratingMotors = {"motor 1":1,
                 "motor 2":2,
                 "motor 3":3,
                 "motor 4":4,
                 "motor 5":5,
                 "motor 6":6,                 
                 }

rewardMotors = {"motor 1":7,
                "motor 2":8,
                "motor 3":9,
                "motor 4":10}




thresholds = dict()
timeSpentAreas = dict()
for item in rois:
    #create threshold values for each area
    thresholds[item] = 0
    #create all roi variables in the dictionary and attach an empty list to them
    timeSpentAreas[item] = np.zeros(nTrials)


#create variables that will store session data
areasRewarded = list()
hits = list()
miss = list()
incorrect = list()

#preload variables
hasVisited = dict()
mousePresent = dict()




#start the camera object
cap = cv.VideoCapture('/home/andre/Desktop/maze_test.mp4')

### START FOR LOOP TO AVERAGE N FRAMES FOR THRESHOLDING

#grab one frame to adjust tresholds of empty spaces:
gray,valid = sf.grab_n_convert_frame(cameraHandle=cap)
ret,gray = cv.threshold(gray,180,255,cv.THRESH_BINARY)
#gray = gray[:,:,0]
#run a loop to catch each area and sum the pixel values on that area of the frame
areas = dict()
for item in rois:
    areas[item] = sf.grab_cut(gray,
                xstart = rois[item]["xstart"],
                ystart =  rois[item]["ystart"],
                xlen = rois[item]["xlen"],
                ylen =  rois[item]["ylen"],
                )
    
    thresholds[item] = np.sum(areas[item])

#print(thresholds)

#cap = sf.start_camera()
#cap = cv.VideoCapture("~/Desktop/maze_test.mp4")



sessionStartTime = time.time()

for trial in range(nTrials):
    print ("starting trial "+str(trial+1))
    #if cv.waitKey(1) == ord('q'):
    #    break
    #which area should be rewarded:
    rewardTarget = trialsIDs["ra1"][trial]
    #define which servo motor should be used for this specific area
    for item in rewardMotors.keys():
        if str(rewardTarget) in item:
            rewMotor = rewardMotors[item]
            break
        else:
            rewMotor = 7
            #print("correct reward motor not found!! defaulting to motor 7")
        
    
    #run code to start the gratings
    for grating in gratingID:
        print(grating)
        #add arduino code here so that all gratings turn to neutral position"
        #ser.print(xxxxxxxx)
    
        #maybe add a pause? so that the servo motors have time to catch up
        
    for grating in gratingID:
        if habituation:
            position = 0
        else:
            position = trialsIDs[grating][trial]
        
        print(position)
        #than add code so that they turn to the trial specific position"
        #maybe add a pause? so that the servo motors have time to catch up
    
    
    for item in rois:
        hasVisited[item] = False 
    
    #ent1 = 0
    #ent2 = 0
    trialOngoing = True
    rewarded = False
    enteredMaze = False
    mistake = False
    hasLeft1 = False
    hasLeft2 = False
    e2Aftere1 = False
    e1Aftere2 = False
    
    
    ent1History = [False,False]
    ent2History = [False,False]
    while trialOngoing:
        
        #the line below needs to be commented out when running the actual experiments
        time.sleep(0.05)
        
        gray,valid = sf.grab_n_convert_frame(cameraHandle=cap)
        ret,gray = cv.threshold(gray,180,255,cv.THRESH_BINARY)
        #binGray = gray[:,:,2]
        
        if not valid:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        #display rois on top of the frame for user feedback
        for item in rois:
            cv.rectangle(gray, (rois[item]["xstart"],
                                rois[item]["ystart"]),
                               (rois[item]["xstart"]+rois[item]["xlen"],
                                rois[item]["ystart"]+rois[item]["ylen"]),
                           color=(0,0,0), thickness=2)

        # Display the resulting frame
        cv.imshow('frame', gray)
        
        if cv.waitKey(1) == ord('q'):
            break
        
        #grab each area of interest and store them in a dictionary
        #this will be used to detect if the animal was there or not
        for item in rois:
            areas[item] = sf.grab_cut(gray,
                xstart = rois[item]["xstart"],
                ystart =  rois[item]["ystart"],
                xlen = rois[item]["xlen"],
                ylen =  rois[item]["ylen"],
                )
            
            cv.imshow(item,areas[item])
            #print(item+" " + str(np.sum(areas[item])))
    
            mousePresent[item] = np.sum(areas[item])<thresholds[item]/2
            
            if mousePresent[item]:
                hasVisited[item] = True
                #timeSpentAreas[item] = time.time()
            #print(item+" "+str(np.sum(areas[item])))
        
        #here we define the logic for this training step
        #this step only cares if the animal reaches the correct area
        #no matter if it entered a wrong area before
        #stillOnEnt1 = 0
        #stillOnEnt2 = 0
        #startEnt1 = time.time()
        
    
        #at each new frame, add the information on whether the mouse
        #was in the Ent1 area to a two element list
        #every new added item goes in front of the list, and the last
        #element is removed.
        ent1History.insert(0,mousePresent["entrance1"])
        ent1History.pop(-1)
        #print(ent1History)
        
        #at each new frame, add the information on whether the mouse
        #was in the Ent2 area to a two element list
        #every new added item goes in front of the list, and the last
        #element is removed.
        ent2History.insert(0,mousePresent["entrance2"])
        ent2History.pop(-1)

        
            
        #calculate the mouse movement based on the Ent1 array history
        # and determine if it has passed Ent1 and/or 2 and in which direction
        if not ent1History[0] and ent1History[1]:
            #print("mouse just left entrance1")
            endEnt1 = time.time()
            #timeSpentAreas["entrance1"].append(trial,endEnt1-startEnt1)
            #Ent1Durations.append((trial,endEnt1-startEnt1))
            hasLeft1 = True
            if hasLeft2:
                e1Aftere2 = True
                e2Aftere1 = False
                
            
        #calculate the mouse movement based on the Ent2 array history
        if not ent2History[0] and ent2History[1]:
            #print("mouse just left entrance2")
            hasLeft2 = True
            if hasLeft1:
                e1Aftere2 = False
                e2Aftere1 = True
                

        
        if e2Aftere1 and enteredMaze==False:
            print("mouse has entered the maze")
            trialStartTime = time.time()
            enteredMaze = True
        if e1Aftere2:
            print("mouse has left the maze")
            trialOngoing=False
            #trialDurations.append((trial,time.time()-trialStartTime))
            enteredMaze = False
            if not rewarded:
                if not mistake:
                    miss.append(trial)
                if mistake:
                    incorrect.append(trial)
            


            

            
        if enteredMaze:
            for item in mousePresent:
                
                if habituation:
                    pass
                
                elif str(rewardTarget) in item and "entrance" not in item:
                    if mousePresent[item] and not rewarded:
                        #this if statement is a placeholder for the training phase where
                        #animals cannot visit a wrong location before visiting the
                        #target location

                        
                        if considerWrongLocations:
                            pass
                            #for item in hasVisited
                            #if rewardTarget
                        
                        else:
                            print(hasVisited)
                            print("animal has reached reward zone")
                            rewarded = True
                            hits.append(trial)
                            #store the reward area
                            areasRewarded.append((trial,rewardTarget))
                            #TODO
                            time2Reward = time.time()
                            #do calculations on time to reward
                            #add code to start proper reward motor
            
            #if trialEnd==1:
            #    trialOngoing = False
        
        
        
        
sessionDuration = time.time()-sessionStarTime    
    

    
    #add some timing metric so we have info on how much time each trial took


    
    




# When everything done, release the capture
cap.release()
cv.destroyAllWindows()

