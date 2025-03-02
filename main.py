#!/usr/bin/python3

import lcddriver
import requests
import json
import re
import os

from time import sleep
from datetime import datetime
from datetime import timedelta

api_url = "http://localhost:80/api"
app_password = "xxxxxxxxxxxxxxxxxxxxxxxxx"
sid = ""

lcd = lcddriver.lcd(0x27)

def get_summary():
    r = requests.get(api_url + "/stats/summary?sid=" + sid)
    print(r.json())
    return r.json()

def check_api():
    r = requests.get(api_url + "/auth?sid=" + sid)
    check_response = r.json()
    auth_valid = check_response["session"]["valid"]
    return auth_valid

def authenticate():
    auth_request = json.dumps({"password": app_password})
    r = requests.post(api_url + "/auth", data=auth_request)
    auth_response = r.json()
    global sid
    sid = auth_response["session"]["sid"]
    print(auth_response)

while(True):
    # check if we are authenticated
    if not check_api():
        authenticate()

    # get version info
    versions = os.popen("pihole -v").read().split("\n")
    version_pihole_re = re.search("version\sis\s(.*?)\s\(Latest:\s(.*?)\)", versions[0])
    version_pihole_current = version_pihole_re.group(1)
    version_pihole_latest = version_pihole_re.group(2)
    if version_pihole_latest == "N/A":
        version_pihole_latest = version_pihole_current
    version_ftl_re = re.search("version\sis\s(.*?)\s\(Latest:\s(.*?)\)", versions[2])
    version_ftl_current = version_ftl_re.group(1)
    version_ftl_latest = version_ftl_re.group(2)
    if version_ftl_latest == "N/A":
        version_ftl_latest = version_ftl_current
    lcd.clear()
    lcd.display_line("PiHole " + version_pihole_current, 1, "c", 16)
    lcd.display_line("FTL " + version_ftl_current, 2, "c", 16)

    sleep(15)

    # should we display the update message?
    available_updates = []
    if version_pihole_current != version_pihole_latest:
        available_updates.append("PiHole")
    if version_ftl_current != version_ftl_latest:
        available_updates.append("FTL")
    if available_updates != []:
        update_line = " + ".join(available_updates)
        lcd.clear()
        lcd.display_line("Update avail", 1, "c", 16)
        lcd.display_line(update_line, 2, "c", 16)
        sleep(30)

    # get some sysinfo
    sysstats = os.popen("uptime").read()
    uptime = "Up: " + re.search("up\s(.*?)\,", sysstats).group(1)
    load = "Load: " + re.search("load\saverage:\s.*?,\s(.*?)\,", sysstats).group(1)

    lcd.clear()
    lcd.display_line(uptime, 1, "c", 16)
    #line = f"{load:<7}{mem:>7}"
    lcd.display_line(load, 2, "c", 16)

    sleep(15)

    # query the pihole api for info
    data = get_summary()
    listed_domains = str(data["gravity"]["domains_being_blocked"])
    queries_today = str(data["queries"]["total"])
    queries_forward = str(data["queries"]["forwarded"])
    ads_blocked = str(data["queries"]["blocked"])
    ads_percent = str(round(data["queries"]["percent_blocked"], 2)) + "%"
    unique_clients = str(data["clients"]["active"])
    total_clients = str(data["clients"]["total"])

    ga_raw = data["gravity"]["last_update"]
    ga_delta = datetime.now() - datetime.fromtimestamp(ga_raw)

    gravity_age = str(ga_delta.days) + ":" + str(ga_delta.seconds//3600).rjust(2, "0") + ":" + str((ga_delta.seconds//60)%60).rjust(2, "0")

    lcd.clear()
    lcd.display_line("Domains", 1, "c", 16)
    lcd.display_line(listed_domains, 2, "c", 16)

    sleep(30)

    lcd.clear()
    lcd.display_line("Queries", 1, "c", 16)
    lcd.display_line(queries_today + "/" + queries_forward, 2, "c", 16)

    sleep(30)

    lcd.clear()
    lcd.display_line("Blocked", 1, "c", 16)
    line = ads_blocked+"  "+ads_percent
    lcd.display_line(line, 2, "c", 16)

    sleep(30)

    lcd.clear()
    lcd.display_line("Clients", 1, "c", 16)
    lcd.display_line(unique_clients + "/" + total_clients, 2, "c", 16)

    sleep(30)

    lcd.clear()
    lcd.display_line("Gravity", 1, "c", 16)
    lcd.display_line(gravity_age, 2, "c", 16)

    sleep(30)
