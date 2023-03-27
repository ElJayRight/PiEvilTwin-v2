import pygame
import sys
import subprocess
import time
'''
clear the screen when scanning

'''
def main():
    scanning_ap = False
    evil_twin_state = 0
    ap_index = 0
    ap_range =0
    wifi_card_name =get_wifi_adaptor()
    pygame.init()
    WINDOW_SIZE = (440 , 260)
    SSID = "Not an Evil Twin"
    MAC_ADDR = "aa:bb:cc:dd:ee:ff"
    FONT = pygame.font.Font(None,24)
    small_font = pygame.font.Font(None,18)

    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Wifi thingy")
    screen.fill((255, 255, 255)) # white color

    #buttons
    draw_text("Start Evil-Twin",(355,204),small_font,screen)
    update_AP_info(SSID,MAC_ADDR,FONT,screen)
    change_ssid(SSID)
    change_mac_addr(MAC_ADDR)

    scan_ap_button = pygame.Rect(10,220,60,36)
    evil_twin = pygame.Rect(370,220,60,36)
    toggle_button(screen,scan_ap_button,0,small_font,("Scanning","SCAN"))
    toggle_button(screen,evil_twin,0,small_font,("Stop","Start"))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type ==pygame.KEYDOWN and event.key ==pygame.K_q):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type==pygame.KEYDOWN:
                if scan_ap_button.collidepoint(event.pos) or event.key==pygame.K_1:
                    toggle_button(screen,scan_ap_button,not scanning_ap,small_font, ("Scanning","SCAN"))
                    mon_name = start_monitor_mode(wifi_card_name)
                    scan_aps(mon_name,5,"out")
                    aps = get_aps("out")
                    toggle_button(screen,scan_ap_button,scanning_ap,small_font, ("Scanning","SCAN"))
                    render_text_list(screen,small_font,aps)
                    ap_range = len(aps)
                    draw_text("Select an AP to mimic",(90,82),small_font,screen)
                    move_menu_selector(screen,ap_index)
                    stop_monitor_mode(mon_name)
                elif evil_twin.collidepoint(event.pos) or event.type==pygame.K_2:
                    if evil_twin_state != 1:
                        evil_twin_state  = 2
                        toggle_button(screen,evil_twin,evil_twin_state,small_font,("Stop","Start"))
                        #run file
                        p = subprocess.Popen(["sudo","./PiEvilTwinStart.sh"],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                    else:
                        evil_twin_state = 3
                        toggle_button(screen,evil_twin,evil_twin_state,small_font,("Stop","Start"))
                        #run the stop file
                        p = subprocess.Popen(["sudo","./stop.sh"],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                    p.communicate()
                    time.sleep(1)
                    evil_twin_state-=1
                    toggle_button(screen,evil_twin,evil_twin_state,small_font,("Stop","Start"))

            elif event.type == pygame.KEYDOWN and ap_range!=0:
                if event.key == pygame.K_DOWN:
                    ap_index = (ap_index+1) % ap_range
                    move_menu_selector(screen,ap_index)
                elif event.key == pygame.K_UP:
                    ap_index = (ap_index-1) % ap_range
                    move_menu_selector(screen,ap_index)
                elif event.key == pygame.K_RETURN:
                    ssid = list(aps.keys())[ap_index]
                    mac = aps[ssid][0]
                    change_ssid(ssid)
                    update_AP_info(ssid,mac,FONT,screen)

def move_menu_selector(screen,pos):
    pygame.draw.rect(screen,(255,255,255),(90,100,8,200))
    scale = 8
    x,y = 90,102+pos*20
    pygame.draw.polygon(screen,(0,0,0),[(x,y),(x,y+scale),(x+scale/2,y+scale/2)])
    pygame.display.update()

def render_text_list(screen,font, text_list):
    # Calculate the position of the text
    text_x, text_y = 100,100
    rect_width = 200
    rect_height = 130
    rect_surf = pygame.Surface((rect_width, rect_height))
    rect_surf.fill((255, 255, 255))
    screen.blit(rect_surf, (100,100))
    # Render the text
    for i, text in enumerate(text_list):
        draw_text(text,(text_x,text_y+i*20),font,screen)
    
    pygame.display.update()
def toggle_button(screen, button, state, font: pygame.font.Font,button_text: tuple):
    if state==1:
        text = button_text[0]
        colour = (0,255,0)
    elif state==0:
        text = button_text[1]
        colour = (200,200,200)
    elif state==2:
        text = "Starting"
        colour = (255,255,0)
    elif state==3:
        text = "Stopping"
        colour = (255,255,0)
    else:
        print(state)
    button_text = font.render(text,True,(0,0,0))
    pygame.draw.rect(screen,colour,button)
    pygame.draw.rect(screen,(0,0,0),button,2)
    x = button[0]+button[2]//2- button_text.get_width()//2
    y = button[1]+ button[3]//2 -button_text.get_height()//2
    screen.blit(button_text,(x,y))
    pygame.display.update()

def update_AP_info(ssid:str,mac_addr:str,font:pygame.font.Font,window):
    pygame.draw.rect(window,0xffffff,(10,10,300,70))
    draw_text(f"SSID: {ssid}",(10,10),font,window)
    draw_text(f"Mac addr: {mac_addr}",(10,30),font,window)
    pygame.display.update()
    
def change_mac_addr(name: str):
    update_file("./PiEvilTwinStart.sh",f"macchanger --mac={name} wlan0\n")

def update_file(file_name: str, string: str):
    file = ''
    with open(file_name, 'r') as f:
        for line in f:
            if line.startswith(string[:4]):
                file+=string
            else:
                file+=line
    with open(file_name,'w') as f:
        f.write(file)

def get_wifi_adaptor() -> str:
    p = subprocess.Popen(["sudo","airmon-ng"],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    name = p.stdout.readlines()[3].decode().split()[1]
    return name

def start_monitor_mode(name) -> str:
    p = subprocess.Popen(["sudo","airmon-ng","start",name],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    new_name = p.stdout.readlines()[-3].decode().split("]")[1].strip()
    time.sleep(.1)
    p.terminate()
    return new_name

def stop_monitor_mode(name):
    p = subprocess.Popen(["sudo","airmon-ng","stop",name],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    time.sleep(.1)
    p.terminate()

def scan_aps(name, times,file_name):
    p = subprocess.Popen(["sudo","timeout",f"{times}s","airodump-ng",name,"-w","/tmp/"+file_name,"-o","csv"],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    time.sleep(6)
    p.terminate()
    return

def get_aps(file_name) -> dict:
    aps = {}
    with open(f"/tmp/{file_name}-01.csv") as file:
        for line in file:
            if "Probed" in line:
                break
            elif "BSSID" in line or line =="\n":
                pass
            else:
                bssid = line.split(',')[0]
                ssid = line.split(',')[-2].strip()
                enc = line.split(',')[5:8]
                if ssid !='':
                    aps[ssid] = [bssid,enc]
    p = subprocess.Popen(["sudo","rm",f"/tmp/{file_name}-01.csv"])
    return aps

def add_wpa2(password):
    with open('./hostapd.conf', 'a') as f:
        for line in f:
            if 'wpa' in line:
                return
        f.write("\nmacaddr_acl=0\n")
        f.write("ignore_broadcast_ssid=0\n")
        f.write("wpa=2\n")
        f.write("wpa_key_mgmt=WPA-PSK\n")
        f.write("rsn_pairwise=CCMP\n")
        f.write(f"wpa_passphrase={password}\n")

def change_ssid(name: str):
    update_file('./hostapd.conf',f'ssid={name}\n')

def draw_text(msg:str, location: tuple, font: pygame.font.Font, window):
    text = font.render(msg,True,(0,0,0))
    window.blit(text,location)



if __name__ == "__main__":
    main()