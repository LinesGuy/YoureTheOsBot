
import pyautogui
import time
time.sleep(2)
print("start")

cpu_x, cpu_y = 252, 221 # cpu top left coordinates

ip_x, ip_y = 252, 357 # Idle processes top left coordinates
proc_size = 89 # Size of process box including padding, used to locate processes on screen
ip_w, ip_h = 7, 6 # Idle processes width/height
ldelay = 0
pyautogui.PAUSE = 0.01


ram_x, ram_y = 913, 331
page_w, page_h = 53, 47
disk_w, disk_h = 16, 7

# Hard:
#disk_x, disk_y = 907, 672
#ram_w, ram_h = 16, 6

# Harder
#disk_x, disk_y = 907, 672
#ram_w, ram_h = 16, 5

# Insane:
disk_x, disk_y = 907, 576
ram_w, ram_h = 16, 4

cpu_num = 16 # Number of cpus available

while True:
    scr = pyautogui.screenshot()
    # Check I/O events
    if scr.getpixel((337, 132)) == (0, 128, 128):
        pyautogui.moveTo(337, 132)
        pyautogui.leftClick()
    ram = []
    for ry in range(ram_h):
        for rx in range(ram_w):
            colour = scr.getpixel((ram_x + page_w * rx, ram_y + page_h * ry))
            if colour == (0, 0, 0):
                ram.append(None) # Empty
            elif colour == (99, 102, 106):
                ram.append(1) # Idle
            elif colour == (255, 255, 255):
                ram.append(2) # In use
            else:
                print(f"!!!!!!!!!!!!Unknown ram colour at {dx}, {dy}: {colour}")
    pyautogui.PAUSE = 0.005
    for dy in range(disk_h):
        for dx in range(disk_w):
            if scr.getpixel((disk_x + page_w * dx, disk_y + page_h * dy)) == (0, 0, 255):
                # Page to be transferred to ram
                #print(f"Moving blue page in disk at {dx}, {dy}")
                # Check if there is an empty slot in ram
                if None in ram:
                    # We can just move the blue page straight into ram then
                    pyautogui.moveTo(disk_x + page_w * dx, disk_y + page_h * dy)
                    pyautogui.leftClick()
                    ram[ram.index(None)] = 2
                    #print("Moved blue page into ram")
                else:
                    # Otherwise, we have to find an unused page in ram to remove
                    s = ram.index(1)
                    rx = s % ram_w
                    ry = s // ram_w
                    #print(f"Found unused page at {rx}, {ry} (index {ram.index(1)}), swapping")
                    #pyautogui.moveTo(ram_x + page_w * rx, ram_y + page_h * ry)
                    #pyautogui.leftClick()
                    pyautogui.leftClick(ram_x + page_w * rx, ram_y + page_h * ry)
                    ram[s] = 2
                    #pyautogui.moveTo(disk_x + page_w * dx, disk_y + page_h * dy)
                    #pyautogui.leftClick()
                    pyautogui.leftClick(disk_x + page_w * dx, disk_y + page_h * dy)
    pyautogui.PAUSE = 0.01
    cpus = []
    for n in range(cpu_num):
        colour = scr.getpixel((cpu_x + n * proc_size, cpu_y))
        if colour == (0, 0, 0):
            cpus.append(None)
        elif colour == (0, 255, 0):
            cpus.append(1)
        elif colour == (255, 255, 0):
            cpus.append(2)
        elif colour == (255, 165, 0):
            cpus.append(3)
        elif colour == (255, 0, 0):
            cpus.append(4)
        elif colour == (139, 0, 0):
            cpus.append(5)
        elif colour == (80, 0, 0):
            cpus.append(6)
        elif colour == (99, 102, 106):
            cpus.append(None) # This is actually the gray process but we treat it like an empty process
        elif colour == (155, 155, 154):
            # Idle process, get it out of here
            pyautogui.moveTo(cpu_x + n * proc_size, cpu_y)
            pyautogui.leftClick()
            cpus.append(None)
            print("Moved idle process out of CPU")
        elif colour == (176, 216, 230):
            # Finished process, get it out of here
            pyautogui.moveTo(cpu_x + n * proc_size, cpu_y)
            pyautogui.leftClick()
            cpus.append(None)
            print("Cleared finished process")
        elif colour == (0, 0, 255):
            # Blue process, don't move it, treat it like it shouldn't be moved at all
            print("Skipping blue process")
            cpus.append(6)
        else:
            print("!!!!!!!!!!!! Unknown CPU colour:", colour)
    #print("cpus:", cpus)
    
    idles = []
    for y in range(ip_h):
        for x in range(ip_w):
            sx = ip_x + x * proc_size
            sy = ip_y + y * proc_size
            colour = scr.getpixel((sx, sy))
            if colour == (0, 0, 0):
                idles.append(None)
            elif colour == (0, 255, 0):
                idles.append(1)
            elif colour == (255, 255, 0):
                idles.append(2)
            elif colour == (255, 165, 0):
                idles.append(3)
            elif colour == (255, 0, 0):
                idles.append(4)
            elif colour == (139, 0, 0):
                idles.append(5)
            elif colour == (80, 0, 0):
                idles.append(6)
            elif colour == (99, 102, 106):
                idles.append(None) # This is actually the gray process but we treat it like an empty process
            elif colour == (155, 155, 154):
                # Idle
                idles.append(None)
            else:
                print("!!!!!!!!! Unknown idle colour:", colour)
    #print("idles:", idles)
    cpu_index = 0
    for cpu in cpus:
        if cpu is None:
            for c in range(6, 0, -1):
                if c not in idles:
                    continue
                i = idles.index(c)
                x = i % ip_w
                y = i // ip_w
                pyautogui.moveTo(ip_x + x * proc_size, ip_y + y * proc_size)
                pyautogui.leftClick()
                idles[i] = None
                print(f"Moved {x}, {y} to {cpu_index + 1}")
                break
        else:
            for c in range(6, cpu, -1):
                if c not in idles:
                    continue
                pyautogui.moveTo(cpu_x + cpu_index * proc_size, cpu_y)
                pyautogui.leftClick()
                print(f"Moved process with priority {cpu} out of {cpu_index + 1}")
                idles[idles.index(None)] = cpu
                #if None in idles:   
                #else:
                    #idles.append(c)
                #i = idles.index(c)
                #x = i % ip_w
                #y = i // ip_w
                #pyautogui.moveTo(ip_x + x * proc_size, ip_y + y * proc_size)
                #pyautogui.leftClick()
                #idles[i] = None
                #print(f"Moved {x}, {y} (index {i}) with priority {c} to {cpu_index + 1}")
                break
        cpu_index += 1
    #input("Press enter to continue")