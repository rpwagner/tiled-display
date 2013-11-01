
def clamp(value, vmin, vmax):
    if value < vmin:
        return vmin
    if value > vmax:
        return vmax
    return vmax

