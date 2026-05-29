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
    print('\n' + '=' * 40)
    print('МЕНЕДЖЕР ЗАДАЧ')
    print('=' * 40)
    print('1. Добавить задачу')
    print('2. Показать все задачи')
    print('3. Изменить статус задачи')
    print('4. Редактировать задачу')
    print('5. Удалить задачу')
    print('6. Просреченные задачи')
    print('7. Статистика')
    print('8. Выход')
    print('=' * 40)

def input_task_data():
    title = input('Название: ').strip()
    if not title:
        print("Ошибка: название не может быть пустым")
        return None

    description = input('Описание (можно оставить пустым): ').strip()
    print(f'Приоритет ({', '.join(VALID_PRIORITIES)}):')
    priority = input('> ').strip().lower()
    if not priority:
        priority = 'средний'

    deadline = input('Дедлайн (ГГГГ-ММ-ДД, можно оставить пустым): ').strip()
    if not deadline:
        deadline = "Без дедлайна"

    return title, description, priority, deadline

def main():
    while True:
        print_menu()
        choice = input('Выберите действие (1-8): ').strip()

        try:
            if choice == '1':
                data = input_task_data()
                if data:
                    task_id = create_task(*data)
                    print(f'Задача создана. ID: {task_id}')

            elif choice == '2':
                print('\nФильтр по статусу (новая | в работе | сделано | все):')
                status = input('> ').strip().lower()
                if status == "все" or not status:
                    status = None

                print('Сортировка (время | приоритет | дедлайн):')
                sort_dict = {
                    'время': 'created_at',
                    "приоритет": 'priority',
                    "дедлайн" : 'deadline'
                }
                sort = sort_dict.get(input('> ').strip().lower(), 'created_at')
                if not sort:
                    sort = 'created_at'

                tasks = list_tasks(status_filter=status, sort_by=sort)
                if tasks:
                    for task in tasks:
                        print(format_task(task))
                        print()
                else:
                    print('Задач не найдено')

            elif choice == '3':
                task_id = int(input("ID задачи: "))
                print(f'Новый статус ({", ".join(VALID_STATUSES)}):')
                new_status = input('> ').strip().lower()
                change_status(task_id, new_status)
                print('Статус обновлен!')

            elif choice == '4':
                task_id = int(input('ID задачи: '))
                description = input('Новое описание: ').strip()
                print(f'Новый приоритет ({", ".join(VALID_PRIORITIES)}):')
                priority = input('> ').strip().lower()
                edit_task(task_id, description, priority)
                print('Задача обновлена.')

            elif choice == '5':
                task_id = int(input('ID задачи: '))
                confirm = input(f'Удалить задачу {task_id}?\n(да | нет): ').strip().lower()
                if confirm == 'да':
                    remove_task(task_id)
                    print('Задача удалена!')
                else:
                    print("Отменено.")

            elif choice == '6':
                tasks = get_overdue()
                if tasks:
                    print(f'\nПросрочено задач: {len(tasks)}')
                    for task in tasks:
                        print(format_task(task))
                        print()
                else:
                    print("Просроченных задач нет.")

            elif choice == '7':
                stats = get_stats()
                print(f'\n{format_stats(stats)}')

            elif choice == '8':
                print("Завершение программы.")
                break

            else:
                print('Неверный выбор. Введите число от 1 до 8.')

        except ValueError as e:
            print(f'Ошибка: {e}')

        except Exception as e:
            print(f'Неизвестная ошибка: {e}')

if __name__ == '__main__':
    main()