import logging

from aiohttp import web

from .handlers.health import health_check

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def web_app(port):
    app = web.Application()
    app.add_routes(
        [
            web.get("/health", health_check),
        ]
    )
    logger.info("port: %s", port)
    return app


async def run_web(port):
    app = web_app(port)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
