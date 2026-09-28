"""Chek rasmini tozalash (02-backend.md, 6-bo'lim).

Rasm Pillow bilan ochiladi va JPEG sifatida qayta kodlanadi: EXIF, GPS, XMP, ICC va
boshqa metadata chiqmaydi, rasm ichiga yashirilgan "polyglot" payload ham yo'qoladi.
HEIC ham JPEG'ga aylantiriladi — mijozlar bitta formatni ko'rsatadi.
"""

import io
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener

from app.application.common.interfaces import SanitizedImage
from app.domain.common.errors import FileRejectedError

register_heif_opener()

_PIL_FORMATS = {"jpeg": {"JPEG", "MPO"}, "png": {"PNG"}, "heic": {"HEIF"}}
_MAX_SIDE = 4096


class PillowImageSanitizer:
    def __init__(self, max_pixels: int) -> None:
        self._max_pixels = max_pixels

    def sanitize(self, data: bytes, expected_format: str) -> SanitizedImage:
        try:
            with warnings.catch_warnings():
                # DecompressionBombWarning ham xato sifatida — chegarani o'zimiz tekshiramiz
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(data)) as img:
                    if img.format not in _PIL_FORMATS.get(expected_format, set()):
                        raise FileRejectedError()
                    if img.width * img.height > self._max_pixels:
                        raise FileRejectedError()
                    img.load()
                    # Orientatsiyani piksellarga qo'llaymiz — keyin EXIF kerak emas
                    clean = ImageOps.exif_transpose(img).convert("RGB")
        except FileRejectedError:
            raise
        except (UnidentifiedImageError, OSError, ValueError, SyntaxError,
                Image.DecompressionBombError, Image.DecompressionBombWarning):
            raise FileRejectedError() from None

        clean.thumbnail((_MAX_SIDE, _MAX_SIDE))
        out = io.BytesIO()
        # exif/icc_profile berilmaydi — metadata yozilmaydi
        clean.save(out, format="JPEG", quality=85, optimize=True)
        return SanitizedImage(data=out.getvalue(), content_type="image/jpeg")


def sniff_image_format(data: bytes) -> str | None:
    """MIME Content-Type'ga emas, fayl boshidagi magic bytes'ga ishonamiz."""
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(data) >= 12 and data[4:8] == b"ftyp" and data[8:12] in {
        b"heic", b"heix", b"hevc", b"hevx", b"heim", b"heis", b"mif1", b"msf1",
    }:
        return "heic"
    return None
