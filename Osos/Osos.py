
import pyautogui
import time
time.sleep(2)
print("Starting")

cpu_x, cpu_y = 252, 221 # cpu top left coordinates

ip_x, ip_y = 252, 357 # Idle processes top left coordinates
proc_size = 89 # Size of process box including padding, used to locate processes on screen
ip_w, ip_h = 7, 6 # Idle processes width/height
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
                print(f"Skipping unknown page in ram at {dx}, {dy} with colour {colour}")
    # Check for and handle any blue pages (pages where a process needs this page in ram)
    pyautogui.PAUSE = 0.005
    for dy in range(disk_h):
        for dx in range(disk_w):
            if scr.getpixel((disk_x + page_w * dx, disk_y + page_h * dy)) == (0, 0, 255):
                # Check if there is an empty slot in ram
                if None in ram:
                    # If so, we can just move the blue page straight into ram then
                    pyautogui.moveTo(disk_x + page_w * dx, disk_y + page_h * dy)
                    pyautogui.leftClick()
                    ram[ram.index(None)] = 2
                else:
                    # Otherwise, we have to find an unused page in ram to remove
                    s = ram.index(1)
                    rx = s % ram_w
                    ry = s // ram_w
                    pyautogui.leftClick(ram_x + page_w * rx, ram_y + page_h * ry)
                    ram[s] = 2
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
            # Rare event when a dead process is flying past, ignore it
            cpus.append(None)
        elif colour == (155, 155, 154):
            # Process is waiting for IO, get it out of here
            pyautogui.moveTo(cpu_x + n * proc_size, cpu_y)
            pyautogui.leftClick()
            cpus.append(None)
            print("Moved IO blocked process out of CPU")
        elif colour == (176, 216, 230):
            # Process is finished, get it out of here
            pyautogui.moveTo(cpu_x + n * proc_size, cpu_y)
            pyautogui.leftClick()
            cpus.append(None)
            print("Cleared finished process")
        elif colour == (0, 0, 255):
            # Process is waiting for IO, for now we assign it the highest priority so the bot doesn't move it out
            cpus.append(6)
        else:
            print("Skipping unknown CPU process colour:", colour)
    
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
                 # Rare event when a dead process (gray) flies past the idle processes, we ignore it since the next frame will almost certainly be back to normal
                idles.append(None)
            elif colour == (155, 155, 154):
                # Process waiting for IO, leave it alone
                idles.append(None)
            else:
                print("Skipping unknown idle process colour:", colour)
                idles.append(None)
    
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
                break
        cpu_index += 1