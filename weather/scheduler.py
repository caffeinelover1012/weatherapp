from apscheduler.schedulers.background import BackgroundScheduler
from .utils import update_affected_zips

def start():
    update_affected_zips()
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_affected_zips, 'interval', hours=6)
    scheduler.start()
