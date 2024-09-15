import asyncio
import aiohttp
import csv
from bs4 import BeautifulSoup
import time
import re

# Maximum number of concurrent requests
CONCURRENT_REQUESTS = 10

async def fetch_course_data(session, sem, term, subject, course_number):
    url = f"https://www.uvic.ca/BAN1P/bwckctlg.p_disp_listcrse?term_in={term}&subj_in={subject}&crse_in={course_number}&schd_in="
    headers = {
        'User-Agent': 'Mozilla/5.0'  # Generic User-Agent
    }
    async with sem:
        for attempt in range(3):  # Retry up to 3 times
            try:
                print(f"Fetching data for {subject} {course_number} in term {term} (attempt {attempt + 1})...", flush=True)
                async with session.get(url, headers=headers, timeout=10) as response:
                    response.raise_for_status()  # Raise exception for HTTP errors
                    html_content = await response.text()
                    print(f"Successfully fetched data for {subject} {course_number} in term {term}.", flush=True)
                    return html_content
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                wait_time = 2 ** attempt
                print(f"Attempt {attempt + 1} failed for {subject} {course_number}: {e}. Retrying in {wait_time} seconds...", flush=True)
                await asyncio.sleep(wait_time)
        print(f"Failed to fetch data for {subject} {course_number} after 3 attempts.", flush=True)
        return None

def parse_html(html_content, term, subject, course_number):
    soup = BeautifulSoup(html_content, 'html.parser')
    sections = soup.find_all('th', class_='ddtitle')
    
    courses = []
    if not sections:
        print(f"No sections found for {subject} {course_number} in term {term}.", flush=True)
    for section in sections:
        course_info = {
            'term': term,
            'subject': subject,
            'course_name': '',
            'course_number': course_number,
            'crn': '',
            'section': '',  # Added 'section' field
            'frequency': '',
            'time': '',
            'days': '',
            'location': '',
            'date_range': '',
            'schedule_type': '',
            'instructor': '',
            'instructional_method': '',
            'units': '',
            'additional_information': ''
        }
        
        # Extract course title
        title = section.find('a').text.strip()
        
        # Updated parsing logic for title
        # Expected format: 'Course Name - CRN - Subject Code Course Number - Section'
        title_parts = title.split(' - ')
        if len(title_parts) >= 4:
            course_info['course_name'] = title_parts[0].strip()
            course_info['crn'] = title_parts[1].strip()
            # Split 'Subject Code Course Number' to get subject and course number if needed
            subject_course = title_parts[2].strip()
            sc_parts = subject_course.split(' ')
            if len(sc_parts) >= 2:
                course_info['subject'] = sc_parts[0].strip()
                course_info['course_number'] = sc_parts[1].strip()
            else:
                print(f"Unexpected subject and course number format: {subject_course}", flush=True)
            course_info['section'] = title_parts[3].strip()
        else:
            print(f"Unexpected title format for {subject} {course_number}: {title}", flush=True)
            continue  # Skip this course if the format is unexpected

        details = section.find_next('td', class_='dddefault')
        if not details:
            print(f"No details found for {subject} {course_number} in term {term}.", flush=True)
            continue  # No details found

        # Extract detailed text
        detail_text = details.get_text('\n').strip()
        lines = [line.strip() for line in detail_text.split('\n') if line.strip()]

        # Extract units (Credits)
        units_regex = re.compile(r'^(\d+\.\d+)\s*Credits$')
        for line in lines:
            units_match = units_regex.match(line)
            if units_match:
                course_info['units'] = units_match.group(1)
                break

        # Extract instructional method
        method_regex = re.compile(r'^(.*)\s+Instructional Method$')
        for line in lines:
            method_match = method_regex.match(line)
            if method_match:
                course_info['instructional_method'] = method_match.group(1)
                break

        # Extract additional information
        try:
            associated_term_index = lines.index('Associated Term:')
            potential_add_info = lines[:associated_term_index]
            # Remove the course name from potential additional information
            potential_add_info = [line for line in potential_add_info if line != course_info['course_name']]
            if potential_add_info:
                course_info['additional_information'] = ' '.join(potential_add_info)
        except ValueError:
            # 'Associated Term:' not found
            pass

        # Extract schedule details
        table = details.find('table', class_='datadisplaytable')
        if table:
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 7:
                    course_info['frequency'] = cols[0].get_text(strip=True)
                    course_info['time'] = cols[1].get_text(strip=True)
                    course_info['days'] = cols[2].get_text(strip=True)
                    course_info['location'] = cols[3].get_text(strip=True)
                    course_info['date_range'] = cols[4].get_text(strip=True)
                    course_info['schedule_type'] = cols[5].get_text(strip=True)
                    course_info['instructor'] = cols[6].get_text(strip=True)
                    break  # Assuming one schedule per course
        
        courses.append(course_info)
    
    return courses

def save_to_csv(courses, filename):
    fieldnames = [
        'term', 'subject', 'course_name', 'course_number', 'crn', 'section',
        'frequency', 'time', 'days', 'location', 'date_range', 'schedule_type',
        'instructor', 'instructional_method', 'units', 'additional_information'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for course in courses:
            writer.writerow(course)
    print(f"Data has been saved to {filename}.", flush=True)

async def main():
    start_time = time.time()
    print("Script started.", flush=True)
    terms = ['202409', '202501']  # Update terms as needed
    all_courses = []
    
    # Read the courses-list.csv file
    with open('courses-list.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        courses_list = list(reader)
    
    sem = asyncio.Semaphore(CONCURRENT_REQUESTS)
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for term in terms:
            print(f"Processing term {term}...", flush=True)
            for course in courses_list:
                subject = course['Subject']
                course_number = course['Course Number']
                tasks.append(
                    fetch_and_parse_course(session, sem, term, subject, course_number)
                )
        
        # Process tasks concurrently with progress indication
        total_tasks = len(tasks)
        completed_tasks = 0

        for future in asyncio.as_completed(tasks):
            courses = await future
            completed_tasks += 1
            print(f"Completed {completed_tasks}/{total_tasks} tasks.", flush=True)
            if courses:
                all_courses.extend(courses)
    
    # Save all the scraped data to a new CSV file
    save_to_csv(all_courses, 'scraped_course_data.csv')
    end_time = time.time()
    total_time = end_time - start_time
    hours, rem = divmod(total_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Script execution time: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds), flush=True)
    print("Script finished.", flush=True)

async def fetch_and_parse_course(session, sem, term, subject, course_number):
    html_content = await fetch_course_data(session, sem, term, subject, course_number)
    if html_content:
        courses = parse_html(html_content, term, subject, course_number)
        return courses
    else:
        return []

if __name__ == "__main__":
    asyncio.run(main())