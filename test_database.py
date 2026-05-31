import pytest
from models import (
    create_task,
    list_tasks,
    change_status,
    edit_task,
    remove_task,
    get_overdue,
    get_stats,
    format_task,
    format_stats,
    VALID_PRIORITIES,
    VALID_STATUSES,
)

import tempfile
import os
import database

@pytest.fixture(autouse=True)
def setup_db():
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    database.DB_PATH = db_path
    database.init_db()
    yield
    os.unlink(db_path)

def test_create_task_success():
    task_id = create_task('Тест', 'Описание', 'высокий', '2026-12-31')
    assert task_id == 1

def test_create_task_empty_title():
    with pytest.raises(ValueError, match='Название задачи не может быть пустым'):
        create_task('')

def test_create_task_whitespace_title():
    with pytest.raises(ValueError, match='Название задачи не может быть пустым'):
        create_task('   ')

def test_create_task_invalid_priority():
    with pytest.raises(ValueError, match='Недопустимый приоритет'):
        create_task('Задача', priority='срочный')

def test_create_task_default_values():
    task_id = create_task('Задача')
    tasks = list_tasks()
    assert tasks[0]['priority'] == 'средний'
    assert tasks[0]['deadline'] == 'Без дедлайна'
    assert tasks[0]['description'] == ''

def test_change_status_success():
    create_task('Задача')
    change_status(1, 'в работе')
    tasks = list_tasks()
    assert tasks[0]['status'] == 'в работе'

def test_change_status_invalid_status():
    create_task('Задача')
    with pytest.raises(ValueError, match='Недопустимый статус'):
        change_status(1, 'завершена')

def test_change_status_invalid_id():
    with pytest.raises(ValueError):
        change_status(999, 'сделано')

def test_edit_task_success():
    create_task('Задача', 'Старое', 'низкий')
    edit_task(1, 'Новое', 'высокий')
    task = list_tasks()[0]
    assert task['description'] == 'Новое'
    assert task['priority'] == 'высокий'

def test_edit_task_invalid_priority():
    create_task('Задача')
    with pytest.raises(ValueError, match='Недопустимый приоритет'):
        edit_task(1, 'Описание', 'сверхсрочный')

def test_remove_task_success():
    create_task('Задача')
    remove_task(1)
    assert len(list_tasks()) == 0

def test_remove_task_invalid_id():
    with pytest.raises(ValueError):
        remove_task(999)

def test_list_tasks_invalid_status():
    create_task('Задача')
    with pytest.raises(ValueError, match='Недопустимый статус'):
        list_tasks(status_filter='неизвестный')

def test_format_task():
    task = {
        'id': 1,
        'title': 'Тест',
        'status': 'новая',
        'priority': 'высокий',
        'deadline': '2026-12-31',
        'description': 'Описание'
    }
    result = format_task(task)
    assert '[1] Тест' in result
    assert 'Статус: новая' in result
    assert 'Приоритет: высокий' in result
    assert 'Дедлайн: 2026-12-31' in result
    assert 'Описание' in result

def test_format_task_empty_description():
    task = {
        'id': 2,
        'title': 'Без описания',
        'status': 'сделано',
        'priority': 'низкий',
        'deadline': 'Без дедлайна',
        'description': ''
    }
    result = format_task(task)
    assert '—' in result

def test_format_stats():
    stats = {
        'total': 5,
        'by_status': {'новая': 3, 'в работе': 1, 'сделано': 1},
        'by_priority': {'высокий': 2, 'средний': 2, 'низкий': 1}
    }
    result = format_stats(stats)
    assert 'Всего задач: 5' in result
    assert 'новая: 3' in result
    assert 'высокий: 2' in result

def test_get_overdue_empty():
    overdue = get_overdue()
    assert isinstance(overdue, list)
    assert len(overdue) == 0

def test_get_stats_empty():
    stats = get_stats()
    assert stats['total'] == 0
    assert stats['by_status'] == {}
    assert stats['by_priority'] == {}
