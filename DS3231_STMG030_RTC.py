import os
import time

from datetime import datetime
from sys import argv

import SDL_DS3231
from smbus2 import SMBus, i2c_msg


class RpiRTCController:
    COMAND_SET_DATETIME_OS = (
        'sudo date --set "{0}{1:0=2d}{2:0=2d} {3}:{4}:{5}"'
    )
    ADDR_DS3231 = 0x68
    ADDR_STMG030 = 0x20
    DEFAULT_DILAY_SEC = 1
    BUFFER_SIZE = 6

    def init_rtc_ds3231(self):

        return SDL_DS3231.SDL_DS3231(
            twi=1,
            addr=self.ADDR_DS3231
        )

    def str_to_hexstr_to_int(self, sq):
        result = []
        for param in sq[1:]:
            if len(param) > 2:
                param = param[2:]

            result.append(int('0x' + param, 16))
        return result

    def get_datetime_ds3231(self):
        rtc_device = self.init_rtc_ds3231()

        time.sleep(self.DEFAULT_DILAY_SEC)

        try:
            rtc = rtc_device.read_datetime()
        except Exception:
            print("Модуль не обнаружен")
            return None

        return [rtc.hour,
                rtc.minute,
                rtc.second,
                rtc.day,
                rtc.month,
                rtc.year]

    def get_datetime_stmg030(self):
        with SMBus(1) as bus:
            data = i2c_msg.read(self.ADDR_STMG030,
                                self.BUFFER_SIZE)
            bus.i2c_rdwr(data)
            return list(data)

    def set_datetime_ds3231(self, argv):

        rtc_device = self.init_rtc_ds3231()
        target, arg_year, arg_month, arg_day, arg_h, arg_m, arg_s = argv

        # set the time.
        try:
            rtc_device.write_datetime(
                datetime(
                    year=int(arg_year),
                    month=int(arg_month),
                    day=int(arg_day),
                    hour=int(arg_h),
                    minute=int(arg_m),
                    second=int(arg_s)
                )
            )
            return True
        except Exception:
            return None

    def set_datetime_stmg030(self, argv):

        date_params = self.str_to_hexstr_to_int(argv)
        arg_year, arg_month, arg_day, arg_h, arg_m, arg_s = date_params

        with SMBus(1) as bus:
            msg = i2c_msg.write(self.ADDR_STMG030, [
                arg_h,
                arg_m,
                arg_s,
                arg_day,
                arg_month,
                arg_year,
            ])
            bus.i2c_rdwr(msg)

    def set_datetime_os(self, datetime_params):
        hour, minute, second, day, month, year = datetime_params
        os.system(
            self.COMAND_SET_DATETIME_OS.format(
                year, month,
                day, hour,
                minute, second
            )
        )


def read_rtc(controller):
    datatime_params = controller.get_datetime_ds3231()
    if not datatime_params:
        datatime_params = controller.get_datetime_stmg030()
    return datatime_params


def write_rtc(argv, controller):

    if not controller.set_datetime_ds3231(argv):
        controller.set_datetime_stmg030(argv)
    return read_rtc(controller)


def main(argv):
    controller = RpiRTCController()
    datatime_params = []

    if len(argv) > 1:
        datatime_params = write_rtc(argv, controller)
    else:
        datatime_params = read_rtc(controller)

    try:
        controller.set_datetime_os(datatime_params)
    except ValueError:
        print("Oops! That was no valid list.")


if __name__ == "__main__":
    main(argv)
