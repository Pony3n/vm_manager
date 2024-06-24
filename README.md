# VM Manager

## Описание

VM Manager - это система для управления виртуальными машинами и дисками. Проект включает серверную и клиентскую части, написанные на Python с использованием `asyncio` и `asyncpg` для асинхронного взаимодействия с базой данных PostgreSQL.

## Установка

1. Установите необходимые зависимости для клиента и сервера:
    ```bash
      git clone https://github.com/Pony3n/vm_manager.git
    ```
   
2. Перейдите в директорию проекта:
   ```bash
   cd vm_manager
   ```
   
3. Настройте базу данных PostgreSQL. Создайте базу данных и настройте конфигурацию в файле `config/config.py`.

4. Запустите сервер:
    ```bash
    python -m server.server
    ```

5. Запустите клиент:
    ```bash
    python -m client.client
    ```

## Методы работы клиента

Клиент может отправлять следующие команды на сервер:

- `REGISTER <username> <password>`: Регистрация нового пользователя.
- `LOGIN <username> <password>`: Вход для зарегистрированного пользователя.
- `LOGOUT`: Выход из системы.
- `GET_VM`: Получение виртуальной машины. 
- `CREATE_VM <vm_name> <ram> <cpu_count>`: Создание новой виртуальной машины.
- `UPDATE_VM <vm_id> <vm_name> <ram> <cpu_count>`: Обновление существующей виртуальной машины.
- `CREATE_DISK <size>`: Создание нового диска.
- `UPDATE_DISK <disk_id> <size>`: Обновление существующего диска.
- `LIST_DISKS`: Получение списка всех дисков.

## Методы работы сервера

Сервер имеет внутренние команды, которые могут быть выполнены только с сервера:

- `exit`: Завершение работы сервера.
- `get_active_connections`: Показать количество активных подключений.
- `get_all_vms`: Показать все виртуальные машины из базы данных.
- `get_logged_vms`: Показать виртуальные машины, принадлежащие авторизованным пользователям.