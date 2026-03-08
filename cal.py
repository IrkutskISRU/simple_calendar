#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Файл для хранения событий
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "calendar_events.json"

# Цвета ANSI для оформления
COLORS = {
    'gray': '\033[38;5;240m',
    'yellow': '\033[1;33m',
    'green': '\033[1;32m',
    'white': '\033[1;37m',
    'reset': '\033[0m',
    'red': '\033[1;31m',
}

def generate_recurring_dates(start_dt, recurrence_type, end_dt):
    """Генерирует даты повторения в заданном диапазоне, включая прошлое."""
    dates = []
    current = start_dt

    # Генерируем все повторения в диапазоне (включая прошлое)
    while current <= end_dt:
        dates.append(current)
        if recurrence_type == 'daily':
            current += timedelta(days=1)
        elif recurrence_type == 'weekly':
            current += timedelta(weeks=1)
        elif recurrence_type == 'yearly':
            try:
                current = current.replace(year=current.year + 1)
            except ValueError:
                # Обработка 29 февраля
                current += timedelta(days=365)

    return dates



def section(title):
    """Выводит стилизованный заголовок с линиями по бокам."""
    total_width = 40
    inner = f" {title} "
    side_len = (total_width - len(inner)) // 2
    if side_len < 0:
        side_len = 0

    line = '─' * side_len

    # Серые линии + цветной заголовок
    print(f"{COLORS['gray']}{line} {COLORS['yellow']}{title}{COLORS['gray']} {line}{COLORS['reset']}")

def load_events():
    """Загружает события из файла или создаёт пустой список."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_events(events):
    """Сохраняет события в файл."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def add_event(date_time_str, description, recurrence_type=None):
    """Добавляет новое событие с возможностью повторения."""
    try:
        event_datetime = datetime.strptime(date_time_str, "%d.%m %H:%M")
        now = datetime.now()
        current_year = now.year

        # Устанавливаем текущий год
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
        print(f"Событие добавлено с ID: {next_id}")
        if recurrence_type:
            print(f"Тип повторения: {recurrence_type}")
    except ValueError as e:
        print("Ошибка формата даты. Используйте формат: ДД.ММ ЧЧ:ММ")




def delete_event(event_id):
    """Удаляет событие по ID."""
    events = load_events()
    original_count = len(events)
    events = [e for e in events if e['id'] != event_id]

    if len(events) == original_count:
        print(f"Событие с ID {event_id} не найдено.")
    else:
        save_events(events)
        print(f"Событие {event_id} удалено.")

def show_events():
    os.system('clear')
    print()
    
    now = datetime.now()
    end_period = now + timedelta(hours=48)  # 48 часов вперёд
    grace_period = now - timedelta(hours=5)  # Период «недавнего прошлого» — 5 часов назад

    events = load_events()
    display_events = []

    for event in events:
        print(event)
        try:
            event_dt = datetime.fromisoformat(event['datetime'])
            recurrence = event.get('recurrence')

            if recurrence:
                # Генерируем все повторения в диапазоне
                recurring_dates = generate_recurring_dates(
                    event_dt, recurrence, end_period
                )
                for date in recurring_dates:
                    if grace_period <= date <= end_period:  # Учитываем период «недавнего прошлого»
                        display_events.append({
                    'datetime': date,
            'description': event['description'],
            'id': event['id'],
            'is_recurring': True,
            'is_recently_past': date < now
        })
            else:
                # Для одноразовых событий — проверяем диапазон
                if grace_period <= event_dt <= end_period:
                    display_events.append({
                'datetime': event_dt,
                'description': event['description'],
                'id': event['id'],
                'is_recurring': False,
                'is_recently_past': event_dt < now
            })

        except (KeyError, ValueError) as e:
            print(f"Ошибка обработки события {event.get('id', 'неизвестный ID')}: {e}")
            continue

    # Сортируем все события по времени
    display_events.sort(key=lambda x: x['datetime'])

    has_events = False
    recently_past_events = []  # События, которые прошли ≤5 часов назад
    today_events = []          # События на сегодня
    tomorrow_events = []       # События на завтра

    for ev in display_events:
        ev_date = ev['datetime'].date()
        if ev['is_recently_past']:
            recently_past_events.append(ev)
        elif ev_date == now.date():
            today_events.append(ev)
        elif ev_date == (now + timedelta(days=1)).date():
            tomorrow_events.append(ev)

    # Выводим недавние просроченные события
    if recently_past_events:
        has_events = True
        section("ПРОШЛО НЕДАВНО (≤5 ч)")
        for event in recently_past_events:
            time_str = event['datetime'].strftime("%H:%M")
            marker = "🔁" if event['is_recurring'] else "•"
            print(f"{COLORS['red']}{time_str} {marker}{COLORS['reset']}")
            print(f"{COLORS['white']}{event['description']}{COLORS['reset']}{COLORS['gray']} (ID: {event['id']}){COLORS['reset']}")
            print()  # Пустая строка между событиями

    # Выводим события «сегодня»
    if today_events:
        has_events = True
        section("СЕГОДНЯ")
        for event in today_events:
            time_str = event['datetime'].strftime("%H:%M")
            marker = "🔁" if event['is_recurring'] else "•"
            print(f"{time_str} {marker}")
            print(f"{COLORS['white']}{event['description']}{COLORS['reset']}{COLORS['gray']} (ID: {event['id']}){COLORS['reset']}")
            print()

    # Выводим события «завтра»
    if tomorrow_events:
        has_events = True
        section("ЗАВТРА")
        for event in tomorrow_events:
            time_str = event['datetime'].strftime("%H:%M")
            marker = "🔁" if event['is_recurring'] else "•"
            print(f"{time_str} {marker}")
            print(f"{COLORS['white']}{event['description']}{COLORS['reset']}{COLORS['gray']} (ID: {event['id']}){COLORS['reset']}")
            print()

    if not has_events:
        print(f"{COLORS['gray']}Нет событий в ближайшие 48 часов и недавних просроченных.{COLORS['reset']}")


def main():
    parser = argparse.ArgumentParser(description="Календарь событий")
    subparsers = parser.add_subparsers(dest='command', help='Команды')

    # Команда add
    add_parser = subparsers.add_parser('add', help='Добавить событие')
    add_parser.add_argument('datetime', help='Дата и время (формат: ДД.ММ ЧЧ:ММ)')
    add_parser.add_argument('description', nargs='+', help='Описание события')
    add_parser.add_argument('--daily', action='store_const', const='daily', dest='recurrence', help='Ежедневное повторение')
    add_parser.add_argument('--weekly', action='store_const', const='weekly', dest='recurrence', help='Еженедельное повторение')
    add_parser.add_argument('--yearly', action='store_const', const='yearly', dest='recurrence', help='Ежегодное повторение')

    # Остальные команды без изменений
    del_parser = subparsers.add_parser('del', help='Удалить событие')
    del_parser.add_argument('id', type=int, help='ID события')

    subparsers.add_parser('show', help='Показать события за 48 часов')

    args = parser.parse_args()

    if args.command == 'add':
        description = ' '.join(args.description)
        add_event(args.datetime, description, args.recurrence)
    elif args.command == 'del':
        delete_event(args.id)
    elif args.command == 'show':
        show_events()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

