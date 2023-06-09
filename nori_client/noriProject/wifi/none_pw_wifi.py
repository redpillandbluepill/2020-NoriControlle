import sys

if __name__ == "__main__":
	ssid = sys.argv[1]
	ssid = '"' + ssid + '"'
	print('network={\n\tssid=' + ssid + '\n\tkey_mgmt=NONE\n}')

