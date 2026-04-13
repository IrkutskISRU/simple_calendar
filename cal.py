#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# File used to store events
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "calendar_events.json"

# ANSI colors used for output styling
COLORS = {
    'gray': '\033[38;5;240m',
    'yellow': '\033[1;33m',
    'green': '\033[1;32m',
    'white': '\033[1;37m',
    'reset': '\033[0m',
    'red': '\033[1;31m',
}

def generate_recurring_dates(start_dt, recurrence_type, end_dt):
    """Generate recurrence dates in the given range, including past dates."""
    dates = []
    current = start_dt

    # Generate all recurrences in range (including past dates)
    while current <= end_dt:
        if recurrence_type == 'daily':
            dates.append(current)
            current += timedelta(days=1)
        elif recurrence_type == 'weekdays':
            if current.weekday() < 5:  # Monday-Friday
                dates.append(current)
            current += timedelta(days=1)
        elif recurrence_type == 'weekly':
            dates.append(current)
            current += timedelta(weeks=1)
        elif recurrence_type == 'yearly':
            dates.append(current)
            try:
                current = current.replace(year=current.year + 1)
            except ValueError:
                # Handle February 29
                current += timedelta(days=365)
        else:
            break

    return dates



def section(title):
    """Print a styled section title with lines on both sides."""
    total_width = 40
    inner = f" {title} "
    side_len = (total_width - len(inner)) // 2
    if side_len < 0:
        side_len = 0

    line = '─' * side_len

    # Gray side lines + colored title
    print(f"{COLORS['gray']}{line} {COLORS['yellow']}{title}{COLORS['gray']} {line}{COLORS['reset']}")

def load_events():
    """Load events from file or return an empty list."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_events(events):
    """Save events to file."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def add_event(date_time_str, description, recurrence_type=None):
    """Add a new event, optionally recurring."""
    try:
        event_datetime = datetime.strptime(date_time_str, "%d.%m %H:%M")
        now = datetime.now()
        current_year = now.year

        # Set current year
        event_datetime = event_datetime.replace(year=current_year)

        events = load_events()
        next_id = max([e['id'] for e in events], default=0) + 1

        new_event = {
            'id': next_id,
            'datetime': event_datetime.isoformat(),
            'description': description,
            'recurrence': recurrence_type
        }
        events.append(new_event)
        save_events(events)
        print(f"Event added with ID: {next_id}")
        if recurrence_type:
            print(f"Recurrence type: {recurrence_type}")
    except ValueError as e:
        print("Invalid date format. Use: DD.MM HH:MM")




def delete_event(event_id):
    """Delete an event by ID."""
    events = load_events()
    original_count = len(events)
    events = [e for e in events if e['id'] != event_id]

    if len(events) == original_count:
        print(f"Event with ID {event_id} not found.")
    else:
        save_events(events)
        print(f"Event {event_id} deleted.")

def show_events():
    os.system('clear')
    print()
    
    now = datetime.now()
    end_period = now + timedelta(hours=48)  # Next 48 hours
    grace_period = now - timedelta(hours=5)  # "Recently past" period: 5 hours back

    events = load_events()
    display_events = []

    for event in events:
        try:
            event_dt = datetime.fromisoformat(event['datetime'])
            recurrence = event.get('recurrence')

            if recurrence:
                # Generate all recurrences in range
                recurring_dates = generate_recurring_dates(
                    event_dt, recurrence, end_period
                )
                for date in recurring_dates:
                    if grace_period <= date <= end_period:  # Include "recently past" period
                        display_events.append({
                    'datetime': date,
            'description': event['description'],
            'id': event['id'],
            'is_recurring': True,
            'is_recently_past': date < now
        })
            else:
                # For one-time events, check the range
                if grace_period <= event_dt <= end_period:
                    display_events.append({
                'datetime': event_dt,
                'description': event['description'],
                'id': event['id'],
                'is_recurring': False,
                'is_recently_past': event_dt < now
            })

        except (KeyError, ValueError) as e:
            print(f"Error processing event {event.get('id', 'unknown ID')}: {e}")
            continue

    # Sort all events by time
    display_events.sort(key=lambda x: x['datetime'])

    has_events = False
    recently_past_events = []  # Events that happened <=5 hours ago
    today_events = []          # Events for today
    tomorrow_events = []       # Events for tomorrow

    for ev in display_events:
        ev_date = ev['datetime'].date()
        if ev['is_recently_past']:
            recently_past_events.append(ev)
        elif ev_date == now.date():
            today_events.append(ev)
        elif ev_date == (now + timedelta(days=1)).date():
            tomorrow_events.append(ev)

    # Print recently missed events
    if recently_past_events:
        has_events = True
        section("RECENTLY PASSED (<=5h)")
        for event in recently_past_events:
            time_str = event['datetime'].strftime("%H:%M")
            marker = "🔁" if event['is_recurring'] else "•"
            print(f"{COLORS['red']}{time_str} {marker}{COLORS['reset']}")
            print(f"{COLORS['white']}{event['description']}{COLORS['reset']}{COLORS['gray']} (ID: {event['id']}){COLORS['reset']}")
            print()  # Empty line between events

    # Print today's events
    if today_events:
        has_events = True
        section("TODAY")
        for event in today_events:
            time_str = event['datetime'].strftime("%H:%M")
            marker = "🔁" if event['is_recurring'] else "•"
            print(f"{time_str} {marker}")
            print(f"{COLORS['white']}{event['description']}{COLORS['reset']}{COLORS['gray']} (ID: {event['id']}){COLORS['reset']}")
            print()

    # Print tomorrow's events
    if tomorrow_events:
        has_events = True
        section("TOMORROW")
        for event in tomorrow_events:
            time_str = event['datetime'].strftime("%H:%M")
            marker = "🔁" if event['is_recurring'] else "•"
            print(f"{time_str} {marker}")
            print(f"{COLORS['white']}{event['description']}{COLORS['reset']}{COLORS['gray']} (ID: {event['id']}){COLORS['reset']}")
            print()

    if not has_events:
        print(f"{COLORS['gray']}No events in the next 48 hours or recently passed.{COLORS['reset']}")

