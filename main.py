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
    regex = {
        "data":r"(?s)<tbody.*?</tbody>",
        "rowData":r'(?s)<tr.*?</tr>',
        "courseID":r'(?s)<td>\s*<div>\s*<span>\s*(?P<courseID>\d+)\s*</span>\s*</div>\s*</td>',
    }

    with open('schedule-2564.html', mode='r', encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')
        
        s = re.findall(regex["data"], str(soup))
        
        s = re.findall(regex["rowData"], s[0])
        print(BeautifulSoup(s[2], 'html.parser').prettify())
        courseID = re.search(regex["courseID"], s[0])
        print(courseID.groupdict())


# For Real Scraping
asyncio.get_event_loop().run_until_complete(main())

# For Local development
local_scraping()
