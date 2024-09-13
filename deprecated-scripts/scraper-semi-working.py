import csv
import requests
from bs4 import BeautifulSoup
import time
import random

def fetch_course_data(term, subject, course_number):
    url = f"https://www.uvic.ca/BAN1P/bwckctlg.p_disp_listcrse?term_in={term}&subj_in={subject}&crse_in={course_number}&schd_in="
    response = requests.get(url)
    return response.text

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    sections = soup.find_all('th', class_='ddtitle')
    
    courses = []
    for section in sections:
        course_info = {
            'term': '',
            'subject': '',
            'course_name': '',
            'course_number': '',
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
        
        # Extract CRN and section
        title = section.find('a').text
        course_info['subject'], course_info['course_number'], course_info['section'] = title.split(' - ')[1:]
        course_info['crn'] = title.split(' - ')[0]
        
        details = section.find_next('td', class_='dddefault')
        
        # Extract term
        term_text = details.find('span', string='Associated Term:')
        if term_text:
            course_info['term'] = term_text.next_sibling.strip()
        
        # Extract course name
        course_name = details.find('b')
        if course_name:
            course_info['course_name'] = course_name.text.strip()
        
        # Extract units
        units_text = details.find(string=lambda text: 'Credits' in text if text else False)
        if units_text:
            course_info['units'] = units_text.strip().split()[0]
        
        # Extract additional information
        add_info = details.find('span', class_='fieldlabeltext', string='Additional Information:')
        if add_info:
            course_info['additional_information'] = add_info.next_sibling.strip()
        
        # Extract instructional method
        method_text = details.find(string=lambda text: 'Instructional Method:' in text if text else False)
        if method_text:
            course_info['instructional_method'] = method_text.split(':')[1].strip()
        
        # Extract other information from the table
        table = details.find('table', class_='datadisplaytable')
        if table:
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 7:
                    course_info['frequency'] = cols[0].text.strip()
                    course_info['time'] = cols[1].text.strip()
                    course_info['days'] = cols[2].text.strip()
                    course_info['location'] = cols[3].text.strip()
                    course_info['date_range'] = cols[4].text.strip()
                    course_info['schedule_type'] = cols[5].text.strip()
                    course_info['instructor'] = cols[6].text.strip()
        
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
    with open('courses-list-test.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        courses_list = list(reader)

    for term in terms:
        for course in courses_list:
            subject = course['Subject']
            course_number = course['Course Number']
            
            print(f"Fetching data for {subject} {course_number} in term {term}")
            
            html_content = fetch_course_data(term, subject, course_number)
            courses = parse_html(html_content)
            all_courses.extend(courses)
            
            # Add a small delay to avoid overloading the server
            time.sleep(random.uniform(1, 3))

    # Save all the scraped data to a new CSV file
    save_to_csv(all_courses, 'scraped_course_data.csv')
    print("Data has been scraped and saved to scraped_course_data.csv")

if __name__ == "__main__":
    main()
