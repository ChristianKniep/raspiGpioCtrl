#!env python
"""
Library to calculate the sunset
Written by Michel Anders
http://michelanders.blogspot.fr/2010/12/<br>
        calulating-sunrise-and-sunset-in-python.html
"""

from math import cos, sin, acos, asin, tan
from math import degrees as deg, radians as rad
from datetime import datetime, time


class SunRise:
    """
    Calculate sunrise and sunset based on equations from NOAA
    http://www.srrb.noaa.gov/highlights/sunrise/calcdetails.html
    typical use, calculating the sunrise at the present day:

    import datetime
    import sunrise
    s = sun(lat=49,long=3)
    print('sunrise at ',s.sunrise(when=datetime.datetime.now())
    """
    def __init__(self, lat=52.8948846, lon=10.4468234):
        """
        Instanciate class, by default set Suderburg, Germany as base
        """
        self.coord = (lat, lon)
        self.day = None
        self.time = None
        self.timezone = None

    def sunrise(self, when=datetime.now()):
        """
        return the time of sunrise as a datetime.time object
        when is a datetime.datetime object. If none is given
        a local time zone is assumed (including daylight saving
        if present)
        """
        if when is None:
            when = datetime.now()
        self.__preptime(when)
        self.__calc()
        return SunRise.__timefromdecimalday(self.sunrise_t)

    def sunset(self, when=None):
        """
        returns datetime when sun will set
        """
        if when is None:
            when = datetime.now()
        self.__preptime(when)
        self.__calc()
        return SunRise.__timefromdecimalday(self.sunset_t)

    def solarnoon(self, when=None):
        """
        datetime of solar noon
        """
        if when is None:
            when = datetime.now()
        self.__preptime(when)
        self.__calc()
        return SunRise.__timefromdecimalday(self.solarnoon_t)

    @staticmethod
    def __timefromdecimalday(day):
        """
        returns a datetime.time object.
        day is a decimal day between 0.0 and 1.0, e.g. noon = 0.5
        """
        hours = 24.0 * day
        hour = int(hours)
        minutes = (hours - hour) * 60
        minute = int(minutes)
        seconds = (minutes - minute) * 60
        second = int(seconds)
        res = time(hour=hour, minute=minute, second=second)
        return res

    def __preptime(self, when):
        """
        Extract information in a suitable format from when,
        a datetime.datetime object.
        """
        # datetime days are numbered in the Gregorian calendar
        # while the calculations from NOAA are distibuted as
        # OpenOffice spreadsheets with days numbered from
        # 1/1/1900. The difference are those numbers taken for
        # 18/12/2010
        self.day = when.toordinal() - (734124 - 40529)
        wtime = when.time()
        self.time = (wtime.hour + wtime.minute/60.0 + wtime.second/3600.0) / 24.0

        self.timezone += 2  # Is this right?
        offset = when.utcoffset()
        if not offset is None:
            self.timezone = offset.seconds / 3600.0

    def __calc(self):
        """
        Perform the actual calculations for sunrise, sunset and
        a number of related quantities.
        The results are stored in the instance variables
        sunrise_t, sunset_t and solarnoon_t
        """
        # in hours, east is positive
        timezone = self.timezone
        latitude = self.coord[0]
        longitude = self.coord[1]

        # percentage past midnight, i.e. noon  is 0.5
        some_time = self.time
        # daynumber 1=1/1/1900
        some_day = self.day

        # Julian day
        jday = some_day + 2415018.5 + some_time - (timezone / 24)
        # Julian jentury
        jcent = (jday - 2451545) / 36525

        Manom = 357.52911 + jcent * (35999.05029 - 0.0001537 * jcent)
        Mlong = 280.46646 + jcent * (36000.76983 + jcent * 0.0003032) % 360
        Eccent = 0.016708634 - jcent * (0.000042037 + 0.0001537 * jcent)
        Mobliq = 23 + (26 + ((21.448 - jcent * (46.815 + jcent * (0.00059 - jcent * 0.001813)))) / 60) / 60
        obliq = Mobliq + 0.00256 * cos(rad(125.04 - 1934.136 * jcent))
        vary = tan(rad(obliq / 2)) * tan(rad(obliq / 2))
        Seqcent = sin(rad(Manom)) * (1.914602 - jcent * (0.004817 + 0.000014 * jcent)) + sin(rad(2 * Manom)) * (0.019993 - 0.000101 * jcent) + sin(rad(3 * Manom)) * 0.000289
        Struelong = Mlong + Seqcent
        Sapplong = Struelong - 0.00569-0.00478 * sin(rad(125.04 - (1934.136 * jcent)))
        declination = deg(asin(sin(rad(obliq)) * sin(rad(Sapplong))))

        eqtime = 4 * deg(vary * sin(2 * rad(Mlong)) - 2 * Eccent * sin(rad(Manom)) + 4 * Eccent * vary * sin(rad(Manom)) * cos(2 * rad(Mlong)) - 0.5 * vary * vary * sin(4 * rad(Mlong)) - 1.25 * Eccent * Eccent * sin(2 * rad(Manom)))

        hourangle= deg(acos(cos(rad(90.833)) / (cos(rad(latitude)) * cos(rad(declination))) - tan(rad(latitude)) * tan(rad(declination))))

        self.solarnoon_t = (720 - 4 * longitude - eqtime + timezone * 60) / 1440
        self.sunrise_t = self.solarnoon_t-hourangle * 4 / 1440
        self.sunset_t = self.solarnoon_t+hourangle * 4 / 1440

if __name__ == "__main__":
    #s=sun(lat=52.37,long=4.90) #amsterdam
    sun = SunRise()
    print(sun.sunrise(),sun.solarnoon(),sun.sunset())

