from pymongo import MongoClient

client = MongoClient()

db = client.lesson_database
lessons = db.lesson_database

def db_add_lesson(lesson_data):
    lessons.insert(lesson_data)

def drop_table():
    lessons.drop()

def db_index():
    teachers = db.teacher_database
    audits = db.audit_database

    teachers.drop()
    for teacher in lessons.distinct("teacher_list"):
        teachers.insert(dict(teacher_list=teacher))
    
    audits.drop()
    for audit in lessons.distinct("audit_list"):
        audits.insert(dict(audit_list=audit))

def print_all_groups():
    res = lessons.distinct("group")
    for les in res:
        print(les)
        
    print("#",len(res))

def print_all_lessons():
    for les in lessons.find().sort("time_code"):
        print(les)

def print_schedule_for_group(group):
    print("Группа:", group)
    res = lessons.find({"group":group}).sort("time_code")
    for les in res:
        pprint_lesson(les)

def print_teachers():
    res = lessons.distinct("teacher_list")
    for teacher in res:
        print(teacher)

    print("#",len(res))

def print_lessons_for_teacher(teacher):
    print("Преподаватель:", teacher)
    res = lessons.find({ "teacher_list": teacher }).sort("time_code")
    for les in res:
        pprint_lesson(les)

def print_audit(audit):
    print("Аудитория:",audit)
    res = lessons.find({ "audit_list": audit }).sort("time_code")
    for les in res:
        pprint_lesson(les)

def pprint_lesson(ls):
    week = str(ls['week'])+'.' if ls['week'] else ""
    audit = ", ".join(ls['audit_list'])
    teacher = ", ".join(ls['teacher_list'])
    print("{l[time_code]}-{l[week]}; {l[time_start]:>5}-{l[time_end]}; {l[group]}; \t{l[subject]:^50}; {a:>6}; {t}".format(l=ls, a=audit, t=teacher))


def test_print_all():
    print_all_groups()
    print("----")
    print_teachers()
    print("----")

def test_schedule_for_group():  
    print_schedule_for_group("УБ12-10")
    print("----")

def test_lessons_for_teacher(): 
    print_lessons_for_teacher("Поваляев В.А.")
    print("----")
    print_lessons_for_teacher("Бронов С.А.")
    print("----")
    print_lessons_for_teacher("Авласко П.В.")
    print("----")
    
def test_print_audit():
    print_audit("УЛК407")
    print("----")
    print_audit("УЛК307")
    print("----")
    print_audit({"$regex" : ".*Г.*"})
    print("----")
    print_audit({"$regex" : ".*А3.*"})
    print("----")
    
if __name__ == "__main__":
    #test_print_all()
    test_schedule_for_group()
    test_lessons_for_teacher()
    test_print_audit()
