import json
import logging


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line_number": record.lineno,
        }

        # Include additional data from the log record, if available
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_data.update(record.extra_data)

        return json.dumps(log_data, ensure_ascii=False)


logger = logging.getLogger("tiingobot_logger")

logger.setLevel(logging.INFO)


# Create a file handler
fhandler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
fhandler.setFormatter(JsonFormatter())
fhandler.setLevel(logging.DEBUG)

# Create a stream handler
shandler = logging.StreamHandler()
shandler.setFormatter(JsonFormatter())
shandler.setLevel(logging.DEBUG)

# Add both handlers to the logger
logger.addHandler(fhandler)
logger.addHandler(shandler)
