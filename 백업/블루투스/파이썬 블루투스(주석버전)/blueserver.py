# file: rfcomm-server.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: simple demonstration of a server application that uses RFCOMM sockets
#
# $Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $

import sys
import threading
from bluetooth import *


def send_tread(sock):
    while True:
        message = input()
        data = message.encode('utf-8')
        length = len(data)
        sock.send(length.to_bytes(4, byteorder="little"))
        sock.send(data)


def receive_thread(sock):
    while True:
        data = sock.recv(4)
        length = int.from_bytes(data, "little")
        data = sock.recv(length)
        message = data.decode('utf-8')
        print('receive: ', message)


if __name__ == "__main__":
    server_sock = BluetoothSocket(RFCOMM) #RFCOMM 프로토콜로 블루투스 소켓 생성
    server_sock.bind(("", PORT_ANY)) #소켓에 아무 포트번호나 지정
    server_sock.listen(1) #1개의 접속 요청을 기다림

    port = server_sock.getsockname()[1] #소켓에 지정된 포트번호 가져오기

    # SDP에서 서비스의 종류를 구분하기 위해 사용. 서버-클라이언트가 같아야 함.
    uuid = "00000004-0000-1000-8000-00805F9B34FB"

    # 블루투스 서비스 등록
    advertise_service(server_sock, "SampleServer",
                      service_id=uuid,
                      service_classes=[uuid, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE],
                      )
    print("RFCOMM %d번 port에서 연결 대기중" % port)

    # 접속 요청 승인후 클라이언트와 통신할 전용 소켓 생성
    sock, client_info = server_sock.accept()
    print("연결된 클라이언트의 정보:", client_info)

    while True:
        data = sock.recv(4)  # 클라이언트가 보내준 첫 데이터(문자열 길이) 4바이트 수신
        length = int.from_bytes(data, "little")  # byte 를 리틀 엔디언 방식으로 int 로 변환
        data = sock.recv(length)  # 클라이언트에서 보내준 데이터의 길이만큼 수신
        message = data.decode('utf-8')  # utf-8 형식의 바이트를 문자열로 변환
        print('receive: ', message)




    # sendMessage = threading.Thread(target=send_tread, args=(sock,))
    # receiveMessage = threading.Thread(target=receive_thread, args=(sock,))
    # sendMessage.start()
    # receiveMessage.start()

    print("disconnected")

    #sock.close()
    #server_sock.close()
    print("all done")
