# Artemis-PY Framework Architecture

Artemis-PY is a real-time async event-driven trading framework that provides a flexible architecture for building trading bots and automated strategies.

## Core Concepts

### Component Types

The framework consists of three main component types that work together:

1. **Collectors** - Responsible for gathering data from various sources
2. **Strategies** - Process events and generate trading decisions  
3. **Executors** - Execute actions on external systems

### Data Flow

```
External Sources → Collectors → Events → Strategies → Actions → Executors → External Systems
```

Data flows through the system using async queues:

1. Collectors gather data from external sources (REST APIs, WebSockets, databases, etc.)
2. Events are queued and consumed by strategies
3. Strategies analyze events and generate actions
4. Actions are queued and consumed by executors
5. Executors perform the actual operations (place orders, send notifications, etc.)

## Architecture Components

### Engine

The `Engine` class is the central coordinator that:

- Manages the lifecycle of all components
- Orchestrates communication between components via async queues
- Provides error isolation between components
- Handles graceful startup and shutdown

### Event Queue

- **Capacity**: Configurable (default: 512 events)
- **Producer**: Collectors push events
- **Consumer**: Strategies pull events
- **Processing**: FIFO (First In, First Out)

### Action Queue

- **Capacity**: Configurable (default: 512 actions)  
- **Producer**: Strategies push actions
- **Consumer**: Executors pull actions
- **Processing**: FIFO (First In, First Out)

## Component Lifecycle

### Startup Sequence

1. Engine initializes async queues
2. Components are registered with the engine
3. Engine starts collector, strategy, and executor loops concurrently
4. Each component type syncs its state before processing
5. Main processing loops begin

### Processing Loops

#### Collector Loop
```python
for each collector:
    collector.start()
    
while running:
    for each collector:
        event = await collector.get_event_stream()
        if event:
            await event_queue.put(event)
    await asyncio.sleep(0.1)
```

#### Strategy Loop  
```python
for each strategy:
    await strategy.sync_state()
    
while running:
    if event_queue.not_empty():
        event = await event_queue.get()
        for each strategy:
            action = await strategy.process_event(event)
            if action:
                await action_queue.put(action)
    await asyncio.sleep(0.1)
```

#### Executor Loop
```python
for each executor:
    await executor.sync_state()
    
while running:
    if action_queue.not_empty():
        action = await action_queue.get()  
        for each executor:
            await executor.execute(action)
    await asyncio.sleep(0.1)
```

### Shutdown Sequence

1. Engine receives shutdown signal
2. All component tasks are cancelled
3. Components perform cleanup if needed
4. Queues are drained
5. Engine shuts down gracefully

## Error Handling

- **Component Isolation**: Exceptions in one component don't affect others
- **Graceful Degradation**: Failed components are logged but don't stop the engine
- **Retry Logic**: Components can implement their own retry mechanisms
- **Circuit Breakers**: Can be implemented at the component level

## Concurrency Model

- **Event Loop**: Single asyncio event loop manages all components
- **Parallelism**: Components run concurrently using asyncio tasks
- **Queue-based**: Communication is asynchronous via queues
- **Non-blocking**: All operations are async/await based

## Performance Characteristics

- **Throughput**: Limited by queue capacity and component processing speed
- **Latency**: Minimal overhead from queue operations (~microseconds)
- **Memory**: Queue capacity determines memory usage for buffering
- **CPU**: Efficient async processing with minimal context switching

## Scalability Considerations

### Horizontal Scaling
- Deploy multiple instances with different responsibilities
- Use external message queues (Redis, RabbitMQ) for inter-process communication
- Implement sharding strategies for data collection

### Vertical Scaling  
- Increase queue capacities for higher throughput
- Add more collectors/strategies/executors per engine
- Optimize component processing logic

### Monitoring
- Built-in structured logging with configurable levels
- Health check endpoints for monitoring system status
- Metrics can be added at the component level

## Best Practices

### Component Design
- Keep components stateless where possible
- Implement proper error handling and logging
- Use connection pooling for external resources
- Implement graceful shutdown handling

### Performance Optimization
- Batch operations where possible
- Use appropriate queue sizes based on throughput requirements
- Monitor queue depths to identify bottlenecks
- Implement backpressure mechanisms if needed

### Testing
- Unit test each component independently
- Integration test complete workflows
- Load test with realistic data volumes
- Test error conditions and recovery scenarios
