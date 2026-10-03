from datetime import datetime


def get_time():

    return datetime.now().strftime(
        "%H:%M"
    )



def get_date():

    return datetime.now().strftime(
        "%A %d de %B"
    )
