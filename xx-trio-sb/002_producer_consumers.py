import trio

# 2 consumers, consuming the same channel
# receive channel is cloned
# -> each clone is closed independently
# -> when all clones are closed, the parent is closed


async def producer(send_channel: trio.MemorySendChannel) -> None:
    items: list[int] = list(range(5))

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
        send_channel, receive_channel = trio.open_memory_channel(100)
        nursery.start_soon(producer, send_channel)
        nursery.start_soon(consumer, "CONSUMER_1", receive_channel.clone())
        nursery.start_soon(consumer, "CONSUMER_2", receive_channel.clone())

    print("ALL DONE")


trio.run(main)
