import sqlite3
from datetime import date

DB_PATH = 'todo.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            priority TEXT NOT NULL DEFAULT 'средний',
            status TEXT NOT NULL DEFAULT 'новая',
            created_at TEXT NOT NULL,
            deadline TEXT NOT NULL DEFAULT 'Без дедлайна'
        )
    ''')

    conn.commit()
    conn.close()

def add_task(title, description='', priority='средний', deadline='Без дедлайна'):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM tasks WHERE title = ?', (title,))
    if cursor.fetchone() is not None:
        conn.close()
        raise ValueError(f'Задача с названием "{title}" уже существует')

    created = date.today().isoformat()

    cursor.execute('''
        INSERT INTO tasks (title, description, priority, status, created_at, deadline)
        VALUES (?, ?, ?, 'новая', ?, ?)
    ''', (title, description, priority, created, deadline))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_all_tasks(status_filter=None, sort_by='created_at'):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM tasks'
    params = []

    if status_filter:
        query += ' WHERE status = ?'
        params.append(status_filter)

    if sort_by == 'priority':
        query += ' ORDER BY CASE priority WHEN "высокий" THEN 1 WHEN "средний" THEN 2 WHEN "низкий" THEN 3 END'
    elif sort_by == 'deadline':
        query += ' ORDER BY deadline'
    else:
        query += ' ORDER BY created_at DESC'

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def update_status(task_id, new_status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (new_status, task_id))
    if cursor.rowcount == 0:
        conn.close()
        raise ValueError(f'Задача с id = {task_id} не найдена')

    conn.commit()
    conn.close()

def update_task(task_id, description, priority):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('UPDATE tasks SET description = ?, priority = ? WHERE id = ?',
                   (description, priority, task_id))

    if cursor.rowcount == 0:
        conn.close()
        raise ValueError(f'Задача с id = {task_id} не найдена')

    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM tasks WHERE id =?', (task_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise ValueError(f'Задача с id = {task_id} не найдена')

    conn.commit()
    conn.close()

def get_overdue_tasks():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    today = date.today().isoformat()
    cursor.execute('''
        SELECT * FROM tasks
        WHERE deadline != 'Без дедлайна'
            AND deadline < ?
            AND status != 'сделано'
        ORDER BY deadline
    ''', (today,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_statistics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM tasks')
    total = cursor.fetchone()[0]

    cursor.execute('SELECT status, COUNT(*) FROM tasks GROUP BY status')
    by_status = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute('SELECT priority, COUNT(*) FROM tasks GROUP BY priority')
    by_priority = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()
    return {
        'total': total,
        'by_status': by_status,
        'by_priority': by_priority
    }

if __name__ == '__main__':
    init_db()

    try:
        new_id = add_task('Купить молоко', 'В магазине, у дома', 'высокий', '2026-06-01')
        print(f'Задача добавлена, id = {new_id}')
    except ValueError:
        pass

    try:
        add_task('Погулять с собакой', priority='низкий', deadline='2026-05-27')
    except ValueError:
        pass

    try:
        add_task('Доделать проект', 'Сдать до пятницы', 'высокий', '2026-05-29')
    except ValueError:
        pass

    print('\nВсе задачи:')
    for task in get_all_tasks():
        print(f'[{task['id']}] {task['title']}')
        print(f'Статус: {task['status']}')
        print(f'Приоритет: {task['priority']}')
        print(f'Дедлайн: {task['deadline']}')

    print('\nЗадачи с высоким приоритетом:')
    for task in get_all_tasks(sort_by='priority'):
        print(f'[{task['id']}] {task['title']}')
        print(f'Приоритет: {task['priority']}')

    print('\n--- Тест обновления статуса ---')
    update_status(1, 'в работе')
    task = get_all_tasks()[0]
    print(f"Задача 1 теперь: {task['status']}")

    print('\n--- Тест обновления описания и приоритета ---')
    update_task(2, 'В парке', 'средний')
    tasks = get_all_tasks()
    for t in tasks:
        if t['id'] == 2:
            print(f"Задача 2: описание='{t['description']}', приоритет='{t['priority']}'")

    print('\n--- Тест просроченных задач ---')
    overdue = get_overdue_tasks()
    print(f'Просрочено: {len(overdue)}')
    for t in overdue:
        print(f"[{t['id']}] {t['title']} | дедлайн: {t['deadline']}")

    print('\n--- Тест статистики ---')
    stats = get_statistics()
    print(f"Всего задач: {stats['total']}")
    print(f"По статусам: {stats['by_status']}")
    print(f"По приоритетам: {stats['by_priority']}")

    print('\n--- Тест удаления ---')
    delete_task(3)
    print('Задача 3 удалена')
    print(f"Осталось задач: {len(get_all_tasks())}")