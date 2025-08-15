import subprocess
import sys
import os
from pathlib import Path
import config

def convert_image_to_mb4(image_path):
    image_name = Path(image_path).stem
    output_mb4 = os.path.join(config.OUTPUT_DIR, f"{image_name}.mb4")
    base = Path(output_mb4).with_suffix("")
    bmp_path = str(base) + "2.bmp"
    svg_path = str(base) + "2.svg"

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    cmd1 = f'cmd /c "echo \"{image_path}\" \"{bmp_path}\" | \"{config.CONVERTER_WORKDIR}\\convertcv\" "'

    subprocess.run(cmd1, shell=True, check=True, cwd=config.CONVERTER_WORKDIR)
    subprocess.run(['potrace', '-a', '-100', '--svg', bmp_path], check=True, cwd=config.CONVERTER_WORKDIR)
    subprocess.run([
        sys.executable, config.CONVERTER_SCRIPT,
        "-i", svg_path,
        "-o", output_mb4
    ], check=True, cwd=config.CONVERTER_WORKDIR)

    return output_mb4
