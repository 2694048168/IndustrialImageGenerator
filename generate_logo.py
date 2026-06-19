"""生成工业图像生成器 Logo 图标 (1200×600) — 蓝色工业调，无文字。"""

import cv2
import numpy as np
from pathlib import Path


OUTPUT_DIR = Path(__file__).parent / "assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_logo() -> np.ndarray:
    """创建一个蓝色工业风格的 Logo 图像（纯背景+图案，不含文字）。"""
    w, h = 1200, 600
    img = np.zeros((h, w, 3), dtype=np.uint8)

    # 深蓝渐变背景
    for y in range(h):
        t = y / h
        b = int(150 + 10 * t)
        g = int(100 + 20 * t)
        r = int(60 + 30 * t)
        img[y, :] = (b, g, r)

    # 装饰性边框
    cv2.rectangle(img, (20, 20), (w - 20, h - 20), (200, 150, 60), 2)

    # 顶部装饰线
    cv2.line(img, (80, 50), (w - 80, 50), (180, 130, 50), 1)

    # 底部装饰线
    cv2.line(img, (80, h - 50), (w - 80, h - 50), (180, 130, 50), 1)

    # 中心齿轮图标
    cx, cy = w // 2, h // 2 - 100
    outer_r = 100
    inner_r = 95
    teeth = 12
    teeth_depth = 25

    pts = []
    for i in range(teeth * 2):
        angle = (i * np.pi / teeth) - np.pi / 2
        r = outer_r + teeth_depth if i % 2 == 0 else outer_r
        px = int(cx + r * np.cos(angle))
        py = int(cy + r * np.sin(angle))
        pts.append((px, py))
    pts_array = np.array(pts, dtype=np.int32)
    cv2.fillPoly(img, [pts_array], (200, 160, 60))

    # 齿轮内圈
    cv2.circle(img, (cx, cy), inner_r, (20, 40, 70), -1)
    cv2.circle(img, (cx, cy), inner_r, (200, 160, 60), 2)

    # 中心十字准线
    cv2.line(img, (cx - 40, cy), (cx + 40, cy), (200, 160, 60), 2)
    cv2.line(img, (cx, cy - 40), (cx, cy + 40), (200, 160, 60), 2)
    cv2.circle(img, (cx, cy), 6, (200, 160, 60), -1)

    # 四个角标
    corner_size = 30
    corners = [
        (corner_size + 30, corner_size + 30),
        (w - corner_size - 30, corner_size + 30),
        (corner_size + 30, h - corner_size - 30),
        (w - corner_size - 30, h - corner_size - 30),
    ]
    for ccx, ccy in corners:
        cv2.drawMarker(
            img, (ccx, ccy), (200, 160, 60), cv2.MARKER_TILTED_CROSS, corner_size, 2
        )

    return img


def main():
    logo = create_logo()
    logo_path = OUTPUT_DIR / "logo.png"
    cv2.imwrite(str(logo_path), logo)
    print(f"Logo 已生成: {logo_path}")

    sizes = [256, 64, 48, 32, 16]
    icons = []
    for size in sizes:
        resized = cv2.resize(logo, (size, size), interpolation=cv2.INTER_AREA)
        icons.append(resized)

    icon_path = OUTPUT_DIR / "app_icon.png"
    cv2.imwrite(str(icon_path), icons[0])
    print(f"图标已生成: {icon_path}")

    try:
        from PIL import Image as PILImage

        pil_images = []
        for i, size in enumerate(sizes):
            resized = cv2.cvtColor(icons[i], cv2.COLOR_BGR2RGBA)
            pil_img = PILImage.fromarray(resized)
            pil_images.append(pil_img)

        ico_path = OUTPUT_DIR / "app_icon.ico"
        pil_images[0].save(
            str(ico_path),
            format="ICO",
            sizes=[(s, s) for s in sizes],
            append_images=pil_images[1:],
        )
        print(f"ICO 图标已生成: {ico_path}")
    except ImportError:
        print("Pillow 未安装，跳过 .ico 生成。")

    print("完成!")


if __name__ == "__main__":
    main()
