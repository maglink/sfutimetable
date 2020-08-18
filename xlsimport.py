import os
import re
import xlrd
from lessonmongo import db_add_lesson,drop_table,db_index
from lessontime import get_time,get_time_code,get_day_code,get_daytime_code,get_time_by_code
from colorama import init, Fore
init()

#Magic data
EDGE_X,EDGE_Y = 3,5
TITLE_DAY, TITLE_TIME, TITLE_WEEK  = "Дни", "Часы", "Неделя"
TEACHER_NAME_PAT = "(\w+\s\w\.\w\.)\s*"
AUDIT_PAT = "\/(\d{3}\w|\d{3})"
LESSON_TYPE_PAT = "(пр|лек|лаб)"

def write_lesson_to_db(lesson_data):
	db_add_lesson(lesson_data)

def drop_db_tables():
	drop_table()

def process_dir(dir_name):
	dir_list = [x for x in os.listdir(dir_name) if x.endswith(".xls")]
	for file_name in dir_list:
		try:
			print("Processing file:  {} ".format(file_name), end="")
			process_file(dir_name + file_name)
			print(Fore.GREEN + " [OK]" + Fore.RESET)
		except Exception as err:
			print(Fore.RED + " [FAIL]" + Fore.RESET, err)

def process_file(file_name):
	file = xlrd.open_workbook(file_name)
	sheet_name = file.sheet_names()[0]
	sheet = file.sheet_by_name(sheet_name)

	edge_x, edge_y = find_edge(sheet)

	for specialty,group,x,y in read_specialties(sheet, edge_x, edge_y):
		for lesson in read_group(sheet,x,y):
			write_lesson_to_db(dict(lesson, group = group))
		print (".", end="") #processed specialty

def find_edge(sheet):
	x=0
	for y in range(0, 10):
		if (sheet.cell(y,x).value == TITLE_DAY
		and sheet.cell(y,x+1).value == TITLE_TIME
		and sheet.cell(y,x+2).value == TITLE_WEEK):
			return x+3, y
	for y in range(0, 15):
		day = sheet.cell(y,x).value
		try:
			if (get_day_code(day) > 0
			and sheet.cell(y-2,x+1).value == TITLE_TIME
			and sheet.cell(y-2,x+2).value == TITLE_WEEK):
				return x+3, y-2
			if (get_day_code(day) > 0 #subgroups
			and sheet.cell(y-3,x+1).value == TITLE_TIME
			and sheet.cell(y-3,x+2).value == TITLE_WEEK):
				return x+3, y-3
		except:
			continue;
	raise Exception("Edge not found")
	
def read_specialties(sheet,x,y):
	ncols = sheet.ncols
	has_next_group = True

	if not sheet.cell(y,x).value:
		raise Exception("Speciality is not defined")

	if not sheet.cell(y+1,x).value:
		raise Exception("Group is not defined")
	
	while(has_next_group):
		specialty =  sheet.cell(y,x).value or specialty
		group = sheet.cell(y+1,x).value
		group, start_y = subgroup_add(sheet, group, x, y+2)
		group = group_trim(group)

		yield specialty,group,x,start_y
		
		x += 1
		if(x >= ncols or sheet.cell(y+1,x).value == ""):
			has_next_group = False

def group_trim(string):
	if string:
		string = string.replace("\r", "")
		string = string.replace("\n", "")
		while(not string.find("  ") == -1):
			string = string.replace("  ", " ")
	return string.strip()

def subgroup_add(sheet, group, x, y):
	if sheet.cell(y,0).value:
		return group, y
	if not sheet.cell(y,x).value:
		Exception("Subgroup is not defined")
	group = '{0} ({1})'.format(group, sheet.cell(y,x).value)
	return group, y+1

def read_group(sheet,x,y):
	nrows = sheet.nrows# - y-1;
	if not sheet.cell(y,0).value:
		raise Exception("Day value not found")

	for ypos in range(y, nrows, 6):
		day = sheet.cell(ypos,0).value or day
		time = sheet.cell(ypos,1).value

		if not time:
			continue

		try:
			time_start, time_end = get_time(time)
		except:
			continue
		
		datetime_code1, datetime_code2 = get_daytime_code(day,time_start,time_end)

		for datetime_code in range(datetime_code1, datetime_code2+1):
			this_time_start = time_start
			if datetime_code != datetime_code1:
				this_time_start = get_time_by_code(datetime_code, "start")

			this_time_end = time_end
			if datetime_code != datetime_code2:
				this_time_end = get_time_by_code(datetime_code, "end")
			
			time_data = {
				"day_code": get_day_code(day),
				"time_code": datetime_code,
				"time_start":  this_time_start, 
				"time_end": this_time_end,
				"time_start_code": get_time_code(this_time_start),
				"time_end_code": get_time_code(this_time_end),
			}
			
			lesson_w1 = process_lesson(read_lesson(sheet,x,ypos))
			lesson_w2 = process_lesson(read_lesson(sheet,x,ypos+3))

			if any(lesson_w1.values()):
				if lesson_w1 == lesson_w2:
					yield dict(lesson_w1, week=0, **time_data)
					continue
				else:
					yield dict(lesson_w1, week=1, **time_data)

			if any(lesson_w2.values()):
				yield dict(lesson_w2, week=2, **time_data)


def read_lesson(sheet,x,y):
	subject = sheet.cell(y+0,x).value
	teacher = sheet.cell(y+1,x).value
	auditorium = sheet.cell(y+2,x).value

	teacher = re.sub(' +',' ',teacher)
	
	if not type(auditorium) == str:
		auditorium = ""
		
	return (subject, teacher, auditorium)


def process_lesson(lesson_raw):
	subject = lesson_raw[0].strip()
	teacher_list = re.findall(TEACHER_NAME_PAT, lesson_raw[1], re.VERBOSE | re.IGNORECASE)
	audit_list = re.findall(AUDIT_PAT, lesson_raw[2], re.VERBOSE | re.IGNORECASE)
	for i in range(len(audit_list)):
		audit_list[i] = audit_list[i].upper()
	
	lesson_type = re.findall(LESSON_TYPE_PAT, lesson_raw[2], re.VERBOSE | re.IGNORECASE)
	lesson_type = lesson_type[0].lower() if lesson_type else ''

	lesson_data = {"lesson_type": lesson_type, "subject": subject, "teacher_list": teacher_list, "audit_list":audit_list}
	return lesson_data


if __name__ == "__main__":
	print("Dropping db")
	drop_db_tables()
	print("Importing data:")
	process_dir('data/')
	print("Indexing...")
	db_index()
	print("[DONE]")
