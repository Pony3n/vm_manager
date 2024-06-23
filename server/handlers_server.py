import asyncio

from server.handlers_client import sessions
from server.handlers_client import active_connections_count
from server.models import VirtualMachine


async def get_logged_in_vms():
    vms = await VirtualMachine.get_logged_vms(sessions.values())
    return vms


async def command_loop(server):
    while True:
        command = await get_input('Введите команду: ')

        if command == 'exit':
            print("Завершение работы сервера...")
            server.close()
            await server.wait_closed()
            print("Сервер выключен.")
            break
        elif command == 'get_active_connections':
            print(f'Active_connections: {active_connections_count.qsize()}')
        elif command == 'get_all_vms':
            vms = await VirtualMachine.get_all_vms()
            if vms:
                for vm in vms:
                    print(f"VM ID: {vm.vm_id}, User ID: {vm.user_id}, RAM: {vm.ram}, CPU Count: {vm.cpu_count}")
                    if vm.disks:
                        for disk in vm.disks:
                            print(f"  Disk ID: {disk.disk_id}, Size: {disk.size}")
                    else:
                        print("  No disks attached")
            else:
                print("Нет зарегистрированных виртуальных машин")
        elif command == 'list_logged_in_vms':
            vms = await get_logged_in_vms()
            if vms:
                for vm in vms:
                    print(f"VM ID: {vm.vm_id}, User ID: {vm.user_id}, RAM: {vm.ram}, CPU Count: {vm.cpu_count}")
                    for disk in vm.disks:
                        print(f"   Disk ID: {disk.disk_id}, Size: {disk.size}")
            else:
                print("No VMs for logged in users.")
        else:
            print("Неизвестная команда")


async def get_input(prompt):
    print(prompt, end='', flush=True)
    return (await asyncio.get_event_loop().run_in_executor(None, input)).strip()
