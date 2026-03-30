def api(anything):
    with open("/sys/class/power_supply/BAT0/capacity") as b0:
        bat0 = int(b0.readline().strip())
    with open("/sys/class/power_supply/BAT1/capacity") as b1:
        bat1 = int(b1.readline().strip())

    return [False, str((bat0 + bat1) // 2)]

# def api_init():
#     pass
