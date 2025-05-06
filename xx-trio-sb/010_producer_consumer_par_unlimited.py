import trio

# With unlimited paralllelism:
# -> consumer is a nursery, starting consume task as soon as an item is available


async def producer(send_channel: trio.MemorySendChannel) -> None:
    items: list[int] = list(range(50))

    async with send_channel:
        for i in items:
            print(f"@@ producer - ({i})")
            await send_channel.send(i)


async def consume(i: int) -> None:
    print(f"{i} - starting consumption ...")
    await trio.sleep(3)
    print(f"{i} - consumed !")


async def consumer(receive_channel: trio.MemoryReceiveChannel) -> str:
    async with trio.open_nursery() as nursery:
        async with receive_channel:
            async for i in receive_channel:
                nursery.start_soon(consume, i)


async def main() -> None:
    async with trio.open_nursery() as nursery:
        send_channel, receive_channel = trio.open_memory_channel(9999)
        nursery.start_soon(producer, send_channel)
        nursery.start_soon(consumer, receive_channel)

    print("ALL DONE")


trio.run(main)
