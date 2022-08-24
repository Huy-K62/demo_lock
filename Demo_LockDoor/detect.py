import face_recognition
import cv2
import numpy as np
import RPi.GPIO as GPIO
from threading import Thread
import threading
import time
GPIO.setmode(GPIO.BOARD)       #I use Board pin numbering instead of Broadcom(BCM)
GPIO.setup(11, GPIO.IN)
GPIO.setup(7, GPIO.IN) 
GPIO.setup(9, GPIO.IN) 
GPIO.setup(8, GPIO.OUT)
GPIO.setup(10, GPIO.OUT) 
#import RPi.GPIO as GPIO
#GPIO.setmode(GPIO.BCM)

#GPIO.setup(17, GPIO.OUT)
video_capture = cv2.VideoCapture(0)
#file_name = open("name.txt",'ab')
# Load a sample picture and learn how to recognize it.

# Create arrays of known face encodings and their names
known_face_names = []
#print(known_face_names)
# Initialize some variables
known_face_encodings = []
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
flag_detect = 0
flag_b1 = 0
flag_b2 = 0
# flag_wait = 0
count = 1
start_time = 0
end_time = 0
# def face():
while True:
    motion_detect = GPIO.input(11)
    # global process_this_frame
    # global flag_wait
    # motion_detect = 1
    if(motion_detect == 1):
        known_face_names.clear()
        known_face_encodings.clear()
        object_image = face_recognition.load_image_file("manager.jpg")
        object_face_encoding = face_recognition.face_encodings(object_image)[0]
        known_face_encodings.append(object_face_encoding)
        # with open('name.txt') as rf:
        #     lines = rf.readlines()
        #     for idx, line in enumerate(lines):
        #         known_face_names.append(line)
        #         known_face_names[idx] = known_face_names[idx].strip()
        #         #known_face_names = set(known_face_names)
        # for i in range(count):
        #     name_customer = "customer"+str(count)+".jpg"
        #     customer_image = face_recognition.load_image_file(name_customer)
        #     customer_face_encoding = face_recognition.face_encodings(customer_image)[0]
        #     known_face_encodings.append(customer_face_encoding)
            #known_face_encodings = set(known_face_encodings)

        while True:
            with open('name.txt') as rf:
                lines = rf.readlines()
                for idx, line in enumerate(lines):
                    known_face_names.append(line)
                    known_face_names[idx] = known_face_names[idx].strip()
                #known_face_names = set(known_face_names)
            for i in range(count):
                name_customer = "customer"+str(count)+".jpg"
                customer_image = face_recognition.load_image_file(name_customer)
                customer_face_encoding = face_recognition.face_encodings(customer_image)[0]
                known_face_encodings.append(customer_face_encoding)
                
            button1 = GPIO.input(7)
            button2 = GPIO.input(9)
            # Grab a single frame of video
            ret, frame = video_capture.read()
            if(button1 == 1):
                flag_b1 = 1
            if(button2 == 1):
                flag_b2 = 1
                time.sleep(1)
            if(flag_b1 == 1):
                print("Chon che do")
                if(flag_detect == 1):
                    if(flag_b2 == 1):
                        if(top>100 and right>390 and bottom>290 and left>195):
                            print("chup anh")
                            count=int(count) + 1
                            cv2.imwrite("/home/pi/Demo_LockDoor/MFRC522-python/"+"customer"+str(count)+".jpg", frame)
                            #file_name.write("customer" + str(count))
                            with open('name.txt', 'a') as wf:
                                wf.write('Customer' + str(count) + "\n")
                            # print("sau: ", count)
                            flag_b2 = 0
                            flag_b1 = 0
                        else:
                            print("bao coi")
            # Only process every other frame of video to save time
            if process_this_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]
                
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        if(name == "Manager"):
                            flag_detect = 1
                        start_time = time.time()
                        GPIO.output(10, 1)
                        print("thuc hien trong 3s")
                        
                    else:
                        flag_detect = 0
                        GPIO.output(10, 0)
                        print("dong cua")
                    face_names.append(name)

            end_time = time.time()
            if (end_time-start_time > 3):
                GPIO.output(10, 0)
                print("het time")
            process_this_frame = not process_this_frame
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                    # print(top,right,bottom,left)
                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Video', frame)

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q') or GPIO.input(11) == 0:
            # if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()

# def lock_door():
#     global flag_wait
#     print("thread2: ", flag_wait)
#     if(flag_wait == 1):
#         start_time = time.time()
#         while True:
#             # GPIO.output(10, 1)
#             print("chay trong 3s")
#             end_time = time.time()
#             # if(end_time-start_time > 3 or flag_b1 == 1 or flag_wait == 0):
#             if(end_time-start_time > 3 or flag_wait == 0):
#                 # GPIO.output(10, 0)
#                 print("ngung chay")
#                 break
# try:
#     t1 = threading.Thread(target=face)
#     t2 = threading.Thread(target=lock_door)
#     t1.start()
#     t2.start()
#     # t1.join()
#     # t2.join()
# except:
#     print("error")
