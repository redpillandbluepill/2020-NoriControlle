# file: rfcomm-server.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: simple demonstration of a server application that uses RFCOMM sockets
#
# $Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $

import sys
import threading
import pyautogui as pag
from bluetooth import *

def send_tread(sock):
    while True:
        message = input()
        if message == 'quit':
            break
        data = message.encode('utf-8')
        length = len(data)
        sock.send(length.to_bytes(4, byteorder="little"))
        sock.send(data)


def receive_thread(sock):
    global True_key #키보드 입력을 제어하기 위해 전역변수 선언
    while True:
        data = sock.recv(4)
        length = int.from_bytes(data, "little")
        data = sock.recv(length)
        message = data.decode('utf-8')
        #print('receive: ', message)
        rpy_list = message.split(',')  #받은 문자열을 ','을 기준으로 나눠 리스트에 넣기
        print('roll:'+rpy_list[0]+' pitch:'+rpy_list[1]+' raw:'+rpy_list[2])
        rpy = list(map(float, rpy_list)) #문자열 리스트를 float형으로 변환

        if rpy[0] <= -20:   #값에 따라 변수 입력 -> 메인에서 동작함
            True_key = 1
        elif rpy[0] >= 20:
            True_key = 2
        elif rpy[1] <= -20:
            True_key = 3
        elif rpy[1] >= 20:
            True_key = 4
        else:
            True_key = 0


if __name__ == "__main__":
    global True_key
    True_key = 0
    server_sock = BluetoothSocket(RFCOMM)
    server_sock.bind(("", PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    uuid = "00000004-0000-1000-8000-00805F9B34FB"

    advertise_service(server_sock, "SampleServer",
                      service_id=uuid,
                      service_classes=[uuid, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE],
                      #                   protocols = [ OBEX_UUID ]
                      )

    print("Waiting for connection on RFCOMM channel %d" % port)

    sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

    sendMessage = threading.Thread(target=send_tread, args=(sock,))
    receiveMessage = threading.Thread(target=receive_thread, args=(sock,))
    sendMessage.start()
    receiveMessage.start()

    while True:
        try:
            print(True_key)



            """
            while True_key == 1: #특정키가 계속 눌러지게 하기 위해 무한 반복
                pag.keyDown('w')
                pag.keyDown('num4')
                if True_key != 1:
                    pag.keyUp('w')
                    pag.keyUp('num4')
                    break
            while True_key == 2:
                pag.keyDown('w')
                pag.keyDown('num6')
                if True_key != 2:
                    pag.keyUp('w')
                    pag.keyUp('num6')
                    break
            while True_key == 3:
                pag.keyDown('w')
                pag.keyDown('num8')
                if True_key != 3:
                    pag.keyUp('w')
                    pag.keyUp('num8')
                    break
            while True_key == 4:
                pag.keyDown('w')
                pag.keyDown('num5')
                if True_key != 4:
                    pag.keyUp('w')
                    pag.keyUp('num5')
                    break
            """
        except:
            pass

    """
    try:
        while True:
            data = client_sock.recv(1024)
            if len(data) == 0: break
            print("received [%s]" % data)
    except IOError:
        pass
    """
    print("disconnected")

    #sock.close()
    #server_sock.close()
    print("all done")
