# Examples

This directory contains example implementations demonstrating how to use the Artemis framework.

## Simple Example

A basic example showing the core concepts:

```bash
# From the project root
python examples/simple_example.py
```

This example demonstrates:
- **MockPriceCollector**: Generates simulated price events
- **PriceChangeStrategy**: Detects significant price movements  
- **AlertExecutor**: Logs alerts when conditions are met

## Orderly Liquidation Searcher

A complete real-world example showing how to build a liquidation searcher:

```bash
# Navigate to the example directory
cd examples/orderly_liquidation_searcher

# Set up environment variables
export ORDERLY_KEY="your_orderly_key"
export ORDERLY_SECRET="your_orderly_secret"

# Run the example (requires orderly-sdk)
uv pip install orderly-sdk>=0.2.2
python main.py -c ../../conf/staging.yml
```

This example shows:
- **REST and WebSocket Collectors**: Real-time data from Orderly Network
- **Liquidation Strategy**: Identifies profitable liquidation opportunities
- **Exchange Executor**: Executes trades on Orderly

**⚠️ WARNING: The liquidation searcher is not fully tested! Use at your own risk with small amounts first.**

## Creating Your Own Example

1. Create a new directory: `examples/my_example/`
2. Implement your collectors, strategies, and executors
3. Create a main.py file to set up and run the engine
4. Add any configuration files needed
5. Document your example in a README.md

### Basic Template

```python
import asyncio
from artemis import Engine, Collector, Strategy, Executor

# Your custom components
class MyCollector(Collector):
    # Implementation here
    pass

class MyStrategy(Strategy):
    # Implementation here  
    pass

class MyExecutor(Executor):
    # Implementation here
    pass

# Set up and run
async def main():
    engine = Engine()
    engine.add_collector(MyCollector())
    engine.add_strategy(MyStrategy()) 
    engine.add_executor(MyExecutor())
    await engine.run()

if __name__ == "__main__":
    asyncio.run(main())
```
