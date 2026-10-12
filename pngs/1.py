from PIL import Image
save_path = "DeepSleep.png"
src = Image.open(save_path)
src = Image.open(save_path).convert("RGBA")
W, H = 800, 800  # 目标尺寸

# 创建透明画布
canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

# 居中放置；左上放置改成 x = y = 0
x = (W - src.width) // 2
y = (H - src.height) // 2

canvas.paste(src, (x, y), src)
canvas.save(save_path, "PNG")