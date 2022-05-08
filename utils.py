def radio_stn_info():
	type_t = (1).to_bytes(1, 'big')
	data = type_t
	return data

def site_info(site_name, site_desc, stations):
	type_t = (10).to_bytes(1, 'big')
	site_name_size_t = (len(site_name)).to_bytes(1, 'big')
	site_name = site_name.encode('ascii')
	site_desc_size_t = (len(site_desc)).to_bytes(1, 'big')
	site_desc = site_desc.encode('ascii')
	stations_size_t = (len(stations)).to_bytes(1, 'big')
	data = type_t + site_name_size_t + site_name + site_desc_size_t + site_desc + stations_size_t
	for station in stations:
		data += station_info(station)
	return data

def station_info(station):
	station_number = station['number'].to_bytes(1, 'big')
	station_name_size_t = (len(station['name'])).to_bytes(1, 'big')
	station_name = station['name'].encode('ascii')
	temp = [*map(int, station['multicast_ip'].split('.'))]
	station_multicast_ip = temp[0].to_bytes(1, 'big')
	station_multicast_ip += temp[1].to_bytes(1, 'big')
	station_multicast_ip += temp[2].to_bytes(1, 'big')
	station_multicast_ip += temp[3].to_bytes(1, 'big')
	station_multicast_port = station['multicast_port'].to_bytes(2, 'big')
	station_multicast_infoport = station['multicast_infoport'].to_bytes(2, 'big')
	station_inforate = station['bitrate'].to_bytes(4, 'big')
	data = station_number + station_name_size_t + station_name + station_multicast_ip + station_multicast_port + station_multicast_infoport + station_inforate
	return data

def song_info(song_name, next_song_name, rem_time):
	type_t = (12).to_bytes(1, 'big')
	song_name_size_t = (len(song_name)).to_bytes(1, 'big')
	song_name = song_name.encode('ascii')
	remaining_time = rem_time.to_bytes(2, 'big')
	next_song_name_size_t = (len(next_song_name)).to_bytes(1, 'big')
	next_song_name = next_song_name.encode('ascii')
	data = type_t + song_name_size_t + song_name + remaining_time + next_song_name_size_t + next_song_name
	return data

def get_song_info(data):
	song_name_size_t = int.from_bytes(data[1:2], 'big')
	song_name = data[2:2+song_name_size_t].decode('ascii')
	remaining_time = int.from_bytes(data[2+song_name_size_t:4+song_name_size_t], 'big')
	next_song_name_size_t = int.from_bytes(data[4+song_name_size_t:5+song_name_size_t], 'big')
	next_song_name = data[5+song_name_size_t:5+song_name_size_t+next_song_name_size_t].decode('ascii')
	return song_name, next_song_name, remaining_time

def get_station_info(data):
	station_number = int.from_bytes(data[0:1], 'big')
	station_name_size_t = int.from_bytes(data[1:2], 'big')
	station_name = data[2:2+station_name_size_t].decode('ascii')
	station_multicast_ip = data[2+station_name_size_t:6+station_name_size_t]
	temp = ""
	for i in range(0, 4):
		temp += str(station_multicast_ip[i]) + "."
	station_multicast_ip = temp[:-1]
	station_multicast_port = int.from_bytes(data[6+station_name_size_t:8+station_name_size_t], 'big')
	station_multicast_infoport = int.from_bytes(data[8+station_name_size_t:10+station_name_size_t], 'big')
	station_inforate = int.from_bytes(data[10+station_name_size_t:14+station_name_size_t], 'big')
	total_size = 14+station_name_size_t
	return station_number, station_name, station_multicast_ip, station_multicast_port, station_multicast_infoport, station_inforate, total_size

def get_site_info(data):
	site_name_size_t = int.from_bytes(data[1:2], 'big')
	site_name = data[2:2+site_name_size_t].decode('ascii')
	site_desc_size_t = int.from_bytes(data[2+site_name_size_t:3+site_name_size_t], 'big')
	site_desc = data[3+site_name_size_t:3+site_name_size_t+site_desc_size_t].decode('ascii')
	stations_size_t = int.from_bytes(data[3+site_name_size_t+site_desc_size_t:4+site_name_size_t+site_desc_size_t], 'big')
	stations = []
	total_size = 4+site_name_size_t+site_desc_size_t
	for i in range(stations_size_t):
		station_number, station_name, station_multicast_ip, station_multicast_port, station_multicast_infoport, station_inforate, add_size = get_station_info(data[total_size:])
		stations.append({'number': station_number, 'name': station_name, 'multicast_ip': station_multicast_ip, 'multicast_port': station_multicast_port, 'multicast_infoport': station_multicast_infoport, 'inforate': station_inforate})
		total_size += add_size
	return site_name, site_desc, stations, total_size