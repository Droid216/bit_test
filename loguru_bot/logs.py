from loguru import logger

logger.add("./loguru_bot/filelog/logbot.log",
           format="{time:YYYY-MM-DD at HH:mm:ss}  {level}  {message}",
           level='INFO',
           rotation="1 week",
           backtrace=False,
           compression="zip")

logger.add("./loguru_bot/filelog/errbot.log",
           format="{time:YYYY-MM-DD at HH:mm:ss}  {level}  {message}",
           level="ERROR",
           catch=True,
           rotation="1 week",
           compression="zip")
