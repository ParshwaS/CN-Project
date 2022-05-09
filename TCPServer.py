import socket            
from utils import site_info

s = socket.socket()
print ("Socket successfully created")

port = 5432

s.bind(('127.0.0.1', port))        
print ("socket binded to %s" %(port))
 
s.listen(5)    
print ("socket is listening")

site_name = "Daddy Radio"
site_desc = "Daddy Radio is a radio station that broadcasts from the Ahmedabad University."
stations = [
	{
		"number": 1,
		"name": "New",
		"multicast_ip": "239.192.12.1",
		"multicast_port": 6253,
		"multicast_infoport": 6235,
		"bitrate": 128,
	},
	{
		"number": 2,
		"name": "Old",
		"multicast_ip": "239.192.12.2",
		"multicast_port": 6253,
		"multicast_infoport": 6235,
		"bitrate": 128,
	}
]
 
while True:
	c, addr = s.accept()
	data = c.recv(1024)
	if(data[0] == 1):
		data = site_info(site_name, site_desc, stations)
		c.send(data)
	c.close()