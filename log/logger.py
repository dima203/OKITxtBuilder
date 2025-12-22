from loguru import logger


logger.add("logger.log", rotation="5 MB")
