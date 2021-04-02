from datetime import datetime
from datetime import timedelta
import logging
from logging.config import fileConfig

import requests

from Periodic import periodic_func
from push_over_wrapper import send_notification
from decouple import config


class SlotsManager:
    duration: int = 900
    main_url = "https://www.migrationsverket.se"
    booking_url = 'https://www.migrationsverket.se/ansokanbokning/valjtyp'

    def __init__(self, args: "Program Arguments") -> None:
        self.logger = logging.getLogger('simpleExample')
        fileConfig('logging.conf')

        self.slot_url = 'https://www.migrationsverket.se/ansokanbokning/wicket/page'
        self.args = args
        self.duration = args.duration
        self.lang = args.lang
        self.no_of_slots = args.no_of_slots
        self.start_time = args.start_time
        self.end_time = args.end_time
        self.session = None
        self.data = {}

    @periodic_func(duration)
    def update_data(self):
        self._update_session()
        free_slots_param = {'1-1.IBehaviorListener.1-form-kalender-kalender': '',
                            'start': self.start_time.isoformat(),
                            'end': self.end_time.isoformat()}
        self.logger.debug(f"sending GET request to {self.slot_url} with params: {free_slots_param}")
        response = self.session.get(self.slot_url, params=free_slots_param)
        self.logger.info(f"matched slots {len(response.json())}")
        notification_data = []
        for entry in response.json():
            if entry['start'] not in self.data:
                self.data[entry['start']] = entry
                notification_data.append(entry['start'])

        if len(notification_data):
            slots = '\n'.join(notification_data[:3])
            message = f"""New slots available 
From :  {self.start_time.ctime()} 
To   :  {self.end_time.ctime()}
Slots:  
{slots}"""
            send_notification(message)
        else:
            self.logger.info("No New Slots")

    def _update_session(self):
        self.logger.info("resetting the  deadline and creating a new session")
        self._close_and_create_new_session()
        self._update_main_session_cookie()
        self._update_booking_session_cookie()


    def _close_and_create_new_session(self):
        if self.session:
            self.logger.debug("closing current session")
            self.session.close()
        self.session = requests.session()
        self.logger.debug("new session is created")

    def _update_main_session_cookie(self):
        self.logger.info("updating the main cookie")
        self.logger.debug(f"sending GET request to {self.main_url}")
        main_response = self.session.get(self.main_url)
        self.logger.debug(f"new cookie:{main_response.cookies}")

    def _update_booking_session_cookie(self):
        self.logger.info("updating the booking cookie")
        booking_params = {'spark': self.lang, 'bokningstyp': '2', 'enhet': 'Z102', 'sokande': self.no_of_slots}
        self.logger.debug(f"sending GET request to {self.booking_url} with params: {booking_params}")
        booking_response = self.session.get(self.booking_url, params=booking_params)
        self.logger.debug(f"new cookie:{booking_response.cookies}")
