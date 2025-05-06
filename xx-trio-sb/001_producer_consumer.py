import trio

# producer produces elements one by one (no parallelism)
# the queue can hold up to 5 items trio.open_memory_channel(5) (float('inf) -> no restriction)
# producer is waiting for room in the queue at send_channel.send(...)

# consumer consumes elements one by one (no parallelism)
# consumer is waiting for an item in the queue at async for e in receive_channel


async def producer(send_channel: trio.MemorySendChannel) -> None:
    items: list[int] = list(range(5))

    # async with -> closes the send channel once block exited
    async with send_channel:
        for i in items:
            print(f"@@ producer - ({i})")
            await send_channel.send(i)


async def consume(i: int) -> None:
    print(f"{i} - starting consumption ...")
    await trio.sleep(3)
    print(f"{i} - consumed !")


async def consumer(receive_channel: trio.MemoryReceiveChannel) -> str:
    # async with -> when send channel closed and queue empty -> closes the receive channel
    async with receive_channel:
        async for i in receive_channel:
            await consume(i)


async def main() -> None:
    async with trio.open_nursery() as nursery:
        send_channel, receive_channel = trio.open_memory_channel(100)
        nursery.start_soon(producer, send_channel)
        nursery.start_soon(consumer, receive_channel)

    print("ALL DONE")


trio.run(main)
