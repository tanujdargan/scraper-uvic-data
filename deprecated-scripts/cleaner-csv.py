import pandas as pd

# Read the CSV file
df = pd.read_csv('./cleaned_courses.csv')
# Initialize a list to store cleaned data
cleaned_data = []

# Iterate over the DataFrame rows
for i in range(0, len(df), 2):
    # Merge the two rows into one
    row1 = df.iloc[i]
    row2 = df.iloc[i + 1]

    # Create a new row by combining information from both rows
    combined_row = {
        'term': row1['term'],
        'subject': row1['subject'],
        'course_number': row1['course_number'],
        'frequency': row2['frequency'],
        'time': row2['time'],
        'days': row2['days'],
        'location': row2['location'],
        'date_range': row2['date_range'],
        'schedule_type': row2['schedule_type'],
        'instructor': row2['instructor']
    }

    # Append the combined row to the cleaned data list
    cleaned_data.append(combined_row)
# Create a new DataFrame from the cleaned data
cleaned_df = pd.DataFrame(cleaned_data)
# Write the cleaned DataFrame to a new CSV file
cleaned_df.to_csv('cleaned_file.csv', index=False)
