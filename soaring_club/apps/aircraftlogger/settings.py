HOME_AIRPORT = 'LIDT'
DURATION_RATE = 2.5 #euro/cent
DURATION_TOW_RATE = 2.5 #euro/cent
DURATION_TST_RATE = 2.0 #euro/cent
DURATION_TMG_RATE = 0.85 #euro/cent
DURATION_TST_RATE = 2 #euro/cent
DATE_FORMAT_STRF ='%d/%m/%Y'
TIME_FORMAT_STRF ='%H:%M'
DATETIME_FORMAT_STRF = '%d/%m/%Y %H:%M'
DATE_FORMAT ='d/m/Y'
TIME_FORMAT ='H:i'
DATETIME_FORMAT = 'd/m/Y H:i'
DATE_INPUT_FORMATS = ('%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', '%d %b %Y', '%d %b, %Y', '%d %B %Y', '%d %B, %Y')
TIME_INPUT_FORMATS = ('%H:%M:%S', '%H:%M')
DATETIME_INPUT_FORMATS = ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y', '%d/%m/%y %H:%M:%S', '%d/%m/%y %H:%M', '%d/%m/%y')
ADMIN_GROUP = 'managers'
MIN_CREDIT = -5 #threshold for consider a Member in debit status
import datetime
MAX_DAYS_FROM_LAST_FLIGHT_CLUB = datetime.timedelta(60)
MAX_DAYS_FROM_LAST_FLIGHT_PRIVATE = datetime.timedelta(180)