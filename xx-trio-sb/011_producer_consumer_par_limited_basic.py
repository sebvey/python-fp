import trio

# With limited parallelism - basic:
# -> we launch x sub_consumers task in parallel
# -> each sub_consumer reads from a receive_channel clone

PAR = 3


async def producer(send_channel: trio.MemorySendChannel) -> None:
    items: list[int] = list(range(50))

    async with send_channel:
        for i in items:
            print(f"@@ producer - ({i})")
            await send_channel.send(i)


async def consume(i: int, consumer_name: str) -> None:
    print(f"{consumer_name} - {i} - starting consumption ...")
    await trio.sleep(3)
    print(f"{consumer_name} - {i} - consumed !")


async def consumer(
    name: str,
    receive_channel: trio.MemoryReceiveChannel,
) -> str:
    async with receive_channel:
        async for i in receive_channel:
            await consume(i, name)


async def main() -> None:
    async with trio.open_nursery() as nursery:
        send_channel, receive_channel = trio.open_memory_channel(9999)
        nursery.start_soon(producer, send_channel)
        await trio.sleep(0.1)
        for n in range(PAR):
            consumer_name: str = f"CONSUMER_{n}"
            nursery.start_soon(consumer, consumer_name, receive_channel.clone())

    print("ALL DONE")


trio.run(main)
