import asyncio
from bs4 import BeautifulSoup
from pyppeteer import launch
import os


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
    with open('schedule-2564.html', 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
        print(soup.prettify())


# For Real Scraping
asyncio.get_event_loop().run_until_complete(main())

# For Local development
local_scraping()
