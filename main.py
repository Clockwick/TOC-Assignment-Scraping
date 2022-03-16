import asyncio
from bs4 import BeautifulSoup
from pyppeteer import launch
import os
import re

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
    page_path = 'https://new.reg.kmitl.ac.th/reg/#/teach_table?mode=by_class&selected_year=2564&selected_semester=2&selected_faculty=01&selected_department=05&selected_curriculum=06&selected_class_year=3&search_all_faculty=false&search_all_department=false&search_all_curriculum=false&search_all_class_year=false'

    # Open our test file in the opened page
    await page.goto(page_path, {'waitUntil': 'networkidle0'})
    page_content = await page.content()

    # Process extracted content with BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')
    print(soup.span.string)

    # Close browser
    await browser.close()


def local_scraping():
    # r'(?s)<td>\s*<div>\s*<span>\s*(?P<courseID>\d*)\s*</span>\s*</div>\s*</td>\s*<td>\s*<a[^>]*>\s*(?P<courseName>\s*|\w+[\s\w]*\w+)\s*</a>\s*</td>\s*<td>\s*(?P<unit>\s*|\d{1}\(\d{1}-\d{1}-\d{1}\))\s*</td>\s*<td[^>]*>\s*(?P<section>\d+)\s*<span>\s*<span[^>]*>\s*<span[^>]*>\s*(?P<type>\s*|[\u0E00-\u0E7F]*)\s*</span>\s*</span>\s*</span>\s*</td>\s*'
    regex = {
        "table":r"(?s)<tbody.*?</tbody>",
        "rowData":r'(?s)<tr.*?</tr>',
        "data":r'(?s)<td><div><span>(?P<courseID>\s*|\d*)</span></div></td><td><a[^>]*>(?P<courseName>\s*|\w+[\s\w]*\w+)</a></td><td>(?P<unit>\s*|\d{1}\(\d{1}-\d{1}-\d{1}\))</td><td[^>]*>(?P<section>\s*|\d+)<span><span[^>]*><span[^>]*>(?P<type>\s*|[\u0E00-\u0E7F]*)</span></span></span></td><td[^>]*><a[^>]*>[<div>]*(?P<schedule>.*?)[</div>]*</a></td><td>(?P<room>.*?)</td><td>(?P<building>.*?)</td><td[^>]*><div>(?P<teacher>.*?)</div></td><td.*?><span.*?/span><span[^>]*>(?P<midterm>.*?)</span>.*?<span.*?/span><span[^>]*>(?P<final>.*?)<.*?/td><td.*?v>(?P<condition>.*?)</div></td><td.*?v>(?P<note>.*?)<.*?></td>',
        "teacher":r'(?s)<div>(.*?)</div>',
        "condition":r'(?s)<div>(.*?)<div.*?/div></div>'
    }
    
    with open('schedule-2564.html', mode='r', encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')
        
        # minify html
        minify_string = re.sub(r'(?s)<!--.*?-->|\s{3,}|\n','',str(soup))

        # get all table
        tables = re.findall(regex["table"], str(minify_string))

        for table in tables:

            rows = re.findall(regex["rowData"], table)

            for row in rows:

                data_rex = re.search(regex["data"], row)

                teacher_list = re.findall(regex['teacher'], data_rex.group('teacher'))
                condition_list = re.findall(regex['condition'], data_rex.group('condition'))

                data = data_rex.groupdict()

                data['teacher'] = teacher_list
                data['condition'] = condition_list

                print(data)

def test_regex():
    test = """
        <td>
            <div>
                เฉพาะรหัส 60000001-63999999
                <div>
                    <font color="red">
                        (ไม่รับนศ.อื่น)
                    </font>
                </div>
            </div>
        </td>
    """
    minify_string = re.sub(r'(?s)<!--.*?-->|\s{3,}|\n','',str(test))
    # print(minify_string)
    testreg = r'(?s)<td.*?v>(?P<note>.*?)<.*?></td>'
    
    result = re.search(testreg, minify_string)
    
    # iterreg = r'(?s)<div>(.*?)<div.*?/div></div>'
    # result_list = re.findall(iterreg, result.group('condition'))

    print(result.groupdict())
    # print(result_list)


# For Real Scraping
# asyncio.get_event_loop().run_until_complete(main())

# For Local development
# test_regex()
local_scraping()
