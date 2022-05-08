import sys
import time
import tkinter
import pyaudio
import socket
import struct
from threading import Thread
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Label

from utils import get_site_info, get_song_info, get_station_info, radio_stn_info


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

frames = []
stop_playing = False
siteIP = ""

song_name = "Not Playing"
next_song_name = "Not Playing"
time_rem = "00:00"

def udpStream(CHUNK, IP, PORT):

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((IP, PORT))
	mreq = struct.pack("4sl", socket.inet_aton(IP), socket.INADDR_ANY)

	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	global stop_playing
	global frames
	while True:
		soundData = sock.recv(CHUNK * 4)
		frames.append(soundData)
		if(stop_playing):
			frames = []
			break

	sock.close()

def udpInfoStream(IP, PORT):

	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	udp.bind((IP, PORT))
	mreq = struct.pack("4sl", socket.inet_aton(IP), socket.INADDR_ANY)

	udp.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	global stop_playing, song_name, next_song_name, time_rem
	while True:
		data = udp.recv(1024)
		song_name__t, next_song_name_t, time_rem_t = get_song_info(data)
		time_rem_t = "{min:02d}:{sec:02d}".format(min=int(time_rem_t//60), sec=int(time_rem_t%60))
		song_name = song_name__t
		next_song_name = next_song_name_t
		time_rem = time_rem_t
		if(stop_playing):
			break

	udp.close()

def play(stream):
	BUFFER = 10
	global stop_playing
	global frames
	while True:
		if len(frames) >= BUFFER:
			while len(frames) > 0:
				data = frames.pop(0)
				stream.write(data)
				if(stop_playing):
					break
		if stop_playing:
			frames = []
			break

stations = []
current_station = -1

def StartStation(event):
	global stop_playing
	stop_playing = True
	time.sleep(1.2)

	p = pyaudio.PyAudio()

	i = int(event.x - 105.0) // 256
	IP = stations[i]["multicast_ip"]
	PORT = stations[i]["multicast_port"]
	INFOPORT = stations[i]["multicast_infoport"]
	RATE = 44100
	FORMAT = 32
	CHUNK = 2048
	CHANNELS = 2

	print(IP, PORT, INFOPORT)

	stream = p.open(
				format=FORMAT,
				channels = CHANNELS,
				rate = RATE,
				output = True,
				frames_per_buffer = CHUNK,
			)
	stop_playing = False
	Ts = Thread(target = udpStream, args=(CHUNK, IP, PORT,))
	Tis = Thread(target = udpInfoStream, args=(IP, INFOPORT,))
	Tp = Thread(target = play, args=(stream,))
	Ts.start()
	Tis.start()
	Tp.start()

def AddStationsToDisplay(canvas):
	canvas.delete("radio")
	for i in range(len(stations)):
		canvas.create_rectangle(
			76.0+i*256.0,
			300.0,
			283.0+i*256.0,
			498.0,
			fill="#18672A",
			outline="",
			tags=["radio"+str(i+1), "radio"])
		canvas.tag_bind("radio"+str(i+1), "<Button-1>", StartStation)
		canvas.create_text(
			170.0+i*256.0,
			310.0,
			anchor="nw",
			text=stations[i]["number"],
			fill="#FFFFFF",
			font=("OpenSansRoman SemiBold", 30 * -1)
		)
		canvas.create_text(
			126.0+i*256.0,
			358.0,
			anchor="nw",
			text=stations[i]["name"],
			fill="#FFFFFF",
			font=("OpenSansRoman SemiBold", 30 * -1)
		)

def LoadNew(canvas):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		global siteIP
		s.connect((siteIP, 5432))
		s.send(radio_stn_info())
		data = s.recv(2048)
		global stations
		site_name, site_desc, stations, total_size = get_site_info(data)
		AddStationsToDisplay(canvas)
		s.close()

	except socket.error as err:
		print("Error")

def StopAll(event):
	global stop_playing
	song_name = "Not Playing"
	next_song_name = "Not Playing"
	time_rem = "00:00"
	stop_playing = True
	time.sleep(1.2)

def clock(canvas, sn, ns, tr):
	canvas.itemconfig(sn, text=song_name)
	canvas.itemconfig(ns, text=next_song_name)
	canvas.itemconfig(tr, text=time_rem)
	canvas.after(1000, lambda: clock(canvas, sn, ns, tr))

if __name__ == "__main__":
	window = Tk()
	window.title("Daddy Radio")
	window.geometry("1321x944")
	window.configure(bg = "#262626")

	siteIP = sys.argv[1]


	canvas = Canvas(
		window,
		bg = "#262626",
		height = 944,
		width = 1321,
		bd = 0,
		highlightthickness = 0,
		relief = "ridge"
	)

	canvas.place(x = 0, y = 0)

	image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
	image_1 = canvas.create_image(
		1066.0,
		89.0,
		image=image_image_1,
		tags=["Refresh"]
	)
	
	canvas.tag_bind("Refresh", "<Button-1>", lambda event: LoadNew(canvas))

	AddStationsToDisplay(canvas)

	canvas.create_text(
		405.0,
		33.0,
		anchor="nw",
		text="Daddy Radio",
		fill="#FFFFFF",
		font=("OpenSansRoman Bold", 76 * -1)
	)

	canvas.create_rectangle(
		305.0,
		708.0,
		981.0,
		822.0,
		fill="#FFFFFF",
		outline="")

	image_image_2 = PhotoImage(
		file=relative_to_assets("image_2.png"))
	image_2 = canvas.create_image(
		358.0,
		765.0,
		image=image_image_2,
		tags=["stopPlaying"]
	)
	canvas.tag_bind("stopPlaying", "<Button-1>", StopAll)

	sn = canvas.create_text(
		424.0,
		726.0,
		anchor="nw",
		text=song_name,
		fill="#000000",
		font=("OpenSansRoman SemiBold", 20 * -1)
	)

	tr = canvas.create_text(
		542.0,
		767.0,
		anchor="nw",
		text=time_rem,
		fill="#000000",
		font=("OpenSansRoman SemiBold", 12 * -1)
	)

	canvas.create_rectangle(
		685.0,
		708.0,
		981.0,
		822.0,
		fill="#18672A",
		outline="")

	image_image_3 = PhotoImage(
		file=relative_to_assets("image_3.png"))
	image_3 = canvas.create_image(
		721.4583129882812,
		764.4583740234375,
		image=image_image_3
	)

	ns = canvas.create_text(
		745.0,
		744.0,
		anchor="nw",
		text=next_song_name,
		fill="#FFFFFF",
		font=("OpenSansRoman SemiBold", 20 * -1)
	)

	clock(canvas, sn, ns, tr)
	
	window.resizable(False, False)
	window.mainloop()
	stop_playing = True