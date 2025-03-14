from apscheduler.schedulers.background import BackgroundScheduler


appointment_scheduler = BackgroundScheduler()
# appointment_scheduler.add_job(   
#     id='send mails',
#     func=lambda: print('123'),
#     trigger='interval',
#     seconds=5,
# )
