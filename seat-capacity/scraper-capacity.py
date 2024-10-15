import asyncio
import aiohttp
import csv
from bs4 import BeautifulSoup
import time

# Maximum number of concurrent requests
CONCURRENT_REQUESTS = 10

async def fetch_details(session, sem, term, crn):
    url = f"https://www.uvic.ca/BAN1P/bwckschd.p_disp_detail_sched?term_in={term}&crn_in={crn}"
    headers = {
        'User-Agent': 'Mozilla/5.0'  # Generic User-Agent
    }
    async with sem:
        for attempt in range(3):  # Retry up to 3 times
            try:
                print(f"Fetching details for term {term} CRN {crn} (attempt {attempt + 1})...", flush=True)
                async with session.get(url, headers=headers, timeout=10) as response:
                    response.raise_for_status()  # Raise exception for HTTP errors
                    html_content = await response.text()
                    print(f"Successfully fetched details for term {term} CRN {crn}.", flush=True)
                    return html_content
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                wait_time = 2 ** attempt
                print(f"Attempt {attempt + 1} failed for term {term} CRN {crn}: {e}. Retrying in {wait_time} seconds...", flush=True)
                await asyncio.sleep(wait_time)
        print(f"Failed to fetch details for term {term} CRN {crn} after 3 attempts.", flush=True)
        return None

def parse_details_html(html_content, term, crn):
    soup = BeautifulSoup(html_content, 'html.parser')

    course_info = {
        'term': term,
        'crn': crn,
        'Seats_Capacity': '',
        'Seats_Actual': '',
        'Seats_Remaining': '',
        'Waitlist_Capacity': '',
        'Waitlist_Actual': '',
        'Waitlist_Remaining': ''
    }

    # Find the table with caption "Registration Availability"
    tables = soup.find_all('table', class_='datadisplaytable')
    reg_table = None
    for table in tables:
        caption = table.find('caption', class_='captiontext')
        if caption and 'Registration Availability' in caption.text:
            reg_table = table
            break

    if reg_table is None:
        print(f"No 'Registration Availability' table found for term {term}, CRN {crn}.", flush=True)
        return None

    # Now parse the rows in reg_table
    rows = reg_table.find_all('tr')
    data_rows = rows[1:]  # Skip the header row

    for row in data_rows:
        headers = row.find_all('th')
        cells = row.find_all('td')
        if headers and len(headers) >= 1 and len(cells) >= 3:
            label = headers[0].get_text(strip=True)
            capacity = cells[0].get_text(strip=True)
            actual = cells[1].get_text(strip=True)
            remaining = cells[2].get_text(strip=True)
            if label == 'Seats':
                course_info['Seats_Capacity'] = capacity
                course_info['Seats_Actual'] = actual
                course_info['Seats_Remaining'] = remaining
            elif label == 'Waitlist Seats':
                course_info['Waitlist_Capacity'] = capacity
                course_info['Waitlist_Actual'] = actual
                course_info['Waitlist_Remaining'] = remaining

    return course_info

def save_details_to_csv(courses, filename):
    fieldnames = [
        'term', 'crn', 'Seats_Capacity', 'Seats_Actual', 'Seats_Remaining',
        'Waitlist_Capacity', 'Waitlist_Actual', 'Waitlist_Remaining'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for course in courses:
            writer.writerow(course)
    print(f"Data has been saved to {filename}.", flush=True)

async def fetch_and_parse_details(session, sem, term, crn):
    html_content = await fetch_details(session, sem, term, crn)
    if html_content:
        course_info = parse_details_html(html_content, term, crn)
        return course_info
    else:
        return None

async def main():
    start_time = time.time()
    print("Script started.", flush=True)
    all_courses = []
    
    # Read 'scraped_course_data.csv' and get unique term and crn pairs
    terms_crns = set()
    with open('scraped_course_data.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            term = row['term']
            crn = row['crn']
            terms_crns.add((term, crn))
    
    sem = asyncio.Semaphore(CONCURRENT_REQUESTS)
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for term, crn in terms_crns:
            tasks.append(
                fetch_and_parse_details(session, sem, term, crn)
            )
        
        # Process tasks concurrently with progress indication
        total_tasks = len(tasks)
        completed_tasks = 0
        for future in asyncio.as_completed(tasks):
            course_info = await future
            completed_tasks += 1
            print(f"Completed {completed_tasks}/{total_tasks} tasks.", flush=True)
            if course_info:
                all_courses.append(course_info)
    
    # Save all the scraped data to a new CSV file
    save_details_to_csv(all_courses, 'course_capacity_data.csv')
    end_time = time.time()
    total_time = end_time - start_time
    hours, rem = divmod(total_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Script execution time: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds), flush=True)
    print("Script finished.", flush=True)

if __name__ == "__main__":
    asyncio.run(main())