import logging

class LogController(object):
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        handlers=[
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.disabled = True

    def info(msg: str) -> None:
        LogController.logger.info(msg)

    def debug(msg: str) -> None:
        LogController.logger.debug(msg)

    def warning(msg: str) -> None:
        LogController.logger.warning(msg)

    def error(msg: str) -> None:
        LogController.logger.error(msg)
