import requests
import time
import json
import datetime
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, init as colorama_init
import ctypes
import os

import sys
if os.name == 'nt':
    import ctypes

config_line = os.path.join('cfg', 'settings.json')

config = json.load(open(config_line, encoding="utf-8"))

def clear(): 
    os.system('cls' if os.name =='nt' else 'clear')

def print01(text):
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(0.015)

clear()
print01(Fore.RED + "Created by alihan200" + Fore.RESET + "\n")
time.sleep(1)
print01(Fore.CYAN + "To buy please enter Discord : https://discord.gg/mobile" + Fore.RESET + "\n\n")
time.sleep(5)

clear()

colorama_init()

token_line = os.path.join('cfg', 'tokens.txt')
tokens = open(token_line, 'r').read().replace('\r', '').split('\n')

with open(config_line, 'r') as config_file:
    config_data = json.load(config_file)

webhook_url = config_data['webhook_url']
interval = config_data['delay']
data = config_data['data']
use_proxy = config_data['use_proxy']
max_threads = config_data['threads']
snipe_enabled = config_data.get('snipe_enabled', False)

if use_proxy:
    config_line = os.path.join('cfg', 'proxies.txt')
    proxies = open('proxies.txt', 'r').read().replace('\r', '').split('\n')
    proxy_position = 0
else:
    proxies = []

token_position = 0
snipped = False
reqs = 0
num_symbols = len(tokens)
num_servers = len(data)
start_time = time.time()

def webhook(value):
    data = {
        "content": value
    }
    requests.post(webhook_url, json=data)

def snipe(value):
    global reqs, proxy_position, snipped
    key, value = value
    url = f"https://canary.discord.com/api/v7/guilds/{value[1]}/vanity-url"
    headers = {
        "Accept": "*/*",
        "Authorization": get_token(),
        "Content-Type": "application/json"
    }
    payload = {
        "code": value[0]
    }
    if use_proxy:
        proxy = get_proxy()
        proxies = {"http": proxy, "https": proxy}
    else:
        proxies = {}
    try:
        response = requests.patch(url, headers=headers, data=json.dumps(payload), proxies=proxies, timeout=10)
        json_response = response.json()

        if json_response.get("code") == 50001:
            print(f"{Fore.MAGENTA}[{get_time()}] {Fore.RESET} || {Fore.RED}[TOKEN  HAS NO PERMISSION]")
            return
        
        if json_response.get("errors") and json_response["errors"].get("code") and json_response["errors"]["code"]["_errors"][0]["code"]:
            error_message = json_response["errors"]["code"]["_errors"][0]["message"]
            print(f"{Fore.MAGENTA}[{get_time()}]  || {Fore.RED}[ERROR MESSAGE: {error_message}]")
            return
        
        if json_response.get("code") == 0:
            print(f"{Fore.MAGENTA}[{get_time()}] {Fore.RESET} || {Fore.RED}[INVALID TOKEN]")
            return

        if json_response.get("code") == value[0]:
            print("[{}] Sniper Done || [{}]".format(get_time(), value[0]))
            webhook("**https://discord.gg/{}\n\nAttempts : `{}`\n\n||@everyone||**".format(value[0], {reqs}))
            if snipe_enabled:
                os._exit(0)
        else:
            if "retry_after" in json_response:
                print(f"{Fore.MAGENTA}[{get_time()}]{Fore.RESET} ||{Fore.RED} Retry after: [{get_cooldown(time.time() + json_response['retry_after'])}] {Fore.RESET}||{Fore.RED} ID Server: [{value[1]}]")

            elif json_response.get("code") == 50020:
                reqs += 1
                print(f"{Fore.MAGENTA}[{get_time()}] {Fore.RESET} || {Fore.CYAN}Vanity: {Fore.GREEN}[{value[0]}] {Fore.RESET}||{Fore.CYAN} ID Server: {Fore.YELLOW}[{value[1]}]{Fore.RESET}")

                elapsed_time = time.time() - start_time
                speed = reqs / elapsed_time

                ctypes.windll.kernel32.SetConsoleTitleW(f"Spammer Vanity  | Alihan Gokkaya || Tokens: [{num_symbols}] || Servers: [{num_servers}] || Attempts: [{reqs}] || Speed: {speed:.2f} requests/sec || Time Left: {get_cooldown(time.time() + json_response['retry_after'])}")

    except Exception as e:
        pass

def get_cooldown(cooldown):
    time_left = int(cooldown - time.time())
    hours, remainder = divmod(time_left, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02d}H:{:02d}M".format(hours, minutes)

def get_token():
    global token_position
    if token_position > len(tokens) - 1:
        token_position = 0
    token = tokens[token_position]
    token_position += 1
    return token

def get_proxy():
    global proxy_position
    if proxy_position > len(proxies) - 1:
        proxy_position = 0
    proxy = proxies[proxy_position]
    proxy_position += 1
    return proxy

def get_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

print(f"{Fore.MAGENTA}[{get_time()}] {Fore.RESET}|| {Fore.GREEN}Start Sniping {Fore.RESET}|| {Fore.RED}Sniping Speed: [{interval}ms]\n")
time.sleep(2)

with ThreadPoolExecutor(max_workers=max_threads) as executor:
    try:
        while not snipped:
            executor.map(snipe, data.items())
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
