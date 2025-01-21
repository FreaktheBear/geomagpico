import utime
import math
from machine import RTC
from geomag import GeoMag

# Credits for this function go to Peter Hinch
def days_between(d0, d1):           
        d0 += (1, 0, 0, 0, 0)       # ensure a time past midnight
        d1 += (1, 0, 0, 0, 0)
        return utime.mktime(d1) // (24*3600) - utime.mktime(d0) // (24*3600)

latitude = -36.848461           # Auckland latitude
longitude = 174.763336          # Auckland longitude

# create RTC set datetime variables
t_datetime = (2025, 1, 21, 0, 12, 0, 0, 0)  #(year, month, day, weekday, hours, minutes, seconds, subseconds)
rtc = RTC()
rtc.datetime(t_datetime)
now = rtc.datetime()
print(now)

# calculate current year + decimal days to use for geomag function
d0 = (now[0], 1, 1)                 
d1 = (now[0:3])
days_dec = '{:.2f}'.format(days_between(d0, d1)/365)
time_dec = float(now[0])+float(days_dec)
print(time_dec)

# calculate magnetic declination and convert to degrees-minutes
geo_mag = GeoMag(coefficients_file="wmm/WMM_2025.COF")              
result = geo_mag.calculate(glat=latitude, glon=longitude, alt=0, time=time_dec)
print(result.d)
decimal , degrees = math.modf(result.d)
dec_minutes = round(decimal*60, 0)
my_magn_dec = (int(degrees), int(dec_minutes))
print(my_magn_dec)