import pandas as pd
import re


def preprocess(data):
    # Adjust regex pattern to match WhatsApp timestamps, which might be in the format: [dd/mm/yy, hh:mm:ss AM/PM]
    pattern = r"\[\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}:\d{2}\s?(?:AM|PM)\]"

    # Split data into messages and dates
    messages = re.split(pattern, data)[1:]  # Messages are split by the regex, ignoring the first empty element
    dates = re.findall(pattern, data)  # Find all the dates that match the pattern

    # Create a DataFrame with 'user_message' and 'message_date'
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert 'message_date' to datetime format, catching any errors in conversion
    try:
        df['message_date'] = pd.to_datetime(df['message_date'], format='[%d/%m/%y, %I:%M:%S %p]', dayfirst=True)
    except ValueError as e:
        print("Error while converting date:", e)
        print(df['message_date'])  # To debug offending date strings

    # Rename the 'message_date' column to 'date'
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Initialize lists for users and messages
    users = []
    messages = []

    # Loop through each message in the 'user_message' column
    for message in df['user_message']:
        # Split by the first occurrence of a username pattern: "<username>: <message>"
        entry = re.split(r'([^\s]+):\s', message, maxsplit=1)  # Adjust regex to capture usernames correctly
        if len(entry) > 2:  # Means we have a user and a message
            users.append(entry[1])  # Username
            messages.append(entry[2])  # Message
        else:
            users.append('group_notification')  # Default for group notifications
            messages.append(entry[0])  # Use the entire message

    # Add 'user' and 'message' columns to the DataFrame
    df['user'] = users
    df['message'] = messages

    # Drop the original 'user_message' column
    df.drop(columns=['user_message'], inplace=True)

    # The 'date' column is already in datetime format, so no need to parse 'timestamp' again
    df['year'] = df['date'].dt.year
    df['day'] = df['date'].dt.day  # Extract day
    df['month'] = df['date'].dt.month_name()  # Get the month name
    df['hour'] = df['date'].dt.hour  # Extract hour
    df['minute'] = df['date'].dt.minute  # Extract minute

    return df
