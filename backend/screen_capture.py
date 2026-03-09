import base64
import io
from typing import Optional

try:
    import mss
    import mss.tools
    from PIL import Image
    MSS_OK = True
except ImportError:
    MSS_OK=False


def capture_b64(max_width: int =1280)->Optional[str]:
    if not MSS_OK:
        return None
    try:
        with mss.mss() as sct:
            monitor=sct.monitors[1]  #primary
            raw =sct.grab(monitor)
            img =Image.frombytes("RGB", (raw.width, raw.height), raw.rgb)
            if img.width > max_width:
                ratio =max_width / img.width
                img =img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
            buf =io.BytesIO()
            img.save(buf, format="JPEG", quality=70)
            return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None
