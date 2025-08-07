# Artemis-PY

A real-time async event-driven trading framework inspired by [paradigmxyz/artemis](https://github.com/paradigmxyz/artemis).

Artemis-PY provides a flexible, extensible architecture for building trading bots and strategies. The framework is built around three core components:

- **Collectors**: Gather data from various sources (REST APIs, WebSocket feeds, databases, etc.)
- **Strategies**: Process events and generate trading actions based on custom logic
- **Executors**: Execute the generated actions on exchanges or other external systems

## Features

- **Event-driven Architecture**: Asynchronous processing with asyncio queues
- **Modular Design**: Easy to extend with custom collectors, strategies, and executors
- **Concurrent Processing**: All components run concurrently for maximum performance
- **Error Isolation**: Exceptions in one component don't affect others
- **Comprehensive Logging**: Built-in structured logging with configurable levels

## Architecture

```
┌─────────────┐    Events    ┌─────────────┐    Actions   ┌─────────────┐
│ Collectors  │─────────────→│ Strategies  │─────────────→│ Executors   │
├─────────────┤              ├─────────────┤              ├─────────────┤
│ REST APIs   │              │ Arbitrage   │              │ Exchange    │
│ WebSocket   │              │ Market      │              │ Orders      │
│ Databases   │              │ Making      │              │ Database    │
│ Files       │              │ Technical   │              │ Writes      │
│ ...         │              │ Analysis    │              │ Webhooks    │
└─────────────┘              │ ...         │              │ ...         │
                             └─────────────┘              └─────────────┘
```

The engine coordinates all components using async queues:
1. Collectors push events to the event queue
2. Strategies consume events and push actions to the action queue  
3. Executors consume and execute actions

## Installation

```bash
# Install the framework
pip install uv
uv venv .venv
source .venv/bin/activate
uv pip install -e .

# For development
uv pip install -e ".[dev]"

# For running examples 
uv pip install -e ".[examples]"
```

## Source code structure

```
/src/artemis/                     - Core framework code
  ├── __init__.py                 - Framework API exports
  ├── types.py                    - Base classes and interfaces
  ├── engine/                     - Engine implementation
  └── utils/                      - Utility functions
/examples/                        - Example implementations
  └── orderly_liquidation_searcher/ - Liquidation searcher example
/docs/                            - Documentation
/conf/                            - Configuration files for examples
/deployment/                      - Deployment configurations
```

## Quick Start

### Basic Usage

```python
import asyncio
from artemis import Engine, Collector, Strategy, Executor

# Create your custom components
class MyCollector(Collector):
    def start(self, timeout=None):
        # Start collecting data
        pass
    
    async def get_event_stream(self):
        # Return collected events
        return {"event_type": "my_event", "data": "..."}

class MyStrategy(Strategy):
    async def sync_state(self):
        # Initialize strategy state
        pass
    
    async def process_event(self, event):
        # Process event and return action
        return {"action_type": "my_action", "data": "..."}

class MyExecutor(Executor):
    async def sync_state(self):
        # Initialize executor state  
        pass
    
    async def execute(self, action):
        # Execute the action
        print(f"Executing: {action}")

# Set up and run the engine
async def main():
    engine = Engine()
    engine.add_collector(MyCollector())
    engine.add_strategy(MyStrategy())
    engine.add_executor(MyExecutor())
    
    await engine.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Running Examples

The framework includes a complete example showing how to build a liquidation searcher for Orderly Network:

```bash
# Navigate to the example directory
cd examples/orderly_liquidation_searcher

# Set up environment variables
export ORDERLY_KEY="your_orderly_key"
export ORDERLY_SECRET="your_orderly_secret"

# Run the example
python main.py -c ../../conf/staging.yml
```

## Extending the Framework

### Creating Custom Collectors

```python
from artemis import Collector
import asyncio

class WebSocketCollector(Collector):
    def __init__(self, url):
        self.url = url
        self.queue = asyncio.Queue()
    
    def start(self, timeout=None):
        # Start WebSocket connection
        asyncio.create_task(self._connect())
    
    async def _connect(self):
        # WebSocket connection logic
        pass
    
    async def get_event_stream(self):
        if not self.queue.empty():
            return await self.queue.get()
        return None
```

### Creating Custom Strategies

```python
from artemis import Strategy

class ArbitrageStrategy(Strategy):
    async def sync_state(self):
        # Load market data, trading pairs, etc.
        pass
    
    async def process_event(self, event):
        if event["event_type"] == "price_update":
            # Check for arbitrage opportunities
            if self.detect_arbitrage(event):
                return {
                    "action_type": "place_order",
                    "symbol": event["symbol"],
                    "side": "buy",
                    "quantity": 100
                }
        return None
```

### Creating Custom Executors

```python
from artemis import Executor

class ExchangeExecutor(Executor):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
    
    async def sync_state(self):
        # Initialize exchange client, get account info
        pass
    
    async def execute(self, action):
        if action["action_type"] == "place_order":
            # Execute order on exchange
            await self.exchange_client.place_order(action)
```

## Example: Orderly Liquidation Searcher

The framework includes a complete example that demonstrates building a liquidation searcher for Orderly Network. This example shows:

- **REST and WebSocket Collectors**: Gather liquidation events from Orderly APIs
- **Hedge Strategy**: Identify profitable liquidation opportunities  
- **Exchange Executor**: Execute liquidation claims and hedge trades

**WARNING: This example bot is not fully tested! Use at Your Own Risk!**

## Configuration

Example configuration for the liquidation searcher:

```yaml
# conf/staging.yml
app:
  level: "INFO"
  port: 8088 # health check port

orderly:
  account_id: '' # your account id
  rest_endpoint: 'https://testnet-api-evm.orderly.org'
  ws_public_endpoint: 'wss://testnet-ws-evm.orderly.network/ws/stream/'
  max_notional: 1000 # max notional per liquidation claim
  liquidation_symbols: ['PERP_BTC_USDC', 'PERP_ETH_USDC', 'PERP_NEAR_USDC']
```

Environment variables:

```bash
export ORDERLY_KEY="your_api_key"
export ORDERLY_SECRET="your_api_secret"
```

## Development

```bash
# Clone the repository
git clone https://github.com/longcipher/artemis-py.git
cd artemis-py

# Set up development environment
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
python -m pytest

# Format code
ruff format

# Check types
mypy src/
```

## Deployment

### Systemd Service

Reference systemd unit file: [liquidation_searcher_dev.service](/deployment/liquidation_searcher_dev.service)

### Docker

Reference Dockerfile for containerized deployment: [Dockerfile](/Dockerfile)

### Kubernetes

The framework can be deployed to Kubernetes. Make sure to:
1. Set environment variables in ConfigMaps/Secrets
2. Configure health check endpoints
3. Set appropriate resource limits

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided "as is" without any warranties. Trading cryptocurrencies involves substantial risk and can result in significant financial losses. Users are responsible for their own trading decisions and should thoroughly test any strategies before deploying them with real funds.
