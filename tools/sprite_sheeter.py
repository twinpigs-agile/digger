from PIL import Image

from settings import asset_path

# Открываем исходный спрайт-шит
sprite_sheet = Image.open(asset_path("digger/digger.png"))

# Размеры
tile_size = 512
rows, cols = 2, 2  # 512x512 -> 4 части (2 строки, 2 столбца)

# Разрезаем и сохраняем
for row in range(rows):
    for col in range(cols):
        left = col * tile_size
        upper = row * tile_size
        right = left + tile_size
        lower = upper + tile_size

        # Вырезаем часть
        tile = sprite_sheet.crop((left, upper, right, lower))
        tile.save(asset_path(f"digger/tile_{row}_{col}.png"))

print("Готово! 4 файла tile_0_0.png ... tile_1_1.png")
