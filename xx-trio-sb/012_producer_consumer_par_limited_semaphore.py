import trio

# With limited parallelism - with semaphore:
# - a semaphore is handled by the consumer
# - a nursery is handled by the consumer
# - launching a task is conditioned to semaphore
# - each time the consumer launch a consume task, it 'acquire' from the semaphore
# - the task itself 'release' from the semaphore

PAR = 4


async def producer(send_channel: trio.MemorySendChannel) -> None:
    items: list[int] = list(range(50))

    async with send_channel:
        for i in items:
            print(f"@@ producer - ({i})")
            await send_channel.send(i)


async def consume(i: int, semaphore: trio.Semaphore) -> None:
    print(f"{i} - starting consumption ...")
    await trio.sleep(3)
    print(f"{i} - consumed !")
    semaphore.release()


async def consumer(receive_channel: trio.MemoryReceiveChannel) -> str:
    semaphore = trio.Semaphore(PAR)
    async with trio.open_nursery() as nursery:
        async with receive_channel:
            async for i in receive_channel:
                await semaphore.acquire()
                nursery.start_soon(consume, i, semaphore)


async def main() -> None:
    async with trio.open_nursery() as nursery:
        send_channel, receive_channel = trio.open_memory_channel(9999)
        nursery.start_soon(producer, send_channel)
        await trio.sleep(0.1)
        nursery.start_soon(consumer, receive_channel)

    print("ALL DONE")


trio.run(main)
