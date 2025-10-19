# mypy: ignore-errors
from PIL import Image

from settings import asset_path


def remove_background(path, back=(255, 255, 255), threshold=40):
    br, bg, bb = back
    path = asset_path(path)
    img = Image.open(path).convert("RGBA")
    new_data = []
    for r, g, b, a in img.getdata():
        brightness = abs(r - br) + abs(g - bg) + abs(b - bb)
        if brightness < threshold:
            new_data.append((r, g, b, 0))  # fully transparent
        else:
            new_data.append((r, g, b, a))
    img.putdata(new_data)
    img.save(path)


def chromakey(path, coeff=5):
    path = asset_path(path)
    img = Image.open(path).convert("RGBA")
    new_data = []
    for r, g, b, a in img.getdata():
        if (b + r) * coeff < g:
            new_data.append((r, g, b, 0))  # fully transparent
        else:
            new_data.append((r, g, b, a))
    img.putdata(new_data)
    img.save(path)


def remove_light(path, trhreshold=80, var=1.10):
    path = asset_path(path)
    img = Image.open(path).convert("RGBA")
    new_data = []
    for r, g, b, a in img.getdata():
        if g / var < r < g * var and g / var < b < g * var and g > trhreshold:
            new_data.append((r, g, b, 0))  # fully transparent
        else:
            new_data.append((r, g, b, a))
    img.putdata(new_data)
    img.save(path)


"""remove_light("digger/n_0.png")
remove_light("digger/n_1.png")
remove_light("digger/n_2.png")
remove_light("digger/n_3.png")
remove_light("digger/n_4.png")
"""
chromakey("digger/green.png")
