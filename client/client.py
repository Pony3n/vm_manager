import asyncio
from client.handlers import handle_command


async def tcp_client():
    reader, writer = await asyncio.open_connection('localhost', 8888)

    while True:
        command = input("Enter command: ")
        if command.lower() in ('exit', 'quit'):
            print("Exiting...")
            writer.write(b'exit\n')
            await writer.drain()
            break

        await handle_command(reader, writer, command)

    writer.close()
    await writer.wait_closed()


if __name__ == '__main__':
    asyncio.run(tcp_client())
