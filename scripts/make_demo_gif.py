"""Assemble actual browser captures into a walkthrough; never synthesize UI data."""

from pathlib import Path

from PIL import Image, ImageOps

assets = Path("docs/assets")
frames = []
for name in ["dashboard", "customers", "customer-detail", "models", "monitoring"]:
    with Image.open(assets / f"{name}.png") as source:
        frame = ImageOps.pad(source.convert("RGB"), (1080, 825), color="#f5f7fa")
        frames.append(frame.quantize(colors=128))
frames[0].save(
    assets / "demo.gif",
    save_all=True,
    append_images=frames[1:],
    duration=[2400, 1800, 2600, 2400, 2400],
    loop=0,
    optimize=True,
)
print(assets / "demo.gif")
