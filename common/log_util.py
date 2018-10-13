import datetime

def print_log(str):
    print("%s: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str))
