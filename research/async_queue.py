import asyncio

q = asyncio.Queue(maxsize=512)


async def produce():
    for i in range(10):
        await asyncio.sleep(1)
        await q.put(i)
        print("put", i)
    await q.put(None)  # indicate the end of the stream


async def consume():
    while True:
        item = await q.get()
        if item is None:
            break
        print("get", item)
        q.task_done()


async def main():
    q = asyncio.Queue(maxsize=512)
    await q.put("hello")
    await q.put("world")
    # for _ in range(4):
    #     if not q.empty():
    #         item = await q.get()
    #         print(item)
    #     else:
    #         print("Queue is empty")
    res = None
    while not res:
        try:
            res = await asyncio.wait_for(q.get(), timeout=10)
            if res:
                print(res)
        except asyncio.TimeoutError:
            print("Queue is empty")


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
