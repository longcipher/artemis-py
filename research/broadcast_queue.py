import asyncio


class BroadcastQueue:
    def __init__(self):
        self.subscribers = set()
        self.queue = asyncio.Queue()

    async def subscribe(self):
        subscriber = asyncio.Queue()
        self.subscribers.add(subscriber)
        return subscriber

    async def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)

    async def publish(self, message):
        await self.queue.put(message)
        for subscriber in self.subscribers:
            await subscriber.put(message)

    async def get(self):
        return await self.queue.get()


async def consumer(name, queue):
    while True:
        message = await queue.get()
        if message == "exit":
            break
        print(f"{name} received message: {message}")


async def main():
    broadcast_queue = BroadcastQueue()

    consumers = ["Consumer-1", "Consumer-2", "Consumer-3"]

    # 启动多个消费者任务
    consumer_tasks = [
        asyncio.create_task(consumer(name, await broadcast_queue.subscribe()))
        for name in consumers
    ]

    # 发布多条消息
    await broadcast_queue.publish("Hello, World!")
    await broadcast_queue.publish("Message 1")
    await broadcast_queue.publish("Message 2")

    # 等待消费者任务完成
    for _ in range(len(consumers)):
        await broadcast_queue.publish("exit")  # 退出信号

    # 等待订阅者队列关闭
    await asyncio.gather(
        *(
            broadcast_queue.unsubscribe(subscriber)
            for subscriber in broadcast_queue.subscribers
        )
    )

    # 等待消费者任务完成
    await asyncio.gather(*consumer_tasks)


if __name__ == "__main__":
    asyncio.run(main())
