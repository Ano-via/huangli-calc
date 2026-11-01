#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date, timedelta
from pathlib import Path
from lunar_python import Solar

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def get_years():
    """返回去年、今年、明年。"""
    current_year = date.today().year
    return range(current_year - 1, current_year + 2)


def format_items(items):
    """将宜忌列表转换为单行文本。"""
    if not items:
        return "无"
    return ",".join(str(item) for item in items)


def generate():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    yi_lines = [
        "# lunar-python 每日宜事项",
        "# 格式：公历日期|宜事项（逗号分隔）",
    ]
    ji_lines = [
        "# lunar-python 每日忌事项",
        "# 格式：公历日期|忌事项（逗号分隔）",
    ]

    years = list(get_years())

    for year in years:
        current = date(year, 1, 1)
        end = date(year + 1, 1, 1) if year < 9999 else None

        while end is not None and current < end:
            solar = Solar.fromYmd(
                current.year,
                current.month,
                current.day,
            )
            lunar = solar.getLunar()

            yi = lunar.getDayYi()
            ji = lunar.getDayJi()

            date_text = current.isoformat()

            yi_lines.append(f"{date_text}|{format_items(yi)}")
            ji_lines.append(f"{date_text}|{format_items(ji)}")

            current += timedelta(days=1)

    (DATA_DIR / "yi.calc").write_text(
        "\n".join(yi_lines) + "\n",
        encoding="utf-8",
    )
    (DATA_DIR / "ji.calc").write_text(
        "\n".join(ji_lines) + "\n",
        encoding="utf-8",
    )

    print(f"生成完成：{years[0]}—{years[-1]}")
    print(f"宜事项：{DATA_DIR / 'yi.calc'}")
    print(f"忌事项：{DATA_DIR / 'ji.calc'}")


if __name__ == "__main__":
    generate()
