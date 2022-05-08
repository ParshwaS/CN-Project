import time
import socket
from threading import Thread
import wave
import os
import sys

from utils import song_info

stop_server = False
i = 0
files = []
time_rem = 0

def udpStream(CHUNK, IP):

	MCAST_GRP = IP
	MCAST_PORT = 6253
	MULTICAST_TTL = 2
	global stop_server
	global i
	global files
	global time_rem

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

	while True:
		wf = wave.open(files[i], 'rb')
		data = wf.readframes(CHUNK)
		sent = 0
		total_f = wf.getnframes()
		rate_f = wf.getframerate()
		bitdepth_f = wf.getsampwidth()
		bitrate = rate_f * bitdepth_f
		while len(data) > 0:
			sock.sendto(data, (MCAST_GRP, MCAST_PORT))
			sent += 1
			time_rem = int(((total_f - (sent * CHUNK)) / rate_f))
			data = wf.readframes(CHUNK)
			time.sleep(CHUNK/bitrate)
			if(stop_server):
				break
		
		wf.close()
		if(stop_server):
			break
		
		i += 1
		i %= len(files)
		time_rem = 0
	
	sock.close()

def udpInfoStream(IP):

	MCAST_GRP = IP
	MCAST_PORT = 6235
	MULTICAST_TTL = 2
	global stop_server
	global i
	global files
	global time_rem

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

	while True:
		data = song_info(files[i].split('/')[-1].split('.')[0], files[(i+1)%len(files)].split('/')[-1].split('.')[0], time_rem)
		sock.sendto(data, (MCAST_GRP, MCAST_PORT))
		time.sleep(1)
		if(stop_server):
			break
	
	sock.close()

if __name__ == "__main__":
	CHUNK = 2048

	if(len(sys.argv) <= 2):
		print("Usage: python3 UDPServer.py <MCAST IP> <Director Path>")

	IP = str(sys.argv[1])
	print(IP)
	dire = sys.argv[2]

	for file in os.listdir(dire):
		if file.endswith(".wav"):
			files.append(os.path.join(dire, file))
	
	#Initialize Threads
	udpThread = Thread(target = udpStream, args = (CHUNK,IP,))
	udpInfoThread = Thread(target = udpInfoStream, args = (IP,))
	udpThread.start()
	udpInfoThread.start()
	input("Press Enter to stop...")
	stop_server = True
	udpThread.join()
	udpInfoThread.join()
