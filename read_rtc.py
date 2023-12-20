from DS3231_STMG030_RTC import RpiRTCController, read_rtc

controller = RpiRTCController()
datatime_params = read_rtc(controller)
try:
    controller.set_datetime_os(datatime_params)
except ValueError:
    print("Oops! That was no valid list.")
