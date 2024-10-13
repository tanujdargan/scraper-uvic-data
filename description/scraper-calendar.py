import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Load your CSV file with course details
file_path = 'courses-list.csv'
courses_df = pd.read_csv(file_path)

# Verify the columns in your CSV file
print("Columns in CSV file:", courses_df.columns)

# Assuming your CSV has columns 'Subject' and 'Course Number'
if 'Subject' in courses_df.columns and 'Course Number' in courses_df.columns:
    # Remove any leading/trailing whitespace from Subject and Course Number
    courses_df['Subject'] = courses_df['Subject'].astype(str).str.strip().str.upper()
    courses_df['Course Number'] = courses_df['Course Number'].astype(str).str.strip().str.upper()

    # Combine Subject and Course Number to create Course Codes
    courses_df['Course Code'] = courses_df['Subject'] + ' ' + courses_df['Course Number']

    # Configure Selenium WebDriver
    options = Options()
    options.headless = False  # Set to False to see the browser actions for debugging
    driver = webdriver.Chrome(options=options)  # Ensure chromedriver is in your PATH

    # Function to scrape course details using Selenium
    def scrape_course_details(subject, course_number):
        course_code = f"{subject} {course_number}"
        print(f"Processing Course Code: {course_code}")

        # Open the main courses page
        driver.get("https://www.uvic.ca/calendar/undergrad/index.php#/courses")
        time.sleep(5)  # Wait for the page to load completely

        try:
            # Wait and click on the 'Accept all cookies' button if it appears
            try:
                accept_cookies_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept all cookies')]")
                accept_cookies_button.click()
                time.sleep(1)  # Wait for the modal to close
            except:
                pass  # If the button isn't found, continue

            # Scroll to the subject code
            subject_element = driver.find_element(By.XPATH, f"//div[@class='subject-code' and text()='{subject}']")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", subject_element)
            time.sleep(1)  # Wait for scrolling

            # Click on the subject to expand the list of courses
            subject_element.click()
            time.sleep(2)  # Wait for the courses to load

            # Scroll to the course
            course_element = driver.find_element(By.XPATH, f"//div[@class='course-code' and text()='{course_code}']")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", course_element)
            time.sleep(1)  # Wait for scrolling

            # Click on the course to view details
            course_element.click()
            time.sleep(3)  # Wait for the course details to load

            # Switch to the course details iframe
            # Note: The course details may be loaded in an iframe or modal. Adjust accordingly.

            # Extract the description
            try:
                description_element = driver.find_element(By.XPATH, "//div[@class='course-description']")
                description = description_element.text.strip()
            except:
                description = 'Description not available'

            # Extract the notes
            try:
                notes_element = driver.find_element(By.XPATH, "//div[@class='course-notes']")
                notes = notes_element.text.strip()
            except:
                notes = 'Notes not available'

            print(f"Extracted Description: {description}")
            print(f"Extracted Notes: {notes}")

            return {
                'Subject': subject,
                'Course Number': course_number,
                'Course Code': course_code,
                'Description': description,
                'Notes': notes
            }

        except Exception as e:
            print(f"Error processing course {course_code}: {e}")
            return {
                'Subject': subject,
                'Course Number': course_number,
                'Course Code': course_code,
                'Description': 'Error retrieving data',
                'Notes': 'Error retrieving data'
            }

    # List to store the scraped data
    scraped_data = []

    # Iterate over each course code in your DataFrame
    for index, row in courses_df.iterrows():
        subject = row['Subject']
        course_number = row['Course Number']
        course_data = scrape_course_details(subject, course_number)
        scraped_data.append(course_data)

    # Close the WebDriver
    driver.quit()

    # Convert scraped data to a DataFrame and save to CSV
    scraped_df = pd.DataFrame(scraped_data)
    scraped_df.to_csv('scraped_course_details.csv', index=False)

    print("Scraping complete. Data saved to 'scraped_course_details.csv'.")

else:
    print("Error: 'Subject' and/or 'Course Number' columns not found in CSV file.")
    print("Available columns:", courses_df.columns)
    # Handle the error or exit the script
    import sys
    sys.exit(1)