import asyncpg
from config.config import DB_CONFIG


async def init_db():
    conn = await asyncpg.connect(**DB_CONFIG)
    try:

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS virtual_machines (
                vm_id SERIAL PRIMARY KEY,
                ram INTEGER NOT NULL,
                cpu_count INTEGER NOT NULL,
                user_id INTEGER
            )
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS disks (
                disk_id SERIAL PRIMARY KEY,
                size INTEGER NOT NULL,
                vm_id INTEGER
            )
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(80) NOT NULL UNIQUE,
                password VARCHAR(80) NOT NULL,
                vm_id INTEGER
            )
        ''')

        try:
            await conn.execute('''
                ALTER TABLE virtual_machines
                ADD CONSTRAINT fk_virtual_machines_users FOREIGN KEY (user_id)
                REFERENCES users(user_id) DEFERRABLE INITIALLY DEFERRED
            ''')
        except asyncpg.exceptions.DuplicateObjectError:
            pass

        try:
            await conn.execute('''
                    ALTER TABLE disks
                    ADD CONSTRAINT fk_disks_virtual_machines FOREIGN KEY (vm_id)
                    REFERENCES virtual_machines(vm_id) DEFERRABLE INITIALLY DEFERRED
                ''')
        except asyncpg.exceptions.DuplicateObjectError:
            pass

        try:
            await conn.execute('''
                    ALTER TABLE users
                    ADD CONSTRAINT fk_users_virtual_machines FOREIGN KEY (vm_id)
                    REFERENCES virtual_machines(vm_id) DEFERRABLE INITIALLY DEFERRED
                ''')
        except asyncpg.exceptions.DuplicateObjectError:
            pass
    finally:
        await conn.close()


async def get_db_connection():
    return await asyncpg.connect(**DB_CONFIG)
