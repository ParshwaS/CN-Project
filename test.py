from utils import get_site_info, get_song_info, get_station_info, radio_stn_info, site_info, station_info

site_name = "Daddy Radio"
site_desc = "Daddy Radio is a radio station that broadcasts from the Ahmedabad University."
stations = [
	{
		"number": 1,
		"name": "Radio 1",
		"multicast_ip": "230.192.12.1",
		"multicast_port": 6253,
		"multicast_infoport": 6235,
		"bitrate": 128,
	},
	{
		"number": 2,
		"name": "Radio 2",
		"multicast_ip": "230.192.12.2",
		"multicast_port": 6253,
		"multicast_infoport": 6235,
		"bitrate": 128,
	}
]

data = site_info(site_name, site_desc, stations)
test2 = get_site_info(data)
data = station_info(stations[0])
# test1 = get_station_info(data)
# test3 = get_station_info(test2)
print(data, "\n",test2)