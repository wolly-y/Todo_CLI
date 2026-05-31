import sqlite3
import pytest
import database
import tempfile
import os
from database import (
    init_db,
    add_task,
    get_all_tasks,
    update_status,
    update_task,
    delete_task,
    get_overdue_tasks,
    get_statistics,
)
from datetime import date, timedelta

@pytest.fixture(autouse=True)
def test_db():
    """Создаем временный файл БД для тестов."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    database.DB_PATH = db_path
    init_db()
    yield
    os.unlink(db_path)

def test_add_task():
    task_id = add_task('Тестовая задача', "Описание", "высокий", "2026-12-31")
    assert task_id == 1
    tasks = get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Тестовая задача"
    assert tasks[0]["priority"] == "высокий"

def test_add_duplicate():
    add_task('Задача')
    with pytest.raises(ValueError, match='уже существует'):
        add_task('Задача')

def test_get_all_tasks_sorting():
    add_task('Б', priority='средний')
    add_task('А', priority='высокий')
    tasks = get_all_tasks(sort_by='priority')
    assert tasks[0]['title'] == 'А'

def test_update_status():
    add_task('Задача')
    update_status(1, 'в работе')
    tasks = get_all_tasks()
    assert tasks[0]['status'] == 'в работе'

def test_update_status_invalid_id():
    with pytest.raises(ValueError, match='не найдена'):
        update_status(999, 'сделано')

def test_update_task():
    add_task('Задача', 'Старое', 'низкий')
    update_task(1, 'Новое', 'высокий')
    task = get_all_tasks()[0]
    assert task['description'] == 'Новое'
    assert task['priority'] == 'высокий'

def test_delete_task():
    add_task('Задача')
    delete_task(1)
    assert len(get_all_tasks()) == 0

def test_delete_task_invalid_id():
    with pytest.raises(ValueError, match='не найдена'):
        delete_task(999)

def test_get_overdue_tasks():
    today = date.today()
    yesterday = (today - timedelta(days=1)).isoformat()
    tomorrow = (today + timedelta(days=1)).isoformat()
    add_task('Просрочено', deadline=yesterday)
    add_task('Не просрочено', deadline=tomorrow)
    add_task('Без дедлайна')
    overdue = get_overdue_tasks()
    assert len(overdue) == 1
    assert overdue[0]['title'] == 'Просрочено'

def test_get_statistics():
    add_task('Задача 1', priority='высокий')
    add_task('Задача 2', priority='низкий')
    update_status(1, 'сделано')
    stats = get_statistics()
    assert stats['total'] == 2
    assert stats['by_status'] == {'новая': 1, 'сделано': 1}
    assert stats['by_priority'] == {'высокий': 1, 'низкий': 1}
