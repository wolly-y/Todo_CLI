from database import (
    add_task as db_add_task,
    get_all_tasks as db_get_all_tasks,
    update_status as db_update_status,
    update_task as db_update_task,
    delete_task as db_delete_task,
    get_overdue_tasks as db_get_overdue_tasks,
    get_statistics as db_get_statistics,
)

VALID_PRIORITIES = {'высокий', 'средний', 'низкий'}
VALID_STATUSES = {'новая', 'в работе', 'сделано'}

def create_task(title, description='', priority='средний', deadline='Без дедлайна'):
    title = title.strip()
    if not title:
        raise ValueError('Название задачи не может быть пустым')
    if priority not in VALID_PRIORITIES:
        raise ValueError(f'Недопустимый приоритет. Допустимые: {VALID_PRIORITIES}')
    return db_add_task(title, description, priority, deadline)

def list_tasks(status_filter=None, sort_by='created_at'):
    if status_filter and status_filter not in VALID_STATUSES:
        raise ValueError(f'Недопустимый статус. Допустимые: {VALID_STATUSES}')
    return db_get_all_tasks(status_filter, sort_by)

def change_status(task_id, new_status):
    if new_status not in VALID_STATUSES:
        raise ValueError(f'Недопустимый статус. Допустимые: {VALID_STATUSES}')
    db_update_status(task_id, new_status)

def edit_task(task_id, description, priority):
    if priority not in VALID_PRIORITIES:
        raise ValueError(f'Недопустимый приоритет. Допустимые: {VALID_PRIORITIES}')
    db_update_task(task_id, description, priority)

def remove_task(task_id):
    db_delete_task(task_id)

def get_overdue():
    return db_get_overdue_tasks()

def get_stats():
    return db_get_statistics()

def format_task(task):
    return (
        f"[{task['id']}] {task['title']}\n"
        f"  Статус: {task['status']} | Приоритет: {task['priority']} | Дедлайн: {task['deadline']}\n"
        f"  Описание: {task['description'] or '—'}"
    )

def format_stats(stats):
    lines = [f'Всего задач: {stats["total"]}']
    lines.append('По статусам:')
    for status, count in stats['by_status'].items():
        lines.append(f' {status}: {count}')
    lines.append('По приоритетам:')
    for priority, count in stats['by_priority'].items():
        lines.append(f' {priority}: {count}')
    return '\n'.join(lines)