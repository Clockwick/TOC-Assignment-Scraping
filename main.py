import asyncio
from calendar import c
from encodings import utf_8
from statistics import mode
from turtle import pd
from xml.sax import parseString
from bs4 import BeautifulSoup
from pyppeteer import launch
import os
import re
import json
'''
TODO:
    1. เอาข้อมูล col มาใส่เป็น List
'''


async def main():
    # Launch the browser
    browser = await launch()

    # Open a new browser page
    page = await browser.newPage()

    # Create a URI for our test file
    page_path = 'https://new.reg.kmitl.ac.th/reg/#/teach_table?mode=by_class&selected_year=2564&selected_semester=2&selected_faculty=01&selected_department=05&selected_curriculum=06&selected_class_year&search_all_faculty=false&search_all_department=false&search_all_curriculum=false&search_all_class_year=true'

    # Open our test file in the opened page
    await page.goto(page_path, {'waitUntil': 'networkidle0'})
    page_content = await page.content()

    # Process extracted content with BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')
    with open('a.html', mode='w', encoding="utf-8") as f:
        f.write(soup.prettify())
    # json_payload = scraping_html(soup.prettify())

    # print(json_payload)
    # Close browser
    await browser.close()


def local_scraping_html():

    json_payload = ""
    a = 'a.html'
    b = 'schedule-2564.html'
    with open(b, mode='r', encoding="utf-8") as f:

        soup = BeautifulSoup(f, 'html.parser')
        # make html in compatible format ( important!!! )
        json_payload = scraping_html(soup.prettify())

    with open("datahtml.json", mode='w', encoding='utf_8') as jsonfile:
        jsonfile.write(json_payload)


def local_scraping_pdf():

    json_payload = ""
    with open("mockpdf.txt", mode='r', encoding='utf-8') as pdf:
        json_payload = scraping_pdf(pdf.read())

    with open("datapdf.json", mode='w', encoding='utf_8') as jsonfile:
        jsonfile.write(json_payload)


def scraping_html(prettified_string):

    # {
    #     "subjects": [
    #         {
    #             "faculty": "",
    #             "major": "",
    #             "field": "",
    #             "field_subjects": [
    #                 "type":"",
    #                 "courses":[
    #                     "courseId":"",
    #                     "courseName:"",
    #                     "credit":"",
    #                     "section":"",
    #                     "type":"",
    #                     "schedule":[],
    #                     "room":"",
    #                     "building":"",
    #                     "teacher":[],
    #                     "midterm":"",
    #                     "final":"",
    #                     "restriction":[],
    #                     "note":""
    #                 ]
    #             ]
    #         }
    #     ]
    # }

    regex = {
        "top": r'<main.*?<.*?<.*?<.*?<.*?<.*?<h2[^>]*>(?P<tableheader>.*?)</h2>.*?<h2[^>]*>(?P<semester>.*?)</h2></div><div[^>]*><div[^>]*>(?P<alltable>.*?)</div></div></div><div[^>]*><button.*?/button></div></div></div></div></main>',

        "all_subjects": r'<div.*?><h2[^>]*>(?P<faculty>.*?)</h2><h2[^>]*>(?P<major>.*?)</h2><h2[^>]*>(?P<field>.*?)</h2>(?P<field_subjects>.*?)</div><div class="v-card__actions">.*?</div></div>',

        "courses": r'<div><div[^>]*>(?P<type>.*?)</div><div[^>]*><div[^>]*><table>(?P<courses>.*?)</table></div></div></div>',

        "tbody": r"<tbody.*?/tbody>",

        "rowData": r'<tr.*?/tr>',

        "data": r'<td><div><.*?>(?P<courseID>\s*|\d*)</.*?></div></td><td><a[^>]*>(?P<courseName>\s*|\w+[\s\w]*\w+)</a></td><td>(?P<credit>\s*|\d{1}\(\d{1,2}-\d{1,2}-\d{1,2}\))</td><td[^>]*>(?P<section>\s*|\d+)<span>(?P<typediv>.*?)</span></td><td[^>]*><a[^>]*>(?P<schedule_all>.*?)</a></td><td>(?P<room>.*?)</td><td>(?P<building>.*?)</td><td[^>]*><div>(?P<teacher>.*?)</div></td><td[^>]*>(?P<exam>.*?)</td><td.*?v>(?P<restriction>.*?)</div></td><td.*?v>(?P<note>.*?)<.*?></td>',
        
        "type": r'<.*?>(?P<type>[\u0E00-\u0E7F]*)</span></span>',

        "exam": r'<div><span.*?<span.*?<span[^>]*>(?P<midterm>.*?)</span></div><div><span.*?<span.*?<span[^>]*>(?P<final>.*?)</span></div>',

        "teacher": r'<div>(.*?)</div>',

        "schedule": r'<div>(?P<schedule>[+ ]{,2}[\u0E00-\u0E7F]{1,2}. \d{2}:\d{2}-\d{2}:\d{2})</div>',

        "restriction": r'<div>(.*?)<div.*?/div></div>'
    }

    payload = {}

    minify_string = re.sub(
        r'(?s)<!--.*?-->|\s{3,}|\n', '', str(prettified_string))

    # get the semester data
    top = re.search(regex['top'], str(minify_string))

    payload["semester"] = top.group('semester')

    all_subjects = re.findall(regex['all_subjects'], top.group('alltable'))

    payload["subjects"] = []

    for field_table in all_subjects:
        fs = {
            "faculty": field_table[0],
            "major": field_table[1],
            "field": field_table[2],
            "field_subjects": []
        }

        courses_tables = re.findall(regex['courses'], field_table[3])

        for course_table in courses_tables:
            t = {
                "type": course_table[0],
                "courses": []
            }

            courses = re.findall(regex["tbody"], course_table[1])

            for course in courses:
                rows = re.findall(regex["rowData"], course)

                for row in rows:
                    
                    data = {}
                    data_rex = re.search(regex["data"], row)

                    data['courseId'] = data_rex.group('courseID')
                    data['courseName'] = data_rex.group('courseName')
                    data['credit'] = data_rex.group('credit')
                    data['section'] = data_rex.group('section')

                    if data_rex.group('typediv') != '':
                        data['type'] = re.search(
                            regex['type'], data_rex.group('typediv')).group('type')
                    else:
                        data['type'] = ""

                    data['schedule'] = re.findall(
                        regex['schedule'], data_rex.group('schedule_all'))

                    data['room'] = data_rex.group('room')
                    data['building'] = data_rex.group('building')

                    data['teacher'] = re.findall(
                        regex['teacher'], data_rex.group('teacher'))

                    if data_rex.group('exam') != '':
                        exam = re.search(regex['exam'], data_rex.group('exam'))
                        data['midterm'] = exam.group('midterm')
                        data['final'] = exam.group('final')
                    else:
                        data['midterm'] = ""
                        data['final'] = ""

                    data['restriction'] = re.findall(
                        regex['restriction'], data_rex.group('restriction'))
                    data['note'] = data_rex.group('note')

                    t['courses'].append(data)

            fs['field_subjects'].append(t)

        payload['subjects'].append(fs)

    json_payload = json.dumps(
        payload, sort_keys=False, indent=4, ensure_ascii=False)

    return json_payload


