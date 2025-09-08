from datetime import datetime
import zoneinfo

def to_iso8601(year,month,day,hour,minute,second,tz_name):
    tz=zoneinfo.ZoneInfo(tz_name)
    dt=datetime(year,month,day,hour,minute,second,tzinfo=tz)
    return dt.isoformat()