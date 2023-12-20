from sys import argv

from DS3231_STMG030_RTC import RpiRTCController, write_rtc

controller = RpiRTCController()
datatime_params = write_rtc(argv, controller)
try:
    controller.set_datetime_os(datatime_params)
except ValueError:
    print("Oops! That was no valid list.")
