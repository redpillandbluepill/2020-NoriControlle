#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""PyBluez simple example rfcomm-client.py
Simple demonstration of a client application that uses RFCOMM sockets intended
for use with rfcomm-server.
Author: Albert Huang <albert@csail.mit.edu>
$Id: rfcomm-client.py 424 2006-08-24 03:35:54Z albert $
"""

import sys
import os
import threading
import bluetooth
import time
from MPU6050 import MPU6050
import socket
from imutils.video import VideoStream
import imagezmq
import RPi.GPIO as GPIO
import spidev

class NoriClient:
	def __init__(self):
		self.gyro_stop = False

		self.spi = spidev.SpiDev()  # mcp3008 디지털 신호를 아날로그 신호로 변환하기 위해 사용
		self.spi.open(0, 0)
		self.spi.max_speed_hz = 1000000

		self.buttonX = 17
		self.buttonY = 27
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.buttonX, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.buttonY, GPIO.IN, pull_up_down=GPIO.PUD_UP)

		addr = None
		if len(sys.argv) < 2:  # 실행 인자가 없을 때
			print("지정된 장치가 없습니다. 근처의 모든 블루투스 기기를 검색합니다.")
		else:  # 실행 인자로 블루투스 맥주소를 넣을 때
			addr = sys.argv[1]
			print("서버를 검색합니다. {}...".format(addr))

		# 서비스 검색
		# SDP (Service Discovery Protocol) 주변에 사용가능한 서비스를 찾는 프로토콜
		# SDP 에서 서비스의 종류를 구분하기 위해 사용. 서버-클라이언트가 같아야 함.
		uuid = "00000004-0000-1000-8000-00805F9B34FB"
		service_matches = bluetooth.find_service(uuid=uuid, address=addr)  # 블루투스 서비스 찾기

		if len(service_matches) == 0:  # 검색 실패
			print("서버의 서비스를 찾을 수 없습니다.")
			sys.exit(0)

		first_match = service_matches[0]  # 검색한 서비스의 정보
		port = first_match["port"]  # 서버 포트번호
		name = first_match["name"]  # 서버 이름
		host = first_match["host"]  # 서버 맥 주소
		print("port:{}, name:{}, address:{} 연결 중...".format(port, name, host))

		# 클라이언트 블루투스 소켓 생성
		self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		self.sock.connect((host, port))  # 서버로 접속 요청
		print("연결되었습니다.")

		self.wifi_info = WiFiInformation()
		self.wifi_info.send_wifi_information(self.sock, 'wifi')

		#sendMessage = threading.Thread(target=self.send_tread, args=(sock,))
		# sendMessage.start()
		receiveMessage = threading.Thread(target=self.receive_thread)
		receiveMessage.start()
		gyro_thread = threading.Thread(target=self.gyro_thread)
		gyro_thread.start()

	def send_message(self, length, message):
		self.sock.sendall(length.to_bytes(4, byteorder="little"))
		self.sock.sendall(message.encode('utf-8'))

	def receive_thread(self):
		while True:
			data = self.sock.recv(4)
			length = int.from_bytes(data, "little")
			data = self.sock.recv(length)
			message = data.decode('utf-8')
			print('receive: ', message)
			if 'wifi' in message:
				ir_camera = IRCamera(message)
				ir_camera.daemon = True
				ir_camera.start()
			elif 'gyro_stop' in message:
				self.gyro_stop = True
				self.wifi_info.send_wifi_scan(self.sock, 'connect')
				print('자이로 송신 중지 + 와이파이 정보 송신')
			elif 'gyro_start' in message:
				self.gyro_stop = False
			elif 'connect' in message:
				wifi_list = message.split(':')[1]
				wifi_list = wifi_list.split(',')
				self.wifi_info.wifi_connect(wifi_list[0], wifi_list[1], self.sock)
			else:
				print('PC를 와이파이에 연결 후 다시 시도해 주세요.')
			time.sleep(0.001)

	def gyro_thread(self):
		__author__ = 'Geir Istad'  # MPU6050_example.py의 내용 - roll, pitch, yaw를 사용하기 위함
		i2c_bus = 1
		device_address = 0x68
		# The offsets are different for each device and should be changed
		# accordingly using a calibration procedure
		x_accel_offset = -5489
		y_accel_offset = -1441
		z_accel_offset = 1305
		x_gyro_offset = -2
		y_gyro_offset = -72
		z_gyro_offset = -5
		enable_debug_output = True

		mpu = MPU6050(i2c_bus, device_address, x_accel_offset, y_accel_offset,
					  z_accel_offset, x_gyro_offset, y_gyro_offset, z_gyro_offset,
					  enable_debug_output)

		mpu.dmp_initialize()
		mpu.set_DMP_enabled(True)
		mpu_int_status = mpu.get_int_status()
		print(hex(mpu_int_status))

		packet_size = mpu.DMP_get_FIFO_packet_size()
		print(packet_size)
		FIFO_count = mpu.get_FIFO_count()
		print(FIFO_count)

		count = 0
		FIFO_buffer = [0] * 64

		FIFO_count_list = list()
		while True:
			FIFO_count = mpu.get_FIFO_count()
			mpu_int_status = mpu.get_int_status()

			# If overflow is detected by status or fifo count we want to reset
			if (FIFO_count == 1024) or (mpu_int_status & 0x10):
				mpu.reset_FIFO()
			# print('overflow!')
			# Check if fifo data is ready
			elif (mpu_int_status & 0x02):
				# Wait until packet_size number of bytes are ready for reading, default
				# is 42 bytes
				while FIFO_count < packet_size:
					FIFO_count = mpu.get_FIFO_count()
				FIFO_buffer = mpu.get_FIFO_bytes(packet_size)
				accel = mpu.DMP_get_acceleration_int16(FIFO_buffer)
				quat = mpu.DMP_get_quaternion_int16(FIFO_buffer)
				grav = mpu.DMP_get_gravity(quat)
				roll_pitch_yaw = mpu.DMP_get_euler_roll_pitch_yaw(quat, grav)
				# print('roll: ' + str(roll_pitch_yaw.x))
				# print('pitch: ' + str(roll_pitch_yaw.y))
				# print('yaw: ' + str(roll_pitch_yaw.z))

				# 버튼 입력 감지
				x_pos = self.ReadChannel(0)  # mcp 와 연결되는 번호
				y_pos = self.ReadChannel(1)
				button = self.ReadChannel(2)
				button_x = GPIO.input(self.buttonX)
				button_y = GPIO.input(self.buttonY)

				up_arrow = self.button_pos_check(y_pos, 'off', 'up')
				down_arrow = self.button_pos_check(y_pos, 'down', 'off')
				left_arrow = self.button_pos_check(x_pos, 'off', 'left')
				right_arrow = self.button_pos_check(x_pos, 'right', 'off')

				btn = self.button_check(button)
				btn_x = self.button_check(button_x)
				btn_y = self.button_check(button_y)
				print(up_arrow, down_arrow, left_arrow, right_arrow, btn, btn_x, btn_y)

				# roll, pitch, yaw, 버튼을 합쳐서 보내기
				message = 'rpy:'+str(int(roll_pitch_yaw.x)) + ',' + str(int(roll_pitch_yaw.y)) + ',' + str(
					int(roll_pitch_yaw.z)) + 'button:' + up_arrow + ',' + down_arrow + ',' + left_arrow + ','\
						  + right_arrow + ',' + btn + ',' + btn_x + ',' + btn_y
				length = len(message)

				if not self.gyro_stop:
					self.send_message(length, message)
				# print('roll:'+str(int(roll_pitch_yaw.x))+' pitch:'+str(int(roll_pitch_yaw.y))+' yaw:'+str(int(roll_pitch_yaw.z)))
				time.sleep(0.08)  # 0.1초 마다 전송

	def ReadChannel(self, channel):  # mcp3008 데이터 읽기
		r = self.spi.xfer2([1, (8 + channel) << 4, 0])
		adc_out = ((r[1] & 3) << 8) + r[2]

		return adc_out
	
	def button_pos_check(self, button, arrow1, arrow2):
		if button > 800:
			btn = arrow1
		elif button < 200:
			btn = arrow2
		else:
			btn = 'off'
		return btn

	def button_check(self, button):
		if button == 0:
			btn = 'on'
		else:
			btn = 'off'
		return btn


class WiFiInformation:
	def send_wifi_information(self, sock, header):
		wifi_on_off = os.popen('sudo iwconfig').read()
		wifi_on_off = wifi_on_off.split('wlan0')[1].split('\n')[0].split('ESSID:')[1].rstrip()
		print(wifi_on_off)
		if 'off/any' != wifi_on_off:
			temp = str(header) + ':' + str(self.wifi_ip_adress()) + ',' + str(self.wifi_current())
			for j in self.wifi_scan():
				temp = temp + ',' + str(j)
			message = temp
			length = len(message)
			sock.sendall(length.to_bytes(4, byteorder="little"))
			sock.sendall(message.encode('utf-8'))

	def send_wifi_scan(self, sock, header):
		temp = str(header) + ':'
		wifi_scan = self.wifi_scan()
		if wifi_scan == False:
			print('와이파이를 찾지 못함')
		else:
			for i in wifi_scan:
				temp = temp + str(i) + ','
			message = temp[0:-1]  # 제일 뒤에 , 없애기
			length = len(message)
			sock.sendall(length.to_bytes(4, byteorder="little"))
			sock.sendall(message.encode('utf-8'))

	def wifi_connect(self, pc_wifi_ssid, pc_wifi_pw, sock):
		#if pc_wifi_ssid in self.wifi_scan():  # PC에 연결된 WiFi의 SSID가 라즈베리파이가 찾은 WiFi의 SSID 리스트 중에 있다면 실행
		try:
			print('와이파이 접속중....')
			os.system('sudo ifconfig wlan0 up')  # 무선랜 ON
			os.system('sudo killall wpa_supplicant')  # 현재 실행중인 와이파이 OFF

			# 암호가 있는 경우(주의사항: 랜카드가 WiFi 5G 신호를 잡지 못함)
			if pc_wifi_pw != 'None':
				# 와이파이 정보 저장 후 재부팅
				os.system('sudo wpa_passphrase ' + pc_wifi_ssid + ' ' + pc_wifi_pw + '> /home/pi/noriProject/wifi/wpa_psk.conf')
				os.system('sudo chmod 777 /etc/wpa_supplicant/wpa_supplicant.conf')  # 권한 변경
				os.system('sudo head -4 /home/pi/noriProject/wifi/wpa_base.conf > /etc/wpa_supplicant/wpa_supplicant.conf')
				os.system('cat /home/pi/noriProject/wifi/wpa_psk.conf >> /etc/wpa_supplicant/wpa_supplicant.conf')

				ip_adress = 'reboot'
				message = 'success:' + str(ip_adress)
				length = len(message)
				sock.sendall(length.to_bytes(4, byteorder="little"))
				sock.sendall(message.encode('utf-8'))

				os.system('sudo reboot')  # 재시작(WiFi 연결을 위해)

				# wifi 연결 후 재부팅
				# os.system('sudo wpa_passphrase ' + pc_wifi_ssid + ' ' + pc_wifi_pw + '> /home/pi/noriProject/wifi/wpa_psk.conf')  # 연결 시 사용할 psk 저장
				# os.system('sudo wpa_supplicant -B -i wlan0 -c /home/pi/noriProject/wifi/wpa_psk.conf')  # 와이파이 연결
				# os.system('sudo dhclient wlan0')  # ip 할당받기

				#os.system('sudo cat /home/pi/noriProject/wifi/wpa_psk.conf >> /etc/wpa_supplicant/wpa_supplicant.conf')

				# if self.wifi_current() == pc_wifi_ssid:
				# 	print('와이파이 연결 완료')
				# 	# WiFi 자동 실행 파일에 연결한 Wi-Fi 정보 저장
				# 	os.system('sudo chmod 777 /etc/wpa_supplicant/wpa_supplicant.conf')  # 권한 변경
				# 	os.system('sudo head -4 /home/pi/noriProject/wifi/wpa_base.conf > /etc/wpa_supplicant/wpa_supplicant.conf')
				# 	os.system('cat /home/pi/noriProject/wifi/wpa_psk.conf >> /etc/wpa_supplicant/wpa_supplicant.conf')
				#
				# 	ip_adress = self.wifi_ip_adress()
				# 	message = 'success:' + str(ip_adress)
				# 	length = len(message)
				# 	sock.sendall(length.to_bytes(4, byteorder="little"))
				# 	sock.sendall(message.encode('utf-8'))
				#
				# 	os.system('sudo reboot')  # 재시작(WiFi 연결을 위해)
				# else:
				# 	print('와이파이 연결 실패')
				# 	message = 'fail:wifi_pw'
				# 	length = len(message)
				# 	sock.sendall(length.to_bytes(4, byteorder="little"))
				# 	sock.sendall(message.encode('utf-8'))
			else:
				print('암호가 없을 때 연결')
				# 암호가 없는 경우
				#os.system('sudo iwconfig wlan0 essid ' + pc_wifi_ssid)
				#os.system('dhclient wlan0')
				#time.sleep(4)

				os.system('sudo chmod 777 /etc/wpa_supplicant/wpa_supplicant.conf')  # 권한 변경
				os.system('sudo head -4 /home/pi/noriProject/wifi/wpa_base.conf > /etc/wpa_supplicant/wpa_supplicant.conf')
				os.system('python3 /home/pi/noriProject/wifi/none_pw_wifi.py \'' + pc_wifi_ssid + '\' > /home/pi/noriProject/wifi/wpa_psk.conf')
				os.system('cat /home/pi/noriProject/wifi/wpa_psk.conf >> /etc/wpa_supplicant/wpa_supplicant.conf')

				message = 'success:reboot_plz'
				length = len(message)
				sock.sendall(length.to_bytes(4, byteorder="little"))
				sock.sendall(message.encode('utf-8'))

				os.system('sudo reboot')  # 재시작(WiFi 연결을 위해)
				# if self.wifi_current() == pc_wifi_ssid:
				# 	print('와이파이 연결 완료')
				# 	# WiFi 자동 실행 파일에 연결한 Wi-Fi 정보 저장
				# 	os.system('sudo chmod 777 /etc/wpa_supplicant/wpa_supplicant.conf')  # 권한 변경
				# 	os.system('sudo head -4 /home/pi/noriProject/wifi/wpa_base.conf > /etc/wpa_supplicant/wpa_supplicant.conf')
				# 	os.system('python3 /home/pi/noriProject/wifi/none_pw_wifi.py ' + pc_wifi_ssid + ' > /home/pi/noriProject/wifi/wpa_psk.conf')
				# 	os.system('cat /home/pi/noriProject/wifi/wpa_psk.conf >> /etc/wpa_supplicant/wpa_supplicant.conf')
				#
				# 	ip_adress = self.wifi_ip_adress()
				# 	message = 'success:' + str(ip_adress)
				# 	length = len(message)
				# 	sock.sendall(length.to_bytes(4, byteorder="little"))
				# 	sock.sendall(message.encode('utf-8'))
				# else:
				# 	print('와이파이 연결 실패')
				# 	message = 'fail:no_wifi_pw'
				# 	length = len(message)
				# 	sock.sendall(length.to_bytes(4, byteorder="little"))
				# 	sock.sendall(message.encode('utf-8'))

		except:
			print('와이파이 연결 실패')
			message = 'fail:except'
			length = len(message)
			sock.sendall(length.to_bytes(4, byteorder="little"))
			sock.sendall(message.encode('utf-8'))
		#else:
		#	print('PC에 연결된 WiFi를 찾지 못했습니다.')
		
	def wifi_scan(self):
		wifi_list = []
		wifi = os.popen('sudo iw wlan0 scan').read()
		wifi = wifi.split('\n')
		for i in wifi:
			if 'SSID' in i:
				if '*' in i:
					continue
				elif 'x00' in i:
					continue
				else:
					temp = i.split('SSID: ')
					wifi_list.append(temp[1])
		if wifi_list == []:
			wifi_list = False
			print('와이파이를 찾지 못함')
		print(wifi_list)
		return wifi_list

	def wifi_ip_adress(self):
		try:
			ip_adress = os.popen('sudo ifconfig').read()
			ip_adress = ip_adress.split('wlan0')[1].split('\n')[1].split('netmask')[0].split('inet ')[1].rstrip()
			print(ip_adress)
		except:
			ip_adress = os.popen('sudo ifconfig').read()
			ip_adress = ip_adress.split('wlan0')[1].split('\n')[1].split('netmask')[0].split('inet ')[1].rstrip()
			print(ip_adress)
		return ip_adress

	def wifi_current(self):
		wifi_current = os.popen('sudo iwconfig').read()  # 현재 연결된 wifi
		if 'ESSID' in wifi_current:
			temp = wifi_current.split('ESSID:')[1].split('\n')[0].rstrip()  # ssid를 추출함
			wifi_current = temp[1:-1]
		else:
			wifi_current = False
			print('연결된 WiFi 없음')

		return wifi_current


class IRCamera(threading.Thread):
	def __init__(self, wifi_list):
		threading.Thread.__init__(self)
		# 라즈베리파이에서 와이파이 스캔을 통해 잡히는 SSID 리스트
		print(wifi_list)
		wifi_list = wifi_list.split(':')[1]
		wifi_list = wifi_list.split(',')

		self.wifi_ssid = wifi_list[0]
		self.wifi_pw = wifi_list[1]
		self.ip_address = wifi_list[2]

	def run(self):
		# 카메라 영상 송신
		sender = imagezmq.ImageSender(connect_to='tcp://' + self.ip_address + ':5555')  # ImageSender 초기화 해서 5555포트로 접속 한다
		rpi_name = socket.gethostname()  # send RPi hostname with each image
		picam = VideoStream(usePiCamera=True).start()
		time.sleep(2.0)

		while True:
			image = picam.read()
			sender.send_image(rpi_name, image)
			time.sleep(0.001)


if __name__ == "__main__":
	client = NoriClient()
	#wifi_on_off = os.popen('sudo iwconfig').read()
	#wifi_on_off = wifi_on_off.split('wlan0')[1].split('\n')[0].split('ESSID:')[1].rstrip()
	#print('test:',wifi_on_off)

# print('연결 끊어짐')
# sock.close()


