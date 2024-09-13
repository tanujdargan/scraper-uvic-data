# scraper-uvic-data

# Course Data Scraper

A Python script to scrape course information from the University of Victoria's Class Schedule Listing - BAN1P. The script fetches and parses course data, including details like term, subject, course name, course number, CRN, section, schedule, instructor, instructional method, units, and additional information. It is designed to help students and developers access and utilize course information programmatically.

**Note:** This script currently uses the Class Schedule Listing - BAN1P and will soon incorporate class information such as capacity and waitlist information using Detailed Class Information.

## Table of Contents

- [Installation / Setup](#installation--setup)
- [Usage](#usage)
- [Development](#development)
- [Contributing](#contributing)

## Installation / Setup

### Prerequisites

#### Note: This script was developed and tested on Python 3.12.2 compatibility is not guaranteed on other versions. ALthough there should be no issues with future or older versions of python.

- **Python 3.x** installed on your system.
- Required Python packages:
  - `requests`
  - `beautifulsoup4`

You can install the required packages using pip:

```bash
pip install requests beautifulsoup4
```

### Clone the Repository

Clone this repository to your local machine using:

```bash
git clone https://github.com/yourusername/scraper-uvic-data.git
```

### Prepare the Input File

A CSV file named `./courses-list.csv` and `./data/course-list-test.csv` are used to generate the urls and scrape the data respectively:

```csv
UVIC Course Description, Subject, Course Number, Course Name
```

Use the test file for development otherwise leave it as is.

## Usage

Navigate to the directory containing the script and run the script using Python:

```bash
python scraper.py
```

### Running the Script

- The script will iterate through the terms and courses specified in the `courses-list.csv` file.
- It will fetch and parse course data, then save the results to `scraped_course_data.csv`.
- The script includes functionality to stop the scraping process at any time by pressing the `q` key.
- At the end of the execution, the script will display the total execution time.

### Output

The output will be saved in a CSV file named `scraped_course_data.csv`, containing the following columns:

- `term`
- `subject`
- `course_name`
- `course_number`
- `crn`
- `section`
- `frequency`
- `time`
- `days`
- `location`
- `date_range`
- `schedule_type`
- `instructor`
- `instructional_method`
- `units`
- `additional_information`

## Development

This script is open for development and improvement. Feel free to fork the repository, make changes, and contribute back.

### Future Enhancements

- Incorporate class information such as capacity and waitlist details using Detailed Class Information.
- Optimize performance and efficiency.

### Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally.
3. **Create a branch** for your feature or fix

---

**Disclaimer:** This script is intended for educational and personal use. Please ensure compliance with the University of Victoria's policies and guidelines when accessing and using their data.

**Contact:** If you have any questions or suggestions, feel free to reach out over email or open an issue on GitHub.

# Questions or Feedback

If you encounter any issues or have suggestions for improvement, please open an issue in this repository or contact me.

# Planned Features
- Adding seat capacity and waitlist data
- Creating an api that checks for updates regularly and updates the MongoDB database respectively
