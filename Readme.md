# GeoMagPico
This repository is an adaptions of the following existing pygeomag github repository https://github.com/boxpet/pygeomag.
So all credits go to Justin Myers for his extensive contributions.
It calculates the magnetic declination for a given set of parameters (location and time).

## Chances
For this adaption I made a few changes in the geomag.py code in absence of some Micropython functionality for the Pi Pico.

1) Replaced datetime with RTC.datetime
2) Added the typing.py file

Please let me know if you have any comments as we are all here to learn.

## Examples
I have added two examples for the usage of this adaption on the Pi Pico.

1) basic_example.py sets the RTC datetime and uses the datime tuple and year + decimal days to calculate the magnetic declination and return a tuple with degrees minutes.
2) gps_example.py sets the RTC datetime from a NEO-7M GPS https://www.u-blox.com/en/product/neo-7-series (via serial) and calculates the magnetic declination with the current location and UTC time. It runs in a asyncio setup just because I really like this approach of programming. Simply rename to main.py and add your own "subroutines". See the following documentation for more info on Micropython's asyncio https://github.com/peterhinch/micropython-async 


