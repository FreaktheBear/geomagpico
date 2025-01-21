import asyncio
import math
import utime
import gc
from machine import Pin, UART, RTC
from geomag import GeoMag


# ---------------- Global Variable Declaration ------------------ ��
g_my_latitude = 0.0
g_my_longitude = 0.0
g_my_altitude = 0.0
g_my_magn_dec = 0.0
g_alt_correction = 0.0
g_azimuth = "_"
g_altitude = "_"
g_fix_status = False


# ---------------- Async: Read Serial Data from GPS ------------------
async def read_gpsrmc():

    global g_my_latitude, g_my_longitude, g_my_altitude, g_fix_status, g_my_magn_dec
    gps_input= UART(1,baudrate=9600, tx=Pin(4), rx=Pin(5))
    print(gps_input)

    FIX_STATUS = False

    #Store GPS Coordinates
    latitude = None
    longitude = None
    altitude = None
    t_datetime = None
    buff = None

    #Function to convert raw Latitude and Longitude to actual Latitude and Longitude
    def convertToDegree(RawDegrees):

        RawAsFloat = float(RawDegrees)
        firstdigits = int(RawAsFloat/100) #degrees
        nexttwodigits = RawAsFloat - float(firstdigits*100) #minutes
        
        Converted = float(firstdigits + nexttwodigits/60.0)
        Converted = '{0:.6f}'.format(Converted) # to 6 decimal places
        #return str(Converted)
        return Converted
    
    def days_between(d0, d1):
        d0 += (1, 0, 0, 0, 0)  # ensure a time past midnight
        d1 += (1, 0, 0, 0, 0)
        return utime.mktime(d1) // (24*3600) - utime.mktime(d0) // (24*3600)

    while True:
        while FIX_STATUS == False:
            print("Waiting for GPS data")
            while True:
                buff = str(gps_input.readline())
                if buff is not None :
                    break
            parts = buff.split(',')
            print(buff)
            if (parts[0] == "b'$GPRMC" and len(parts) == 13 and parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6]):
                print("Message ID  : " + parts[0])
                print("UTC time    : " + parts[1])
                print("Pos. Status : " + parts[2])
                print("Latitude    : " + parts[3])
                print("N/S         : " + parts[4])
                print("Longitude   : " + parts[5])
                print("E/W         : " + parts[6])
                latitude = convertToDegree(parts[3])
                if (parts[4] == 'S'):
                    latitude = -float(latitude)
                else:
                    latitude = float(latitude)
                longitude = convertToDegree(parts[5])
                if (parts[6] == 'W'):
                    longitude = -float(longitude)
                else:
                    longitude = float(longitude)
                if (parts[2] == 'A'):                    # Test if GPS data is valid
                    print(latitude)
                    print(longitude)
                    g_my_latitude = latitude
                    g_my_longitude = longitude
                    FIX_STATUS = True
                    g_fix_status = True

                    year = int('20'+parts[9][4:6])      # create RTC set datetime variables
                    month = int(parts[9][2:4])
                    day = int(parts[9][0:2])
                    hours = int(parts[1][0:2])
                    minutes = int(parts[1][2:4])
                    seconds = int(parts[1][4:6])
                    t_datetime = (year, month, day, 0, hours, minutes, seconds, 0)  #(year, month, day, weekday, hours, minutes, seconds, subseconds)
                    rtc = RTC()
                    rtc.datetime(t_datetime)
                    now = rtc.datetime()
                    print(now)

                    d0 = (now[0], 1, 1)                 # calculate current year + decimal days to use for pygeomag function
                    d1 = (now[0:3])
                    days_dec = '{:.2f}'.format(days_between(d0, d1)/365)
                    time_dec = float(now[0])+float(days_dec)
                    print(time_dec)

                    geo_mag = GeoMag(coefficients_file="wmm/WMM_2025.COF")              # calculate magnetic declination and convert to degrees-minutes
                    result = geo_mag.calculate(glat=latitude, glon=longitude, alt=0, time=time_dec)
                    print(result.d)
                    decimal , degrees = math.modf(result.d)
                    dec_minutes = round(decimal*60, 0)
                    g_my_magn_dec = (int(degrees), int(dec_minutes))
                    print(g_my_magn_dec)
                    break
                else:
                    print('No GPS fix')
            
            await asyncio.sleep(0.25)
        await asyncio.sleep(0.25)


# ---------------- Main Program Loop ------------------
async def main():
    asyncio.create_task(read_gpsrmc())

    while True:
        try:
            print("Main program running")
            gc.collect()
            #print(gc.mem_free())
        except OSError as e:
            print('Main error')
        await asyncio.sleep(0.5)   # Sleep for 500 milli seconds

try:
    asyncio.run(main())  # Run the main asynchronous function
except OSError as e:
    print('Runtime error')
finally:
    asyncio.new_event_loop() #Create a new event loop