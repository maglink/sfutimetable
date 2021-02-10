import math
import Levenshtein

DAY_DICT = {
	1: "ПОНЕДЕЛЬНИК",
	2: "ВТОРНИК",
	3: "СРЕДА",
	4: "ЧЕТВЕРГ",
	5: "ПЯТНИЦА",
	6: "СУББОТА",
}

TIME_DICT = {
	1: {
		"start": "8:30",
		"end": "10:05",
	},
	2: {
		"start": "10:15",
		"end": "11:50",
	},
	3: {
		"start": "12:00",
		"end": "13:35",
	},
	4: {
		"start": "14:10",
		"end": "15:45",
	},
	5: {
		"start": "15:55",
		"end": "17:30",
	},
	6: {
		"start": "17:40",
		"end": "19:15",
	},
	7: {
		"start": "19:25",
		"end": "21:00",
	},
	8: {
		"start": "21:10",
		"end": "22:45",
	},
}


def get_daytime_code(day,time_start,time_end):
	day = get_day_code(day)*10
	time_code_start = near_time(time_start, "start")
	time_code_end = near_time(time_end, "end")
	return day + time_code_start, day + time_code_end

def get_time_by_code(code, time_type):
	day = math.floor(code/10)
	time = code-(day*10)
	return TIME_DICT[time][time_type]

# Time

def near_time(time, time_type):
	time_code = get_time_code(time)
	near = 1
	near_val = 60*24
	for lkey, ltime in TIME_DICT.items():
		ltime_code = get_time_code(ltime[time_type])
		if time_code == ltime_code:
			return lkey
		val =  abs(ltime_code - time_code)
		if val < near_val:
			near = lkey
			near_val = val
	return near

def get_time_code(time):
	timeH, timeM = time.split(":");
	minutes = int(timeH)*60 + int(timeM);
	return minutes

def get_time(time):
	if time.find("-") == -1:
		raise Exception("Time has incorrect syntax")
	time_start, time_end = time.split("-");
	time_start = time_format(time_start)
	time_end = time_format(time_end)
	return time_start, time_end

def time_format(time):
	time = time.replace(" ", "").strip('.').replace(".", ":")
	time = time.strip(',').replace(",", ":")
	return time_insert_colon(time)

def time_insert_colon(time):
	colon_chr = ':'
	if time.find(colon_chr) == -1:
		index = -2
		if len(time) + index > 0:
			return time[:index] + colon_chr + time[index:]
		else:
			return
	return time

# Day

def get_day_code(day):
	day = day.upper();
	for dkey, dname in DAY_DICT.items():
		if dname == day:
			return dkey
	return near_day(day)
	
def near_day(day):
	day = day.strip()
	near = 1
	near_ratio = 0
	for dkey, dname in DAY_DICT.items():
		ratio = Levenshtein.ratio(dname, day)
		if ratio > near_ratio:
			near = dkey
			near_ratio = ratio
	if near_ratio > 0.7:
		return near
	raise Exception("Day is not defined")

# Main

if __name__ == "__main__":
	assert time_insert_colon("830") == "8:30"
	assert time_insert_colon("0830") == "08:30"
	assert time_insert_colon("08") == None
	assert time_format("830.") == "8:30"
	assert time_format(" .8 .30.") == "8:30"
	assert time_format(" ..30.") == None
	assert get_time("8.30-10:05") == ("8:30","10:05")
	assert get_time_code("05:01") == 301
	assert near_time("8:31", "start") == 1
	assert near_time("10:11", "start") == 2
	assert near_time("12:11", "start") == 3
	assert near_time("14:11", "start") == 4
	assert near_time("15:30", "start") == 5
	assert near_time("18:00", "start") == 6
	assert near_time("19:15", "start") == 7
	assert near_time("21:00", "start") == 8
	assert near_time("10:11", "end") == 1
	assert near_time("12:11", "end") == 2
	assert near_time("14:11", "end") == 3
	assert near_time("15:30", "end") == 4
	assert near_time("18:00", "end") == 5
	assert near_time("19:15", "end") == 6
	assert near_time("21:00", "end") == 7
	assert near_time("22:30", "end") == 8
	assert get_day_code("понедельник") == 1
	assert get_day_code("понеделник") == 1
	assert get_day_code("фтарник") == 2
	assert get_daytime_code("понедельник","8:31","10:05") == (11, 11)
	assert get_daytime_code("понедельник","8:31","12:11") == (11, 12)
	assert get_time_by_code(25, "end") == "17:30"
	assert get_time_code(get_time_by_code(42, "start")) == 615





