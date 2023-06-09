import socket
import time
from imutils.video import VideoStream
import imagezmq

sender = imagezmq.ImageSender(connect_to='tcp://192.168.35.114:5555') # ImageSender 초기화 해서 5555포트로 접속 한다

rpi_name = socket.gethostname() # send RPi hostname with each image
picam = VideoStream(usePiCamera=True).start()
#라즈페리 파이의경우 opencv 의 비디오 캡쳐가 잘먹히지 않는다
#따라서 imutils.video import VideoStream 를 사용한다

time.sleep(2.0)  # 라즈베리파이는 성능이 안좋음 카메라 켜는데 시간이걸림 2초동안기다려~
while True:  # 카메라에서 이미지를 불러옴
     image = picam.read()
     sender.send_image(rpi_name, image)