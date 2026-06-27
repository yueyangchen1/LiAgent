import json
import re
from collections import defaultdict
from datetime import datetime

# run this file can get the issue or discussion start and close time and category of license discussion
time_ranges_start = defaultdict(lambda: defaultdict(int))
time_ranges_close = defaultdict(lambda: defaultdict(int))
tag_counts = defaultdict(int)


total_count = 0

def parse_time_string(time_str):
    if not isinstance(time_str, str):
        return 100000000000  # null 特殊值
    days = hours = minutes = seconds = 0
    match_days = re.search(r'(\d+) days?', time_str)
    match_hours = re.search(r'(\d+) hours?', time_str)
    match_minutes = re.search(r'(\d+) minutes?', time_str)
    match_seconds = re.search(r'(\d+) seconds?', time_str)

    if match_days:
        days = int(match_days.group(1))
    if match_hours:
        hours = int(match_hours.group(1))
    if match_minutes:
        minutes = int(match_minutes.group(1))
    if match_seconds:
        seconds = int(match_seconds.group(1))

    total_days = days + hours // 24 + minutes // 1440 + seconds // 86400
    return total_days

def categorize_time(days):
    if days < 1:
        return '0-1 day'
    elif days < 7:
        return '1-7 days'
    elif days < 30:
        return '7-30 days'
    elif days < 60:
        return '30-60 days'
    elif days < 90:
        return '60-90 days'
    elif days < 180:
        return '90-180 days'
    elif days < 365:
        return '180-365 days'
    elif days == 100000000000:
        return 'null'
    else:
        return '365+ days'

def get_time_diff_str(start_time, end_time):
    if not start_time or not end_time:
        return None
    delta = end_time - start_time
    total_seconds = int(delta.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    parts = []
    if days > 0:
        parts.append(f"{days} days")
    if hours > 0:
        parts.append(f"{hours} hours")
    if minutes > 0:
        parts.append(f"{minutes} minutes")
    if seconds > 0:
        parts.append(f"{seconds} seconds")
    return " ".join(parts) if parts else "0 seconds"

with open('restructured_dataset_discussions_84.json', 'r', encoding='utf-8') as f:
    try:
        data = json.load(f)
        projects = data.get("models", [])
        print(f"Loaded {len(projects)} projects.")
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")
        exit(1)


for project in projects:
    project_created = datetime.strptime(project.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
    for issue in project.get("discussions", []):
        total_count += 1
        tag = issue.get("tag", "No Tag")
        tag_counts[tag] += 1

        issue_created = datetime.strptime(issue.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
        closed_at = issue.get("closed_at")
        issue_closed = datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ") if closed_at else None

        # 计算时间差
        time_since_project_start_str = get_time_diff_str(project_created, issue_created)
        time_to_close_str = get_time_diff_str(issue_created, issue_closed) if closed_at else None

        start_days = parse_time_string(time_since_project_start_str)
        close_days = parse_time_string(time_to_close_str)

        time_ranges_start[tag][categorize_time(start_days)] += 1
        time_ranges_close[tag][categorize_time(close_days)] += 1
        if tag != "no":
            time_ranges_start['Total'][categorize_time(start_days)] += 1
            time_ranges_close['Total'][categorize_time(close_days)] += 1

time_order = [
    "0-1 day", "1-7 days", "7-30 days", "30-60 days",
    "60-90 days", "90-180 days", "180-365 days", "365+ days", "null"
]

print("Tag Counts:")
for tag, count in tag_counts.items():
    print(f"{tag}: {count}")

for tag in tag_counts.keys():
    print(f"\nStatistics for Tag {tag}:")
    print("Time Since Project Start Distribution:")
    for time_range in time_order:
        count = time_ranges_start[tag].get(time_range, 0)
        print(f"{time_range}: {count}")
    print("\nTime To Close Distribution:")
    for time_range in time_order:
        count = time_ranges_close[tag].get(time_range, 0)
        print(f"{time_range}: {count}")

print("\nStatistics for All Issues:")
print("Time Since Project Start Distribution:")
for time_range in time_order:
    print(f"{time_range}: {time_ranges_start['Total'].get(time_range, 0)}")

print("\nTime To Close Distribution:")
for time_range in time_order:
    print(f"{time_range}: {time_ranges_close['Total'].get(time_range, 0)}")
