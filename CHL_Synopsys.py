import csv
import datetime
import os
import sys
import time
import shutil
import datetime
from collections import Counter

#File's name
LOG_FILE = "command_history.csv"

# Backup
LOG_FILE = 'command_log.csv'
BACKUP_FOLDER = 'backups'     
MAX_LOG_SIZE = 1 * 1024 * 1024 

def ensure_backup_folder():
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

def backup_log_if_needed():
    ensure_backup_folder()
    if os.path.exists(LOG_FILE):
        size = os.path.getsize(LOG_FILE)
        if size >= MAX_LOG_SIZE:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{BACKUP_FOLDER}/command_log_backup_{timestamp}.csv"
            shutil.copy2(LOG_FILE, backup_name)
            print(f"Backup created: {backup_name}\n")

#Columns 
CSV_HEADERS = ["timestamp", "command", "category"]

#Initialization
def initialize_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS)

#Writting
def log_command(command: str, category: str = "general"):
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, command, category])

#Reading
def read_log():
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

#History
def interactive_history(n=10):
    log = read_log()
    recent = log[-n:]
    if not recent:
        print("History is empty.\n")
        return

    print(f"\nLast {len(recent)} commands:")
    for i, row in enumerate(recent, start=1):
        print(f"{i}. [{row['timestamp']}] ({row['category']}) {row['command']}")

    print("\nEnter command number to re-run or press Enter to cancel.")
    choice = input("Choice: ").strip()

    if not choice:
        print("Cancelled.\n")
        return

    if not choice.isdigit() or not (1 <= int(choice) <= len(recent)):
        print("Invalid choice.\n")
        return

    cmd_to_run = recent[int(choice) - 1]['command']
    print(f"Re-running command: {cmd_to_run}\n")
    log_command(cmd_to_run)

#Clearing
def clear_log():
    confirm = input("Are you sure you want to clear the log? (yes/no): ")
    if confirm.lower() == "yes":
        with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS)
        print("Log cleared successfully.\n")
    else:
        print("Clear log canceled.\n")

# Deleting last log
def undo_last_command():
    if not os.path.exists(LOG_FILE):
        print("Log file does not exist.\n")
        return

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) <= 1:
        print("No commands to undo.\n")
        return
    last_command = lines[-1].strip()
    lines = lines[:-1]

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"Last command undone: {last_command}\n")

#Showing
def show_help():
    print("""
Available commands:
  help               - Show this help message
  history [N]        - Show last N commands (default 10)
  clearlog           - Clear the log file
  stats              - Show command usage statistics
  tag <tag> <cmd>    - Run cmd with category 
  exit               - Exit the logger
Examples:
  tag deploy git push origin main
  history 5
""")

# Statistics
def show_stats():
    log = read_log()
    commands = [row['command'] for row in log]
    categories = [row['category'] for row in log]

    command_count = Counter(commands)
    category_count = Counter(categories)

    print("\nTop 5 most used commands:")
    for cmd, count in command_count.most_common(5):
        print(f"  {cmd}: {count} times")

    print("\nCommand categories:")
    for cat, count in category_count.items():
        print(f"  {cat}: {count} commands")
    print()

# Handeling
def handle_input(user_input):
    parts = user_input.strip().split()

    if user_input.startswith('!'):
        secret_command = user_input[1:].strip()
        if secret_command == "":
            print("Empty secret command ignored.\n")
            return
        print(f"Secret command received: {secret_command}\n")
        return    

    if not parts:
        return

    cmd = parts[0].lower()

    if cmd == "help":
        show_help()
    elif cmd == "clearlog":
        clear_log()
    elif cmd == "history":
        if len(parts) > 1 and parts[1].isdigit():
            interactive_history(int(parts[1]))
        else:
            interactive_history()
    elif cmd == "stats":
        show_stats()
    elif cmd == "tag":
        if len(parts) >= 3:
            category = parts[1]
            command = ' '.join(parts[2:])
            log_command(command, category)
            print(f"Command logged with category '{category}'\n")
        else:
            print("Usage: tag <category> <command>\n")
    elif cmd == "exit":
        print("Exiting Command History Logger.")
        sys.exit(0)
    
    elif cmd == "search":
        if len(parts) >= 2:
            keyword = ' '.join(parts[1:])
            search_commands(keyword)
        else:
            print("Usage: search <keyword>\n")

    elif cmd == "filter":
        if len(parts) >= 3:
            filter_type = parts[1].lower()
            filter_value = ' '.join(parts[2:])
            if filter_type == "category":
                filter_by_category(filter_value)
            elif filter_type == "date":
                filter_by_date(filter_value)
            else:
                print("Usage: filter category <tag> OR filter date <yyyy-mm-dd>\n")
        else:
            print("Usage: filter category <tag> OR filter date <yyyy-mm-dd>\n")
    elif cmd == "stats" and len(parts) > 1 and parts[1].lower() == "day":
        show_stats_day()

    elif cmd == "undo":
        undo_last_command()

    else:
        log_command(user_input)
        print("Command logged.\n")

def print_banner():
    print("=" * 50)
    print("      📝 Command History Logger")
    print(" Type 'help' for a list of commands")
    print(" Press Ctrl+C or type 'exit' to quit")
    print("=" * 50)

# Showing Stats by days
def show_stats_day():
    log = read_log()
    date_counts = Counter()

    for row in log:
        date_str = row['timestamp'].split(' ')[0]
        date_counts[date_str] += 1

    if not date_counts:
        print("No command history available.\n")
        return

    print("\nCommands entered per day:")
    for date, count in sorted(date_counts.items()):
        print(f"  {date}: {count} commands")
    print()

# Searching
def search_commands(keyword: str):
    log = read_log()
    results = [row for row in log if keyword.lower() in row['command'].lower()]
    if results:
        print(f"\nCommands containing '{keyword}':")
        for row in results:
            print(f"[{row['timestamp']}] ({row['category']}) {row['command']}")
        print()
    else:
        print(f"No commands found containing '{keyword}'.\n")

#Filtering
def filter_by_category(category: str):
    log = read_log()
    results = [row for row in log if row['category'].lower() == category.lower()]
    if results:
        print(f"\nCommands in category '{category}':")
        for row in results:
            print(f"[{row['timestamp']}] {row['command']}")
        print()
    else:
        print(f"No commands found in category '{category}'.\n")

def filter_by_date(date_str: str):
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("Date format should be YYYY-MM-DD.\n")
        return

    log = read_log()
    results = [row for row in log if row['timestamp'].startswith(date_str)]
    if results:
        print(f"\nCommands on date '{date_str}':")
        for row in results:
            print(f"[{row['timestamp']}] ({row['category']}) {row['command']}")
        print()
    else:
        print(f"No commands found on date '{date_str}'.\n")

def main():
    initialize_log()
    print_banner()

    while True:
        try:
            user_input = input("> ").strip()
            if user_input == "":
                continue
            handle_input(user_input)

        except KeyboardInterrupt:
            print("\nInterrupted by user. Exiting.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            log_command(f"[ERROR] {e}", category="error")

if __name__ == "__main__":
    main()
    backup_log_if_needed()

    while True:
        user_input = input("> ")
        handle_input(user_input)