def show_all_events(days_limit=14):
    os.system('clear')
    print()

    now = datetime.now()
    end_period = now + timedelta(days=days_limit)  # Next N days for recurring events

    events = load_events()
    display_events = []

    for event in events:
        try:
            event_dt = datetime.fromisoformat(event['datetime'])
            recurrence = event.get('recurrence')

            if recurrence in ['daily', 'weekdays', 'weekly']:
                # For daily and weekly, only upcoming N days
                recurring_dates = generate_recurring_dates(
                    event_dt, recurrence, end_period
                )
                for date in recurring_dates:
                    if date >= now:  # Future events only
                        display_events.append({
                            'datetime': date,
                            'description': event['description'],
                            'id': event['id'],
                            'is_recurring': True,
                            'recurrence_type': recurrence
                })
            else:
                # For yearly and one-time events, include all future events
                if event_dt >= now:
                    display_events.append({
                        'datetime': event_dt,
                        'description': event['description'],
                        'id': event['id'],
                        'is_recurring': False,
                        'recurrence_type': None
                    })

        except (KeyError, ValueError) as e:
            print(f"Error processing event {event.get('id', 'unknown ID')}: {e}")
            continue

    # Sort all events by time
    display_events.sort(key=lambda x: x['datetime'])

    if not display_events:
        print(f"{COLORS['gray']}No events in the calendar.{COLORS['reset']}")
        return

    section("ALL EVENTS")

    current_year = None
    for ev in display_events:
        ev_year = ev['datetime'].year

        # Print year heading when it changes
        if ev_year != current_year:
            current_year = ev_year
            print(f"\n{COLORS['yellow']}{ev_year} YEAR{COLORS['reset']}")
            print()

        date_str = ev['datetime'].strftime("%d.%m %H:%M")
        marker = "🔁" if ev['is_recurring'] else "•"
        recurrence_info = f" ({ev['recurrence_type']})" if ev['is_recurring'] else ""

        print(f"{COLORS['green']}{date_str}{COLORS['reset']} {marker}{recurrence_info}")
        print(f"{COLORS['white']}{ev['description']}{COLORS['reset']}{COLORS['gray']} (ID: {ev['id']}){COLORS['reset']}")
        print()  # Empty line between events


def main():
    parser = argparse.ArgumentParser(description="Event calendar")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # add command
    add_parser = subparsers.add_parser('add', help='Add an event')
    add_parser.add_argument('datetime', help='Date and time (format: DD.MM HH:MM)')
    add_parser.add_argument('description', nargs='+', help='Event description')
    add_parser.add_argument('--daily', action='store_const', const='daily', dest='recurrence', help='Daily recurrence')
    add_parser.add_argument('--weekdays', action='store_const', const='weekdays', dest='recurrence', help='Weekdays-only recurrence (Mon-Fri)')
    add_parser.add_argument('--weekly', action='store_const', const='weekly', dest='recurrence', help='Weekly recurrence')
    add_parser.add_argument('--yearly', action='store_const', const='yearly', dest='recurrence', help='Yearly recurrence')

    # Other commands
    del_parser = subparsers.add_parser('del', help='Delete an event')
    del_parser.add_argument('id', type=int, help='Event ID')

    all_parser = subparsers.add_parser('all', help='Show all events')
    all_parser.add_argument(
        '--days',
        type=int,
        default=14,
        help='Number of days to show recurring events (default: 14)'
    )


    subparsers.add_parser('show', help='Show events for 48 hours')

    args = parser.parse_args()

    if args.command == 'add':
        description = ' '.join(args.description)
        add_event(args.datetime, description, args.recurrence)
    elif args.command == 'del':
        delete_event(args.id)
    elif args.command == 'show':
        show_events()
    elif args.command == 'all':
        show_all_events(args.days)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

