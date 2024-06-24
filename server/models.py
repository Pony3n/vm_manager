import asyncpg
from server.db import get_db_connection


class User:

    def __init__(self, username, password, user_id=None, vm_id=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.vm_id = vm_id

    async def save(self):
        """
        Метод для сохранения нового пользователя
        """
        conn = await get_db_connection()
        try:
            result = await conn.fetchrow(
                'INSERT INTO users (username, password, vm_id) VALUES ($1, $2, $3) RETURNING user_id',
                self.username,
                self.password,
                self.vm_id
            )
            self.user_id = result['user_id']
        finally:
            await conn.close()

    async def update(self):
        """
        Метод для обновления данных пользователя
        """
        conn = await get_db_connection()
        try:
            await conn.execute(
                'UPDATE users SET username=$1, password=$2 WHERE user_id=$3',
                self.username,
                self.password,
                self.user_id
            )
        finally:
            conn.close()

    async def logout(self, sessions, writer):
        """
        Метод для выхода из авторизованного пользователя
        """
        if writer in sessions and sessions[writer] == self.user_id:
            del sessions[writer]

    @staticmethod
    async def get_by_username(username):
        """
        Получение пользователя по username
        """
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow('SELECT * FROM users WHERE username=$1', username)
            await conn.close()
            if row:
                return User(row['username'], row['password'], row['user_id'], row['vm_id'])
            return None
        finally:
            await conn.close()

    @staticmethod
    async def get_by_id(user_id):
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow('SELECT * FROM users WHERE user_id=$1', user_id)
            if row:
                return User(row['user_id'], row['username'], row['password'], row['vm_id'])
            return None
        finally:
            await conn.close()

    def __str__(self):
        return f'User ID: {self.user_id}, Username: {self.username}'


class VirtualMachine:

    def __init__(self, ram, cpu_count, user_id=None, vm_id=None):
        self.vm_id = vm_id
        self.ram = ram
        self.cpu_count = cpu_count
        self.user_id = user_id
        self.disks = []

    async def save(self, user_id):
        """
        Метод для создания virtual machine
        """
        conn = await get_db_connection()
        try:
            if self.vm_id is None:
                result = await conn.fetchrow(
                    'INSERT INTO virtual_machines (ram, cpu_count, user_id) VALUES ($1, $2, $3) RETURNING vm_id',
                    self.ram,
                    self.cpu_count,
                    user_id
                )
                self.vm_id = result['vm_id']
                await conn.execute(
                    'UPDATE users SET vm_id=$1 WHERE user_id=$2',
                    self.vm_id,
                    user_id
                )
        finally:
            await conn.close()

    async def update(self):
        """
        Метод для обновления информации по virtual machine
        """
        conn = await get_db_connection()
        try:
            await conn.execute(
                'UPDATE virtual_machines SET ram=$1, cpu_count=$2 WHERE vm_id=$3',
                self.ram,
                self.cpu_count,
                self.vm_id
            )
        finally:
            await conn.close()

    @staticmethod
    async def get_by_user_id(user_id):
        """
        Метод для получения данных о виртуальной машине по user_id
        """
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow(
                'SELECT * FROM virtual_machines WHERE user_id=$1',
                user_id
            )
            if row:
                vm = VirtualMachine(row['ram'], row['cpu_count'], row['user_id'], row['vm_id'])
                await vm.load_disks()
                return vm
        finally:
            await conn.close()

    @staticmethod
    async def get_all_vms():
        """
        Метод для получения всех ВМ
        """
        conn = await get_db_connection()
        try:
            rows = await conn.fetch('SELECT vm_id, ram, cpu_count, user_id FROM virtual_machines')
            vms = [VirtualMachine(row['ram'], row['cpu_count'], row['user_id'], row['vm_id'])
                   for row in rows]
            for vm in vms:
                await vm.load_disks()
            return vms
        finally:
            await conn.close()

    @staticmethod
    async def get_logged_vms(user_ids):
        """
        Метод для получения всех ВМ, принадлежащих авторизованным пользователям
        """
        conn = await get_db_connection()
        try:
            vms = []
            rows = await conn.fetch(
                'SELECT * FROM virtual_machines WHERE user_id = ANY($1::int[])',
                user_ids
            )
            for row in rows:
                vm = VirtualMachine(row['ram'], row['cpu_count'], row['user_id'], row['vm_id'])
                await vm.load_disks()
                vms.append(vm)
            return vms
        finally:
            await conn.close()

    async def load_disks(self):
        """
        Метод для загрузки дисков, привязанных к виртуальной машине
        """
        conn = await get_db_connection()
        try:
            rows = await conn.fetch(
                'SELECT * FROM disks WHERE vm_id=$1',
                self.vm_id
            )
            self.disks = [Disk(row['size'], row['disk_id'], row['vm_id']) for row in rows]
        finally:
            await conn.close()

    def __str__(self):
        disk_count = len(self.disks)
        return f'VM ID: {self.vm_id}, RAM: {self.ram} MB, CPU: {self.cpu_count}, Disks count: {disk_count}'


class Disk:

    def __init__(self, size, disk_id=None, vm_id=None):
        self.disk_id = disk_id
        self.size = size
        self.vm_id = vm_id

    async def save(self, vm_id):
        """
        Метод для сохранения диска для определенной virtual machine
        """
        conn = await get_db_connection()
        try:
            result = await conn.fetchrow(
                'INSERT INTO disks (size, vm_id) VALUES ($1, $2) RETURNING disk_id',
                self.size,
                vm_id
            )
            self.disk_id = result['disk_id']
        finally:
            await conn.close()

    async def update(self):
        """
        Метод для обновления данных о диске
        """
        conn = await get_db_connection()
        try:
            await conn.execute(
                'UPDATE disks SET size=$1 WHERE disk_id=$2',
                self.size,
                self.disk_id
            )
        finally:
            await conn.close()

