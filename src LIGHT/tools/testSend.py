import asyncio

async def tcp_echo_client(message):

    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    except :
        server = await asyncio.start_server(handle_echo, '127.0.0.1', 8888)

    print(f'Send: {message!r}')
    writer.write(message.encode())

    print('Close the connection')
    writer.close()

asyncio.run(tcp_echo_client('Hello World!'))