def scraping_pdf(pdf_string):

    # {
    #     "studentId":"",
    #     "name":"",
    #     "birthday":"",
    #     "admission_year":"",
    #     "degree":"",
    #     "major":"",
    #     "total_credit":"",
    #     "subjects":[
    #         {
    #             "semester":"",
    #             "year":"",
    #             "GPS":"",
    #             "GPA":"",
    #             "courses":[
    #                 {
    #                     "courseId":'',
    #                     "courseName":"",
    #                     "credit":"",
    #                     "grade":""
    #                 }
    #             ]
    #         }
    #     ]
    # }

    regex = {
        "name": r'Name [Mrs]{2,3}.(?P<name>[-\w ]+)\n',

        "birthdayAndStudentId": r'Date of Birth (?P<birthday>[\w, ]+) StudentID (?P<studentId>\d{8})\n',

        "admission": r'Date of Admission\s*(?P<admission_year>\d{4})',

        "degree": r'Degree (?P<degree>[\w ]+)\n',

        "major": r'Major (?P<major>[\w ]+)\n',

        "semester": r'(?s)(?P<semester>\w{3}) Semester, Y\s*ear\s*, (?P<year>\d{4}-\d{4})\n(?P<courseInSem>.*?)GPS\s*: (?P<GPS>[\d.-]+) GPA\s*: (?P<GPA>[\d.-]+)\n',

        "courseInfo": r'(?P<courseID>\d{8}) (?P<courseName>.*?) (?P<credit>\d)\s*(?P<grade>[ABCDF+]*)\n(?P<namekern>[A-Z123 ]*)[\n]*',

        "cumuGPA": r'Cumulative GPA\s*: (?P<cumuGPA>\d.\d{2})',

        "totalCredit": r'Total number of credit earned\s*:\s*(?P<total_credit>\d{1,3})'
    }

    payload = {}

    minify_string = re.sub(r'\n{2,}', '\n', pdf_string)

    name = re.search(regex['name'], minify_string)

    birthdayAndStudentId = re.search(
        regex['birthdayAndStudentId'], minify_string)

    admission = re.search(regex['admission'], minify_string)

    degree = re.search(regex['degree'], minify_string)

    major = re.search(regex['major'], minify_string)

    cumuGPA = re.search(regex['cumuGPA'], minify_string)

    totalCredit = re.search(regex['totalCredit'], minify_string)

    semesters = re.findall(regex['semester'], minify_string)

    subjects = []
    for semester in semesters:

        semester_data = {
            "semester": semester[0],
            "year": semester[1],
            "GPS": semester[3],
            "GPA": semester[4],
            "courses": []
        }

        courses_insem = re.findall(regex['courseInfo'], semester[2])

        for course in courses_insem:
            course_data = {
                "courseId": course[0],
                "courseName": "",
                "credit": course[2],
                "grade": course[3]
            }
            # print(course)
            remain = ""
            if course[4] != "":
                remain = " " + course[4]

            course_data["courseName"] = course[1] + remain

            semester_data['courses'].append(course_data)

        subjects.append(semester_data)

    payload['studentId'] = birthdayAndStudentId.group('studentId')
    payload['name'] = name.group('name')
    payload['birthday'] = birthdayAndStudentId.group('birthday')
    payload['admission_year'] = admission.group('admission_year')
    payload['degree'] = degree.group('degree')
    payload['major'] = major.group('major')
    payload['total_credit'] = totalCredit.group('total_credit')
    payload['cumuGPA'] = cumuGPA.group('cumuGPA')
    payload['subjects'] = subjects

    json_payload = json.dumps(
        payload, sort_keys=False, indent=4, ensure_ascii=False)

    return json_payload


def test_regex(s, regex):
    pass


# For Real Scraping #{{{
# ----------------------------------------------------------

# asyncio.get_event_loop().run_until_complete(main())

# }}}

# For Local development #{{{
# ----------------------------------------------------------

# test_regex()
# local_scraping_pdf()
local_scraping_html()

# }}}
