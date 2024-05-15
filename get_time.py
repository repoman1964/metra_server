import datetime
import pytz

def get_eastern_time():
    eastern = pytz.timezone('US/Eastern')
    eastern_time = datetime.datetime.now(eastern)
    return eastern_time.strftime('%-I:%M %p')


def get_day_of_week():
    # Get the current date
    current_date = datetime.datetime.now()
    # Get the day of the week
    day_of_week = current_date.strftime("%A")
    return day_of_week

print(get_eastern_time())
print(get_day_of_week())