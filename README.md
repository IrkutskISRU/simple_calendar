# Simple Calendar CLI

A lightweight command-line calendar for storing and viewing personal events.

The app supports:
- One-time events
- Recurring events (`daily`, `weekly`, `yearly`)
- Quick 48-hour agenda view
- Full upcoming events view
- Local JSON storage (`calendar_events.json`)

## Requirements

- Python 3.8+

## Run

```bash
python3 cal.py <command> [options]
```

## Commands

### Add event

```bash
python3 cal.py add "DD.MM HH:MM" Event description...
```

Examples:

```bash
python3 cal.py add "09.04 14:30" Team sync
python3 cal.py add "10.04 08:00" Morning workout --daily
python3 cal.py add "12.04 19:00" Weekly planning --weekly
python3 cal.py add "25.12 10:00" Christmas brunch --yearly
```

Recurrence flags:
- `--daily`
- `--weekly`
- `--yearly`

### Show near-term events (48h + recently passed)

```bash
python3 cal.py show
```

### Show all upcoming events

```bash
python3 cal.py all
```

You can limit the recurrence horizon (default is 14 days):

```bash
python3 cal.py all --days 30
```

### Delete event

```bash
python3 cal.py del <event_id>
```

Example:

```bash
python3 cal.py del 3
```

## Data storage

Events are stored in `calendar_events.json` in the project root directory.

Each event includes:
- `id`
- `datetime` (ISO format)
- `description`
- `recurrence` (`daily`, `weekly`, `yearly`, or `null`)
