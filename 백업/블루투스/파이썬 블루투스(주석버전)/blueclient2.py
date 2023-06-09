#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""PyBluez simple example rfcomm-client.py
Simple demonstration of a client application that uses RFCOMM sockets intended
for use with rfcomm-server.
Author: Albert Huang <albert@csail.mit.edu>
$Id: rfcomm-client.py 424 2006-08-24 03:35:54Z albert $
"""

import sys
import threading
import bluetooth
"""
while True:
	message = input()
	length = len(message)
	if message == 'quit':
		break
	sock.sendall(length.to_bytes(4, byteorder="little"))
	sock.sendall(message.encode('utf-8'))
"""
def send_tread(sock):
	while True:
		message = input()
		data = message.encode('utf-8') #
		length = len(data)
		#리틀 엔디언 방식으로 데이터의 길이 전송
		sock.sendall(length.to_bytes(4, byteorder="little"))
		#데이터 전송
		sock.sendall(data)

def receive_thread(sock):
	while True:
		data = sock.recv(4)
		length = int.from_bytes(data, "little")
		data = sock.recv(length)
		message = data.decode('utf-8')
		print('receive: ', message)

if __name__ == "__main__":
	addr = None
	if len(sys.argv) < 2:  # 실행 인자가 없을 때
		print("지정된 장치가 없습니다. 근처의 모든 블루투스 기기를 검색합니다.")
	else:   # 실행 인자로 블루투스 맥주소를 넣을 때
		addr = sys.argv[1]
		print("서버를 검색합니다. {}...".format(addr))

	# 서비스 검색
	# SDP (Service Discovery Protocol) 주변에 사용가능한 서비스를 찾는 프로토콜
	# SDP 에서 서비스의 종류를 구분하기 위해 사용. 서버-클라이언트가 같아야 함.
	uuid = "00000004-0000-1000-8000-00805F9B34FB"
	service_matches = bluetooth.find_service(uuid=uuid, address=addr)  # 블루투스 서비스 찾기

	if len(service_matches) == 0: #검색 실패
		print("서버의 서비스를 찾을 수 없습니다.")
		sys.exit(0)

	first_match = service_matches[0]  # 검색한 서비스의 정보
	port = first_match["port"]  # 서버 포트번호
	name = first_match["name"]  # 서버 이름
	host = first_match["host"]  # 서버 맥 주소
	print("port:{}, name:{}, address:{} 연결 중...".format(port, name, host))

	# 클라이언트 블루투스 소켓 생성
	sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
	sock.connect((host, port))  # 서버로 접속 요청

	print("연결되었습니다.")

	while True:
		message = input()
		data = message.encode('utf-8')  # utf-8 형식의 바이트 코드로 변환
		length = len(data)
		# 데이터의 길이를 리틀 엔디언 방식으로 4 바이트로 변환 후 전송
		sock.sendall(length.to_bytes(4, byteorder="little"))
		sock.sendall(data)  # utf-8 형식의 바이트 전송


	#sendMessage = threading.Thread(target=send_tread, args=(sock,))
	#receiveMessage = threading.Thread(target=receive_thread, args=(sock,))
	#sendMessage.start()
	#receiveMessage.start()
	#print('연결 끊어짐')
	#sock.close()


