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
import time
from MPU6050 import MPU6050


def send_tread(sock):
	__author__ = 'Geir Istad' #MPU6050_example.py의 내용 - roll, pitch, yaw를 사용하기 위함
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
			#print('overflow!')
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
			#print('roll: ' + str(roll_pitch_yaw.x))
			#print('pitch: ' + str(roll_pitch_yaw.y))
			#print('yaw: ' + str(roll_pitch_yaw.z))
			message = str(roll_pitch_yaw.x)+','+str(roll_pitch_yaw.y)+','+str(roll_pitch_yaw.z)  #roll, pitch, yaw를 합쳐서 보내기
			length = len(message)
			sock.sendall(length.to_bytes(4, byteorder="little"))
			sock.sendall(message.encode('utf-8'))
			print('roll:'+str(roll_pitch_yaw.x)+' pitch:'+str(roll_pitch_yaw.y)+' yaw:'+str(roll_pitch_yaw.z))
			time.sleep(0.1)   #0.1초 마다 전송
	"""
	while True:
		message=input()
		length = len(message)
		if message == 'quit':
			break
		sock.sendall(length.to_bytes(4, byteorder="little"))
		sock.sendall(message.encode('utf-8'))
	"""
def receive_thread(sock):
	while True:
		data = sock.recv(4)
		length = int.from_bytes(data, "little")
		data = sock.recv(length)
		message = data.decode('utf-8')
		print('receive: ', message)

if __name__ == "__main__":

	addr = None

	if len(sys.argv) < 2:
		print("No device specified. Searching all nearby bluetooth devices for "
		"the SampleServer service...")
	else:
		addr = sys.argv[1]
		print("Searching for SampleServer on {}...".format(addr))

	# search for the SampleServer service
	uuid = "00000004-0000-1000-8000-00805F9B34FB"
	service_matches = bluetooth.find_service(uuid=uuid, address=addr)

	if len(service_matches) == 0:
		print("Couldn't find the SampleServer service.")
		sys.exit(0)

	first_match = service_matches[0]
	port = first_match["port"]
	name = first_match["name"]
	host = first_match["host"]

	print("Connecting to \"{}\" on {}".format(name, host))

	# Create the client socket
	sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
	sock.connect((host, port))

	print("Connected. Type something...")
	sendMessage = threading.Thread(target=send_tread, args=(sock,))
	receiveMessage = threading.Thread(target=receive_thread, args=(sock,))
	sendMessage.start()
	receiveMessage.start()
	"""
	while True:
		message = input()
		length = len(message)
		if message == 'quit':
			 break
		sock.sendall(length.to_bytes(4, byteorder="little"))
		sock.sendall(message.encode('euc-kr'))
	"""
	
	
	#print('연결 끊어짐')
	#sock.close()


