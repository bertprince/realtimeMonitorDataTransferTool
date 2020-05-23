# -*- coding:utf-8 -*-
import csv
from datetime import datetime, timedelta


def runTask(func, day=0, hour=0, min=0, second=0):
    # Init time
    now = datetime.now()
    strnow = now.strftime('%Y-%m-%d %H-%M-%S')
    print
    "now:", strnow
    # First next run time
    period = timedelta(days=day, hours=hour, minutes=min, seconds=second)
    next_time = now + period
    strnext_time = next_time.strftime('%Y-%m-%d %H-%M-%S')
    print
    "next run:", strnext_time
    while True:
        # Get system current time
        iter_now = datetime.now()
        iter_now_time = iter_now.strftime('%Y-%m-%d %H-%M-%S')
        if str(iter_now_time) == str(strnext_time):
            # Get every start work time
            print
            "start work: %s" % iter_now_time
            # Call task func
            func()
            print
            "task done."
            # Get next iteration time
            iter_time = iter_now + period
            strnext_time = iter_time.strftime('%Y-%m-%d %H-%M-%S')
            print
            "next_iter: %s" % strnext_time
            # Continue next iteration
            continue
def create_csv():
    name = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    path = "./server/"+ name +".csv"
    with open(path, 'wb') as f:
        csv_write = csv.writer(f)
        csv_head = ["good", "bad"]
        csv_write.writerow(csv_head)
    print("creat %s" % name)

runTask(create_csv,second=5)