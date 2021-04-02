import argparse
from datetime import datetime
from datetime import timedelta
from logging.config import fileConfig
import logging

import requests

from slots_manager import SlotsManager


def get_booking_json(args: "Program arguments"):
    s = requests.session()
    main_url = "https://www.migrationsverket.se"
    booking_url = 'https://www.migrationsverket.se/ansokanbokning/valjtyp'
    s.get(main_url)
    p = {'spark': args.lang, 'bokningstyp': '2', 'enhet': 'Z102', 'sokande': args.no_of_slots}
    s.get(booking_url, params=p)
    free_slots_param = {'1-1.IBehaviorListener.1-form-kalender-kalender': '', 'start': args.start_time.isoformat(),
                        'end': args.end_time.isoformat()}
    response = s.get('https://www.migrationsverket.se/ansokanbokning/wicket/page', params=free_slots_param)
    print(response.json())
    return response.json()


def parse_args():
    parser = argparse.ArgumentParser(description='Get Slots from Migrationsverket')
    parser.add_argument('lang', metavar='-l', type=str, nargs='?',
                        help='output language used for when debugging (only languages supported by Migrationsverket) ',
                        default="en")
    parser.add_argument('no_of_slots', metavar="-n", type=str, default='1', nargs='?',
                        help='number of slots you are willing to book')
    parser.add_argument('duration', metavar="-d", type=int, default=900, nargs='?',
                        help='Duration in seconds')
    parser.add_argument('start_time', metavar="-s", type=str, default=datetime.now(), nargs='?',
                        help='The Start Date - format YYYY-MM-DD')
    parser.add_argument('end_time', metavar="-e", type=datetime.date,
                        default=(datetime.now() + timedelta(days=94)),
                        nargs='?',
                        help='The End Date - format YYYY-MM-DD')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    fileConfig('logging.conf')
    logger = logging.getLogger("root")
    logger.debug(f"Arguments: {args}")
    slot_manager = SlotsManager(args)
    slot_manager.update_data()
