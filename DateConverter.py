from datetime import datetime, timedelta


class DateConverter():
    def __init__(self):
        pass

    @staticmethod
    def convert_date(fromtime):
        utc_offset = int(round((datetime.now() - datetime.utcnow()).total_seconds() / 3600))
        return (
            datetime.strptime(fromtime, '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=utc_offset)).strftime(
            '%A, %d.%m.%Y %H:%M:%S +0' + str(utc_offset) + '00')