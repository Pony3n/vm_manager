import asyncio

from server.handlers_client import handle_client
from server.handlers_server import command_loop
from server.db import init_db


async def main():
    await init_db()

    server = await asyncio.start_server(handle_client, '0.0.0.0', 8888)

    async with server:
        print('Сервер запущен на порту :8888')

        await command_loop(server)

        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
