import asyncio


async def main():
    q = asyncio.Queue(maxsize=512)
    await q.put("hello")
    await q.put("world")
    for _ in range(4):
        if not q.empty():
            item = await q.get()
            print(item)
        else:
            print("Queue is empty")


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
