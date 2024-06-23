async def handle_command(reader, writer, command):
    writer.write(f"{command}\n".encode())
    await writer.drain()

    response = await reader.read(1000)
    print(response.decode())