import re
import pandas as pd
def preprocessor(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
    messages = re.split(pattern, data)[1:]  # to remove empty string
    dates = re.findall(pattern, data)

    def convert_to_two_digit_year(date_string):
        parts = date_string.split(',')[0].split('/')
        year = parts[2]

        # Convert year to 2 digits
        if len(year) == 4:
            year = year[-2:]  # Get the last 2 digits of the year
            date_string = date_string.replace(parts[2], year)  # Replace year in the date string
        return date_string

    # Apply the year conversion
    dates = [convert_to_two_digit_year(date) for date in dates]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M - ', errors='coerce')

    # If any NaT values exist, try to parse again with 4-digit year format
    df['message_date'] = df['message_date'].fillna(
        pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M - ', errors='coerce'))

    # Check if there are any NaT values left after conversion
    if df['message_date'].isna().sum() > 0:
        print(f"Rows with invalid datetime: {df[df['message_date'].isna()]}")
    df.rename(columns={'message_date': 'date'}, inplace=True)


    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'^(.*?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df