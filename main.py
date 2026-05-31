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

def print_menu():
    """Выводит главное меню программы."""

    print('\n' + '=' * 40)
    print('МЕНЕДЖЕР ЗАДАЧ')
    print('=' * 40)
    print('1. Добавить задачу')
    print('2. Показать все задачи')
    print('3. Изменить статус задачи')
    print('4. Редактировать задачу')
    print('5. Удалить задачу')
    print('6. Просроченные задачи')
    print('7. Статистика')
    print('8. Выход')
    print('=' * 40)

def input_with_cancel(prompt):
    """Безопасный ввод с защитой от Ctrl+C и Ctrl+D.

    Args:
        prompt: Строка-приглашение для ввода.

    Returns:
        Введённую строку или None, если ввод прерван.
    """
    
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print('\nВвод отменён.')
        return None

def input_task_data():
    """Запрашивает у пользователя данные для создания задачи.

    Returns:
        Кортеж (title, description, priority, deadline) или None,
        если ввод прерван или данные некорректны.
    """

    title = input_with_cancel('Название: ')
    if title is None:
        return None
    title = title.strip()
    if not title:
        print('Ошибка: название не может быть пустым.')
        return None

    description = input_with_cancel('Описание (можно оставить пустым): ')
    if description is None:
        return None
    description = description.strip()

    print(f'Приоритет ({", ".join(VALID_PRIORITIES)}):')
    priority = input_with_cancel('> ')
    if priority is None:
        return None
    priority = priority.strip().lower()
    if not priority:
        priority = 'средний'
    elif priority not in VALID_PRIORITIES:
        print(f'Ошибка: неверный приоритет. Допустимые: {", ".join(VALID_PRIORITIES)}')
        return None

    deadline = input_with_cancel('Дедлайн (ГГГГ-ММ-ДД, можно оставить пустым): ')
    if deadline is None:
        return None
    deadline = deadline.strip()
    if not deadline:
        deadline = 'Без дедлайна'
    else:
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', deadline):
            print('Ошибка: неверный формат даты. Используйте ГГГГ-ММ-ДД.')
            return None

    return title, description, priority, deadline

def read_task_id():
    """Безопасно считывает ID задачи.

    Returns:
        Целое число — ID задачи, или None при ошибке ввода.
    """

    try:
        value = input_with_cancel('ID задачи: ')
        if value is None:
            return None
        value = value.strip()
        if not value:
            print('Ошибка: ID не может быть пустым.')
            return None
        return int(value)
    except ValueError:
        print('Ошибка: ID должен быть целым числом.')
        return None

def main():
    """Главный цикл программы: меню и обработка команд."""

    while True:
        print_menu()
        choice = input_with_cancel('Выберите действие (1-8): ')
        if choice is None:
            continue
        choice = choice.strip()

        if choice not in ('1', '2', '3', '4', '5', '6', '7', '8'):
            print('Ошибка: выберите число от 1 до 8.')
            continue

        try:
            if choice == '1':
                data = input_task_data()
                if data is None:
                    continue
                task_id = create_task(*data)
                print(f'Задача создана. ID: {task_id}')

            elif choice == '2':
                print('\nФильтр по статусу (новая | в работе | сделано | все):')
                status = input_with_cancel('> ')
                if status is None:
                    continue
                status = status.strip().lower()
                if status == 'все' or not status:
                    status = None
                elif status not in VALID_STATUSES:
                    print('Ошибка: неверный статус. Показаны все задачи.')
                    status = None

                print('Сортировка (время | приоритет | дедлайн):')
                sort_input = input_with_cancel('> ')
                if sort_input is None:
                    continue
                sort_input = sort_input.strip().lower()
                sort_dict = {
                    'время': 'created_at',
                    'приоритет': 'priority',
                    'дедлайн': 'deadline'
                }
                sort = sort_dict.get(sort_input)
                if not sort:
                    if sort_input:
                        print('Ошибка: неверный тип сортировки. Использована сортировка по времени.')
                    sort = 'created_at'

                tasks = list_tasks(status_filter=status, sort_by=sort)
                if tasks:
                    for task in tasks:
                        print(format_task(task))
                        print()
                else:
                    print('Задач не найдено.')

            elif choice == '3':
                task_id = read_task_id()
                if task_id is None:
                    continue

                print(f'Новый статус ({", ".join(VALID_STATUSES)}):')
                new_status = input_with_cancel('> ')
                if new_status is None:
                    continue
                new_status = new_status.strip().lower()
                if not new_status:
                    print('Ошибка: статус не может быть пустым.')
                    continue
                if new_status not in VALID_STATUSES:
                    print(f'Ошибка: неверный статус. Допустимые: {", ".join(VALID_STATUSES)}')
                    continue

                change_status(task_id, new_status)
                print('Статус обновлён!')

            elif choice == '4':
                task_id = read_task_id()
                if task_id is None:
                    continue

                description = input_with_cancel('Новое описание: ')
                if description is None:
                    continue
                description = description.strip()

                print(f'Новый приоритет ({", ".join(VALID_PRIORITIES)}):')
                priority = input_with_cancel('> ')
                if priority is None:
                    continue
                priority = priority.strip().lower()
                if not priority:
                    print('Ошибка: приоритет не может быть пустым.')
                    continue
                if priority not in VALID_PRIORITIES:
                    print(f'Ошибка: неверный приоритет. Допустимые: {", ".join(VALID_PRIORITIES)}')
                    continue

                edit_task(task_id, description, priority)
                print('Задача обновлена.')

            elif choice == '5':
                task_id = read_task_id()
                if task_id is None:
                    continue

                confirm = input_with_cancel(f'Удалить задачу {task_id}? (да | нет): ')
                if confirm is None:
                    continue
                confirm = confirm.strip().lower()
                if confirm == 'да':
                    remove_task(task_id)
                    print('Задача удалена!')
                elif confirm == 'нет':
                    print('Отменено.')
                else:
                    print('Ошибка: введите "да" или "нет". Отменено.')

            elif choice == '6':
                tasks = get_overdue()
                if tasks:
                    print(f'\nПросрочено задач: {len(tasks)}')
                    for task in tasks:
                        print(format_task(task))
                        print()
                else:
                    print('Просроченных задач нет.')

            elif choice == '7':
                stats = get_stats()
                print(f'\n{format_stats(stats)}')

            elif choice == '8':
                print('Завершение программы.')
                break

        except ValueError as e:
            print(f'Ошибка: {e}')
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')

if __name__ == '__main__':
    main()
