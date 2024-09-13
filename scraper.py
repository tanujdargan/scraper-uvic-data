import time
import csv
import requests
from bs4 import BeautifulSoup
import random
import re
import msvcrt  # Import msvcrt for keyboard detection on Windows

start_time = time.time()  # Record the start time

def fetch_course_data(term, subject, course_number):
    url = f"https://www.uvic.ca/BAN1P/bwckctlg.p_disp_listcrse?term_in={term}&subj_in={subject}&crse_in={course_number}&schd_in="
    response = requests.get(url)
    return response.text

def parse_html(html_content, term, subject, course_number):
    soup = BeautifulSoup(html_content, 'html.parser')
    sections = soup.find_all('th', class_='ddtitle')
    
    courses = []
    for section in sections:
        course_info = {
            'term': term,
            'subject': subject,
            'course_name': '',
            'course_number': course_number,
            'crn': '',
            'section': '',
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
        
        # Extract course name, CRN, and section
        title = section.find('a').text.strip()
        title_parts = title.split(' - ')
        if len(title_parts) >= 3:
            course_info['course_name'] = title_parts[0].strip()
            course_info['crn'] = title_parts[1].strip()
            course_info['section'] = title_parts[2].strip()
        else:
            print(f"Unexpected title format: {title}")
            continue  # Skip this course if the format is unexpected

        details = section.find_next('td', class_='dddefault')
        if not details:
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
    fieldnames = ['term', 'subject', 'course_name', 'course_number', 'crn', 'section', 'frequency', 'time', 'days', 'location', 'date_range', 'schedule_type', 'instructor', 'instructional_method', 'units', 'additional_information']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for course in courses:
            writer.writerow(course)

def main():
    terms = ['202409', '202501']
    all_courses = []

    # Read the courses-list.csv file
    with open('courses-list.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        courses_list = list(reader)

    stop_scraping = False  # Flag to control when to stop scraping

    for term in terms:
        if stop_scraping:
            break
        for course in courses_list:
            subject = course['Subject']
            course_number = course['Course Number']

            print(f"Fetching data for {subject} {course_number} in term {term}")

            html_content = fetch_course_data(term, subject, course_number)
            courses = parse_html(html_content, term, subject, course_number)
            all_courses.extend(courses)

            # Add a small delay to avoid overloading the server
            time.sleep(random.uniform(1, 3))

            # Check if 'q' has been pressed
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key.lower() == b'q':
                    print("Stopping scraping as per user request.")
                    stop_scraping = True
                    break  # Exit the inner loop

        if stop_scraping:
            break

    # Save all the scraped data to a new CSV file
    save_to_csv(all_courses, 'scraped_course_data.csv')
    print("Data has been scraped and saved to scraped_course_data.csv")

if __name__ == "__main__":
    main()
    end_time = time.time()  # Record the end time
    total_time = end_time - start_time  # Calculate the total execution time in seconds

    # Convert the time to hours, minutes, seconds
    hours, rem = divmod(total_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Script execution time: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))