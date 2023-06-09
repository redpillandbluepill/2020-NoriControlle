import cv2
import imagezmq
import numpy as np

image_hub = imagezmq.ImageHub() #ImageHub()  클래스 이니셜라이즈 
while True:  # 이미지를 계속받아옴
        rpi_name, image = image_hub.recv_image() # 이미지받아오면
        
        #파란 사각형 범위 지정
        x = 200
        y = 100
        w = 50
        h = 50

        image = cv2.resize(image, (500, 500)) #화면 크기
        roi = image[y:y + h, x:x + w]  #파란 사격형의 범위를 roi에 대입
        cv2.rectangle(roi, (0, 0), (h - 1, w - 1), (255, 0, 0)) #파란 사각형 생성
        roi = cv2.medianBlur(roi, 3) # 해석 필요
        roi = np.array(roi, dtype=np.uint8)
        hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)  # 지정한 범위를 hsv 색공간으로 변환 후 대입


        h, s, v = cv2.split(hsv)  # 색상 채도 명도를 나눔
        color = h.mean()  #색상의 평균 값을 추출
        color2 = s.mean()
        color3 = v.mean()
        print('{}     {}     {}'.format(color, color2, color3))   #범위안에 색상 값 출력

        if(color>150 and color<170):
                print("반사 스티커 인식 - 키보드 입력.")

        cv2.imshow(rpi_name, image)


        #cv2.imshow(rpi_name, image) # opencv2 의 imshow( ) 를 통해 이미지를 보여줌

        cv2.waitKey(1)
        image_hub.send_reply(b'OK') # 라즈베리 파이쪽에 응답 받았다 'OK'