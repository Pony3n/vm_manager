import asyncio

from server.models import VirtualMachine, Disk, User


sessions = {}
active_connections_count = asyncio.Queue()


async def handle_register(reader, writer, data):
    username, password = data.split()
    user = User(username=username, password=password)
    await user.save()
    writer.write(f'User {username} registered successfully\n'.encode())
    await writer.drain()


async def handle_login(reader, writer, data):
    username, password = data.split()
    user = await User.get_by_username(username)
    if user and user.password == password:
        sessions[writer] = user.user_id
        writer.write(f'User {username} logged in successfully\n'.encode())
    else:
        writer.write(f'Invalid username or password\n'.encode())
    await writer.drain()


async def handle_logout(reader, writer):
    user_id = sessions.get(writer)
    if user_id:
        user = await User.get_by_id(user_id)
        await user.logout(sessions, writer)
        writer.write(f'User {user.username} logged out successfully\n'.encode())
    else:
        writer.write('No user logged in\n'.encode())
    await writer.drain()


async def handle_create_vm(reader, writer, data):
    user_id = sessions.get(writer)
    if not user_id:
        writer.write("User not authenticated\n".encode())
        await writer.drain()
        return

    existing_vm = await VirtualMachine.get_by_user_id(user_id)
    if existing_vm:
        writer.write("User already created a virtual machine\n".encode())
        await writer.drain()
        return

    ram, cpu_count = map(int, data.split())
    vm = VirtualMachine(ram=ram, cpu_count=cpu_count)
    print(f'User: {user_id} trying to create VM')
    await vm.save(user_id)
    writer.write(f"Virtual machine created with ID {vm.vm_id}\n".encode())
    await writer.drain()


async def handle_update_vm(reader, writer, data):
    user_id = sessions.get(writer)
    if not user_id:
        writer.write("User not authenticated\n".encode())
        await writer.drain()
        return

    vm_id, ram, cpu_count = map(int, data.split())
    vm = VirtualMachine(vm_id=vm_id, ram=ram, cpu_count=cpu_count)
    await vm.update()
    writer.write(f"Virtual machine {vm_id} updated\n".encode())
    await writer.drain()


async def handle_get_vm(reader, writer):
    user_id = sessions.get(writer)
    if not user_id:
        writer.write("User not authenticated\n".encode())
        await writer.drain()
        return

    vm = await VirtualMachine.get_by_user_id(user_id)
    if not vm:
        writer.write('No Virtual machine found')
    else:
        writer.write(f'Virtual machine: {vm}'.encode())
    await writer.drain()


async def handle_create_disk(reader, writer, data):
    user_id = sessions.get(writer)
    if not user_id:
        writer.write("User not authenticated\n".encode())
        await writer.drain()
        return

    vm = await VirtualMachine.get_by_user_id(user_id)
    if not vm:
        writer.write("No virtual machine found for this user\n".encode())
        await writer.drain()
        return

    writer.write("Enter disk size: ".encode())
    await writer.drain()
    data = await reader.read(100)
    size = data.decode().strip()

    try:
        size = int(size)
    except ValueError:
        writer.write("Invalid size format\n".encode())
        await writer.drain()
        return

    disk = Disk(size=size)
    await disk.save(vm.vm_id)
    writer.write(f"Disk of size {size} created for VM ID {vm.vm_id}\n".encode())
    await writer.drain()


async def handle_update_disk(reader, writer, data):
    user_id = sessions.get(writer)
    if not user_id:
        writer.write("User not authenticated\n".encode())
        await writer.drain()
        return

    disk_id, size = map(int, data.split())
    disk = Disk(disk_id=disk_id, size=size)
    await disk.update()
    writer.write(f"Disk {disk_id} updated\n".encode())
    await writer.drain()


async def handle_list_disks(reader, writer):
    user_id = sessions.get(writer)
    if not user_id:
        writer.write("User not authenticated\n".encode())
        await writer.drain()
        return

    vm = await VirtualMachine.get_by_user_id(user_id)
    if not vm:
        writer.write("No virtual machine found for this user\n".encode())
        await writer.drain()
        return

    await vm.load_disks()
    if not vm.disks:
        writer.write("No disks found for this VM\n".encode())
    else:
        for disk in vm.disks:
            writer.write(f"Disk ID: {disk.disk_id}, Size: {disk.size}, VM ID: {disk.vm_id}\n".encode())
    await writer.drain()


async def handle_client(reader, writer):
    global active_connections_count
    await active_connections_count.put(1)
    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            command, *args = data.decode().strip().split(' ', 1)
            print(f'args: {args}')
            args = args[0] if args else ''

            if command == 'REGISTER':
                await handle_register(reader, writer, args)
            elif command == 'LOGIN':
                await handle_login(reader, writer, args)
            elif command == 'LOGOUT':
                await handle_logout(reader, writer)
            elif command == 'CREATE_VM':
                await handle_create_vm(reader, writer, args)
            elif command == 'GET_VM':
                await handle_get_vm(reader, writer)
            elif command == 'UPDATE_VM':
                await handle_update_vm(reader, writer, args)
            elif command == 'CREATE_DISK':
                await handle_create_disk(reader, writer, args)
            elif command == 'UPDATE_DISK':
                await handle_update_disk(reader, writer, args)
            elif command == 'LIST_DISKS':
                await handle_list_disks(reader, writer)
            else:
                writer.write(f"Unknown command: {command}\n".encode())
                await writer.drain()
    finally:
        await active_connections_count.get()
        writer.close()


