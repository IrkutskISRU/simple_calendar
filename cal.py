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
    'reset': '\033[0m'
}

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

def add_event(date_time_str, description):
    """Добавляет новое событие."""
    try:
        # Парсим дату и время
        event_datetime = datetime.strptime(date_time_str, "%d.%m %H:%M")
        # Устанавливаем год — текущий или следующий (если дата уже прошла в этом году)
        current_year = datetime.now().year
        event_datetime = event_datetime.replace(year=current_year)
        if event_datetime < datetime.now():
            event_datetime = event_datetime.replace(year=current_year + 1)

        events = load_events()
        # Находим следующий доступный ID
        next_id = max([e['id'] for e in events], default=0) + 1

        new_event = {
            'id': next_id,
            'datetime': event_datetime.isoformat(),
            'description': description
        }
        events.append(new_event)
        save_events(events)
        print(f"Событие добавлено с ID: {next_id}")
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
    """Показывает события за ближайшие 48 часов, группируя по дням."""
    now = datetime.now()
    tomorrow = now + timedelta(hours=48)

    events = load_events()
    today_events = []
    tomorrow_events = []

    for event in events:
        try:
            event_dt = datetime.fromisoformat(event['datetime'])
            # Проверяем строго: событие должно быть не раньше сейчас И не позже чем через 24 часа
            if now <= event_dt < tomorrow:
                if event_dt.date() == now.date():
                    today_events.append({
                        'datetime': event_dt,
                        'description': event['description'],
                        'id': event['id']
                    })
                elif event_dt.date() == (now + timedelta(days=1)).date():
                    tomorrow_events.append({
                        'datetime': event_dt,
                        'description': event['description'],
                        'id': event['id']
                    })
        except (KeyError, ValueError) as e:
            print(f"Ошибка обработки события {event.get('id', 'неизвестный ID')}: {e}")
            continue

    # Сортируем события по времени
    today_events.sort(key=lambda x: x['datetime'])
    tomorrow_events.sort(key=lambda x: x['datetime'])

    has_events = False

    # Выводим события «сегодня»
    if today_events:
        has_events = True
        section("СЕГОДНЯ")
        for event in today_events:
            time_str = event['datetime'].strftime("%H:%M")
            print(f"{time_str}")
            print(f"{COLORS['white']}{event['description']}{COLORS['reset']}{COLORS['gray']} (ID: {event['id']}){COLORS['reset']}")
            print()  # Пустая строка между событиями

    # Выводим события «завтра»
    if tomorrow_events:
        has_events = True
        section("ЗАВТРА")
        for event in tomorrow_events:
            time_str = event['datetime'].strftime("%H:%M")
            print(f"{time_str}")
            print(f"{COLORS['white']}{event['description']}{COLORS['reset']}{COLORS['gray']} (ID: {event['id']}){COLORS['reset']}")
            print()  # Пустая строка между событиями

    # Если нет событий за 24 часа
    if not has_events:
        print(f"{COLORS['gray']}Нет событий в ближайшие 24 часа.{COLORS['reset']}")

def main():
    parser = argparse.ArgumentParser(description="Календарь событий")
    subparsers = parser.add_subparsers(dest='command', help='Команды')

    # Команда add — используем nargs='+' для описания
    add_parser = subparsers.add_parser('add', help='Добавить событие')
    add_parser.add_argument('datetime', help='Дата и время (формат: ДД.ММ ЧЧ:ММ)')
    add_parser.add_argument('description', nargs='+', help='Описание события')

    # Команда del
    del_parser = subparsers.add_parser('del', help='Удалить событие')
    del_parser.add_argument('id', type=int, help='ID события')

    # Команда show
    subparsers.add_parser('show', help='Показать события за 24 часа')

    args = parser.parse_args()

    if args.command == 'add':
        # Объединяем элементы описания в одну строку
        description = ' '.join(args.description)
        add_event(args.datetime, description)
    elif args.command == 'del':
        delete_event(args.id)
    elif args.command == 'show':
        show_events()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

