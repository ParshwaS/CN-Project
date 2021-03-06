import sys
import time
import tkinter as tk
import pyaudio
import socket
import struct
from threading import Thread
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Label
from PIL import Image, ImageTk

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
	sock.bind(('', PORT))
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
	udp.bind(('', PORT))
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
			120.0+i*230,
			230.0,
			320.0+i*230,
			420.0,
			fill="#69451f",
			outline="",
			tags=["radio"+str(i+1), "radio"]
		)
		canvas.tag_bind("radio"+str(i+1), "<Button-1>", StartStation)
		canvas.create_text(
			215.0+i*230,
			280.0,
			anchor="nw",
			text=stations[i]["number"],
			fill="#FFFFFF",
			font=("Comic Sans MS", 30 * -1),
			justify="center"
		)
		canvas.create_text(
				195.0+i*230,
				315.0,
				anchor="nw",
				text=stations[i]["name"],
				fill="#FFFFFF",
				font=("Comic Sans MS", 30 * -1),
				justify="center"
		)
	
def LoadNew(canvas):
	global siteIP
	siteIP = inputtxt.get("1.0", "end-1c")
	print(siteIP)
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((siteIP, 5432))
		s.send(radio_stn_info())
		data = s.recv(2048)
		global stations
		site_name, site_desc, stations, total_size = get_site_info(data)
		AddStationsToDisplay(canvas)
		s.close()

	except socket.error as err:
		print(err)

def StopAll(event):
	global stop_playing, song_name, next_song_name, time_rem
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

# def siteIPFunc():
# 		global siteIP
# 		siteIP = inputtxt.get("1.0", "end-1c")
# 		print(siteIP)

if __name__ == "__main__":
	window = Tk()
	window.title("Radio wale Babu")
	window.geometry("1366x750")
	window.configure(bg = "#162f4a")
	# siteIP = sys.argv[1]


	canvas = Canvas(
		window,
		bg = "#162f4a",
		height = 750,
		width = 1366,
		bd = 0,
		highlightthickness = 0,
		relief = "ridge"
	)

	canvas.place(x = 0, y = 0)

	image_image_1 = PhotoImage(file=relative_to_assets("enter.png"))
	image_1 = canvas.create_image(
		1040.0,
		136.0,
		image=image_image_1,
		tags=["Refresh"]
	)
	
	canvas.tag_bind("Refresh", "<Button-1>", lambda event: LoadNew(canvas))

	AddStationsToDisplay(canvas)

	canvas.create_text(
		550.0,
		30.0,
		anchor="nw",
		text="Radio wale Babu",
		fill="#FFFFFF",
		font=("Comic Sans MS", 50 * -1, "bold"),
		justify="center"
	)
	
	canvas.create_text(
		70.0,
		150.0,
		anchor="nw",
		text="Stations",
		fill="#FFFFFF",
		font=("Comic Sans MS", 36 * -1),
		justify="center"
	)
		# return siteIP

	# e1 = Entry(window, lambda event: siteIPFunc(canvas))
	# e1.grid(row=0, column=1)

	inputtxt = tk.Text(window, height = 1, width = 30)  
	inputtxt.place(x = 580, y = 120)
	inputtxt.insert(tk.END, "Enter IP Address")
	inputtxt.configure(bg = "#262626", fg = "#FFFFFF", font=("Comic Sans MS", 20 * -1))
	inputtxt.bind("<Button-1>", lambda event: inputtxt.delete("1.0", tk.END))

	# button = tk.Button(window, text="Enter", command = siteIPFunc)
	# button.place(x = 500, y = 130)
	# button.configure(bg = "#262626", fg = "#FFFFFF", font=("Comic Sans MS", 15 * -1))


	canvas.create_rectangle(
		389.0,
		620.0,
		981.0,
		700.0,
		fill="#B3d6f9",
		outline="")

	img = Image.open(relative_to_assets("image_2.png"))
	resize_img = img.resize((30,30), Image.ANTIALIAS)
	photo = ImageTk.PhotoImage(resize_img)
	
	image_2 = canvas.create_image(
		434.0,
		660.0,
		image=photo,
		tags=["stopPlaying"]
	)
	canvas.tag_bind("stopPlaying", "<Button-1>", StopAll)

	sn = canvas.create_text(
		470.0,
		648.0,
		anchor="nw",
		text=song_name,
		fill="#000000",
		font=("Comic Sans MS", 20 * -1)
	)

	tr = canvas.create_text(
		470.0,
		675.0,
		anchor="nw",
		text=time_rem,
		fill="#000000",
		font=("Comic Sans MS", 12 * -1)
	)

	canvas.create_rectangle(
		685.0,
		620.0,
		981.0,
		700.0,
		fill="#69451f",
		outline="")

	img_3 = Image.open(relative_to_assets("image_3.png"))
	resize_img_3 = img_3.resize((30,30), Image.ANTIALIAS)
	image_image_3 = ImageTk.PhotoImage(resize_img_3)

	image_3 = canvas.create_image(
		730.0,
		660.0,
		image=image_image_3,
	)

	ns = canvas.create_text(
		760.0,
		648.0,
		anchor="nw",
		text=next_song_name,
		fill="#FFFFFF",
		font=("Comic Sans MS", 20 * -1)
	)

	img_5 = Image.open(relative_to_assets("mello.png"))
	resize_img_5 = img_5.resize((400,500))
	image_image_5 = ImageTk.PhotoImage(resize_img_5)

	image_5 = canvas.create_image(
		985.0+150,
		450.0,
		image=image_image_5,
	)

	clock(canvas, sn, ns, tr)
	
	window.resizable(True, True)
	window.mainloop()
	stop_playing = True
