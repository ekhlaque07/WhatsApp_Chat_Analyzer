import re
import pandas as pd

def preprocess(data):

    # Detect multiple WhatsApp formats
    patterns = {
        "android_12hr": r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?[APMapm]{2}\s-\s',
        "android_24hr": r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s',
        "iphone": r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s?[APMapm]{2}\]\s'
    }

    selected_pattern = None

    for name, pattern in patterns.items():
        if re.search(pattern, data):
            selected_pattern = pattern
            break

    if not selected_pattern:
        raise ValueError("Unsupported WhatsApp chat format")

    messages = re.split(selected_pattern, data)[1:]
    dates = re.findall(selected_pattern, data)

    # Clean brackets and hyphen if iPhone
    dates = [d.replace('[','').replace(']','').replace(' -','') for d in dates]

    df = pd.DataFrame({
        "user_message": messages,
        "date": dates
    })

    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)

    users = []
    messages_clean = []

    for message in df["user_message"]:
        entry = re.split(r'([^:]+):\s', message)
        if len(entry) > 2:
            users.append(entry[1].strip())
            messages_clean.append(entry[2].strip())
        else:
            users.append("group_notification")
            messages_clean.append(entry[0].strip())

    df["user"] = users
    df["message"] = messages_clean
    df.drop(columns=["user_message"], inplace=True)

    # Date features
    df["only_date"] = df["date"].dt.date
    df["year"] = df["date"].dt.year
    df["month_num"] = df["date"].dt.month
    df["month"] = df["date"].dt.month_name()
    df["day"] = df["date"].dt.day
    df["day_name"] = df["date"].dt.day_name()
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute

    return df
