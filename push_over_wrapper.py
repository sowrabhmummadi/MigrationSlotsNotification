import requests
import logging
from decouple import config


def send_notification(data: str):
    logger = logging.getLogger("root")
    r = requests.post("https://api.pushover.net/1/messages.json", data={
        "token": config('pushover_token', default=''),
        "user": config('pushover_user_key', default=''),
        "message": data
    })
    logger.debug(r.text)
