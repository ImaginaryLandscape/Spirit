import logging
import datetime
from zoneinfo import available_timezones, ZoneInfo

__all__ = ['timezones']

logger = logging.getLogger('django')


def is_standard_time(time_zone, date_time):
    # Check if the time zone is in standard time (not DST)
    dst_delta = time_zone.dst(date_time)
    return dst_delta == datetime.timedelta(0)


def utc_offset(time_zone, fixed_dt=None):
    tz = ZoneInfo(time_zone)
    now = fixed_dt or datetime.datetime.now()

    # Loop to find the first date where DST is not in effect
    for __ in range(72):
        if is_standard_time(time_zone=tz, date_time=now):
            break
        now += datetime.timedelta(days=30)

    # Replace or adjust the naive datetime to be timezone-aware
    now = now.replace(tzinfo=tz)
    
    # Return the formatted timezone offset
    return now.strftime('%z')


def offset_to_int(offset):
    assert offset[0] in ('-', '+')

    sign, hour, minutes = offset[0], offset[1:3], offset[3:5]
    utc_offset_int = int(hour) + int(minutes) / 100

    if sign == '-':
        utc_offset_int *= -1

    return utc_offset_int


def timezones_by_offset():
    return sorted(
        ((utc_offset(tz), tz)
         for tz in available_timezones()),
        key=lambda x: (offset_to_int(x[0]), x[1]))


def timezone_format(time_zone, offset):
    zone_parts = time_zone.split('/')
    zone = zone_parts[0]

    if len(zone_parts) > 1:
        zone_label = ', '.join(zone_parts[1:]).replace('_', ' ')
    else:
        zone_label = zone

    return zone, f'(UTC{offset}) {zone_label}'


def timezones():
    """
    Result format::

        [
            ("Africa", [
                ("Africa/Abidjan", "(UTC...) Abidjan"),
                ("Africa/Accra", "(UTC...) Accra"),
                #...
            ]),
            ("America", [
                ("America/Argentina/Buenos_Aires",
                 "(UTC...) Argentina, Buenos Aires"),
                #...
            ]),
            #...
        ]
    """
    timezones_cache = {}

    for offset, time_zone in timezones_by_offset():
        zone, pretty_time_zone = timezone_format(time_zone, offset)
        timezones_cache.setdefault(zone, []).append((time_zone, pretty_time_zone))

    return sorted(timezones_cache.items(), key=lambda x: x[0])
