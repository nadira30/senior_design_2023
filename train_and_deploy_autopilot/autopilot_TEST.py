#!/usr/bin/python3
import cv2 as cv
import servo1 as servo
import motor
from torchvision.io import read_image
from torchvision.transforms import ToTensor, Resize
import torch
from cnn_network import cnn_network
from adafruit_servokit import ServoKit

#pca.frequency = 50
kit = ServoKit(channels=16)


# Load model
model = cnn_network()
model.load_state_dict(torch.load("model_cnn.pth", map_location=torch.device('cpu')))

# Setup Transforms
img2tensor = ToTensor()
resize = Resize(size=(640, 480))

# Create video capturer
cap = cv.VideoCapture(0) #video capture from 0 or -1 should be the first camera plugged in. If passing 1 it would select the second camera
# cap.set(cv.CAP_PROP_FPS, 10)


while True:
    ret, frame = cap.read()   
    if frame is not None:
        # cv.imshow('frame', frame)  # debug
        print(f"original frame size: {frame.shape}")
        #print("original frame: ", frame)
        frame = cv.resize(frame, (int(frame.shape[1]), int(frame.shape[0]))) # THIS LINE DOES NOTHING
        print(f"resized frame size: {frame.shape}")
        #print("resized frame: ", frame)
        gray = frame  # we changed this from b&w to color
        img_tensor = img2tensor(gray) # this also divides by 255
        print(f"frame to tensor size: {img_tensor.size()}")
        #print("frame to tensor: ", img_tensor)
        img_tensor = resize(img_tensor) # THIS LINE IS NOT NEEDED (we don't need to resize the tensor. It already matches what's given in train.py
        print(f"frame to tensor after resize: {img_tensor.size()}")
        #print(img_tensor.shape)
    with torch.no_grad():
        img_tensor = img_tensor.unsqueeze(dim=0) # THIS LINE ADDS THE EXTRA DIMENSION
        print(f"frame unsqueezed size: {img_tensor.size()}")
        pred = model(img_tensor)
    print(pred)
    steering, throttle = pred[0][0].item() + 0.71, pred[0][1].item()
    print("steering: ", steering)
    print("throttle: ", throttle)
    motor.drive(throttle * 650 * 2.5) # we remove the negative before throttle so it doesn't drive bkwards
    print("motor: ", throttle * 650 * 2.5)
    ang = 90 * (1 + steering) + 6.8
    if ang > 180:
        ang = 180
    elif ang < 0:
        ang = 0
    kit.servo[0].angle = ang
    print("ang: ", ang)

    if cv.waitKey(1)==ord('q'):
        motor.stop()
        motor.close()
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
        
