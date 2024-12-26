import asyncio
import logging

from autogen_core import EVENT_LOGGER_NAME
from autogen_magentic_one.utils import LogHandler

from dynamic_taskgraph.task import Task


async def main():
    test_task = Task()  # TODO: TaskGraph
    await test_task.start()


if __name__ == "__main__":
    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_handler = LogHandler()
    logger.handlers = [log_handler]
    asyncio.run(main())
