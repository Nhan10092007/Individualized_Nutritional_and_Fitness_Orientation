"""
Trích xuất Bảng thành phần dinh dưỡng thực phẩm Việt Nam 2017 từ PDF
(bang-thanh-phan-dinh-duong-thuc-pham-vn-2017-27-4-17.pdf)
và chuẩn hóa theo schema ORM `Food`:
code, name_vi, name_en, category, source, serving_unit, serving_weight_g,
calories_100g, protein_100g, fat_100g, carbs_100g, fiber_100g,
estimated_price_vnd, diet_type, notes
"""

import json
import re
from pathlib import Path
from typing import Any

import pypdf

from app.config import BACKEND_DIR

PDF_PATH = BACKEND_DIR / "data" / "raw" / "bang-thanh-phan-dinh-duong-thuc-pham-vn-2017-27-4-17.pdf"
OUTPUT_JSON_PATH = BACKEND_DIR / "data" / "processed" / "vietnam_foods_raw_pdf.json"

CATEGORY_MAP: dict[str, str] = {
    "01": "Ngũ cốc và sản phẩm chế biến",
    "02": "Khoai củ và sản phẩm chế biến",
    "03": "Hạt, quả giàu đạm và béo",
    "04": "Rau, củ, quả dùng làm rau",
    "05": "Quả chín",
    "06": "Dầu, mỡ và bơ",
    "07": "Thịt và sản phẩm chế biến",
    "08": "Thủy sản và sản phẩm chế biến",
    "09": "Trứng và sản phẩm chế biến",
    "10": "Sữa và sản phẩm chế biến",
    "11": "Đồ hộp",
    "12": "Đồ ngọt",
    "13": "Gia vị, nước chấm",
    "14": "Đồ uống",
}


def to_float(val: str | None) -> float:
    if not val or val in ("-", ".", "..", "...", "N/A"):
        return 0.0
    try:
        return round(float(val.replace(",", ".")), 2)
    except ValueError:
        return 0.0


def extract_pdf_foods(
    pdf_path: Path | str | None = None,
    out_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Đọc và trích xuất toàn bộ bảng dinh dưỡng từ file PDF 2017."""
    target_pdf = Path(pdf_path) if pdf_path else PDF_PATH
    if not target_pdf.exists():
        raise FileNotFoundError(f"Không tìm thấy file PDF: {target_pdf}")

    reader = pypdf.PdfReader(str(target_pdf))
    total_pages = len(reader.pages)
    start_page = 23  # Trang 24 trong tài liệu
    end_page = min(145, total_pages)  # Bảng 1 thành phần chính kết thúc ở khoảng trang 145

    pattern = re.compile(
        r"(?:^|\n)\s*(\d{1,4})\s+(\d{5})\s+(.*?)\s+(\d{1,3})\s+(\d{1,4})\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)(.*?)(?=\n\s*\d{1,4}\s+\d{5}|\n\s*(?:I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV)\s|\Z)",
        re.DOTALL,
    )

    foods: list[dict[str, Any]] = []
    seen_codes: set[str] = set()

    for page_idx in range(start_page, end_page):
        text = reader.pages[page_idx].extract_text()
        if not text:
            continue

        for m in pattern.finditer(text):
            item_no, code_raw, name_raw, edible, kcal, water, protein, fat, carb, fiber, tail = m.groups()
            code = f"VN_{code_raw}"
            if code in seen_codes:
                continue
            seen_codes.add(code)

            raw_full = " ".join(name_raw.split())

            # Cột cuối cùng của bảng chứa tên thuần Tiếng Việt
            tail_words = tail.strip().split()
            vi_tail = ""
            if tail_words:
                non_num: list[str] = []
                for w in reversed(tail_words):
                    if re.match(r"^[\d\.\-]+$", w):
                        break
                    non_num.insert(0, w)
                if non_num:
                    vi_tail = " ".join(non_num)

            if vi_tail and len(vi_tail) > 2:
                name_vi = vi_tail
                name_en = raw_full
                if vi_tail.lower() in raw_full.lower():
                    idx = raw_full.lower().find(vi_tail.lower())
                    name_en = (raw_full[:idx] + " " + raw_full[idx + len(vi_tail):]).strip(" ,-")
            else:
                name_vi = raw_full
                name_en = ""

            cat_code = code_raw[:2]
            cat = CATEGORY_MAP.get(cat_code, "Thực phẩm khác")

            # Gán loại ăn kiêng
            if cat_code in ("01", "02", "03", "04", "05"):
                diet_type = "vegan"
            elif cat_code in ("09", "10"):
                diet_type = "vegetarian"
            else:
                diet_type = "all"

            item = {
                "code": code,
                "name_vi": name_vi.strip(),
                "name_en": name_en.strip() or name_vi.strip(),
                "category": cat,
                "source": "VN_FCT",
                "serving_unit": "100g",
                "serving_weight_g": 100.0,
                "calories_100g": to_float(kcal),
                "protein_100g": to_float(protein),
                "fat_100g": to_float(fat),
                "carbs_100g": to_float(carb),
                "fiber_100g": to_float(fiber),
                "estimated_price_vnd": 0.0,
                "diet_type": diet_type,
                "notes": f"Viện Dinh dưỡng Quốc gia 2017 (Tỉ lệ ăn được: {edible}%)",
            }
            foods.append(item)

    dest = Path(out_path) if out_path else OUTPUT_JSON_PATH
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, mode="w", encoding="utf-8") as f:
        json.dump(foods, f, ensure_ascii=False, indent=2)

    return foods


if __name__ == "__main__":
    items = extract_pdf_foods()
    print(f"[+] Đã trích xuất thành công {len(items)} thực phẩm từ file PDF 2017 vào: {OUTPUT_JSON_PATH}")
