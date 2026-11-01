
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
黄历宜忌 ICS 自动生成器

输出：
calendar/huangli-yi.ics
calendar/huangli-ji.ics

日期范围：
去年、今年、明年
"""

import os
import uuid
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

from lunar_python import Lunar, Solar


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "calendar"

CALENDAR_NAME = {
    "yi": "黄历每日宜",
    "ji": "黄历每日忌",
}


def ics_escape(value):
    """转义 ICS 文本字段"""
    value = str(value)
    value = value.replace("\\", "\\\\")
    value = value.replace(";", "\\;")
    value = value.replace(",", "\\,")
    value = value.replace("\r\n", "\\n")
    value = value.replace("\n", "\\n")
    return value


def fold_line(line, limit=75):
    """按照 UTF-8 字节长度折叠 ICS 行"""
    result = []
    current = ""
    current_bytes = 0

    for char in line:
        char_bytes = len(char.encode("utf-8"))

        if current_bytes + char_bytes > limit:
            result.append(current)
            current = " " + char
            current_bytes = 1 + char_bytes
        else:
            current += char
            current_bytes += char_bytes

    result.append(current)
    return "\r\n".join(result)


def get_lunar_info(current_date):
    """获取指定公历日期的农历和宜忌"""

    solar = Solar.fromYmd(
        current_date.year,
        current_date.month,
        current_date.day
    )

    lunar = Lunar.fromSolar(solar)

    yi = lunar.getDayYi()
    ji = lunar.getDayJi()

    # 兼容空值
    yi = [str(x) for x in yi if str(x).strip()]
    ji = [str(x) for x in ji if str(x).strip()]

    lunar_date = (
        lunar.getMonthInChinese()
        + "月"
        + lunar.getDayInChinese()
    )

    return {
        "yi": yi,
        "ji": ji,
        "lunar_date": lunar_date,
        "ganzhi": lunar.getDayInGanZhi(),
        "full_date": current_date.strftime("%Y-%m-%d"),
    }


def make_event(current_date, event_type, info):
    """生成单日全天 ICS 事件"""

    items = info[event_type]

    title_prefix = "宜" if event_type == "yi" else "忌"

    summary = title_prefix + "：" + "、".join(items)

    description = (
        f"公历：{info['full_date']}\n"
        f"农历：{info['lunar_date']}\n"
        f"干支：{info['ganzhi']}\n"
        f"{title_prefix}：{'、'.join(items)}\n"
        f"数据来源：6tail/lunar-python"
    )

    dtstart = current_date.strftime("%Y%m%d")
    dtend = (current_date + timedelta(days=1)).strftime("%Y%m%d")

    now = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    uid = f"{current_date.isoformat()}-{event_type}@huangli-calendar"

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now}",
        f"DTSTART;VALUE=DATE:{dtstart}",
        f"DTEND;VALUE=DATE:{dtend}",
        f"SUMMARY:{ics_escape(summary)}",
        f"DESCRIPTION:{ics_escape(description)}",
        "STATUS:CONFIRMED",
        "TRANSP:TRANSPARENT",
        "END:VEVENT",
    ]

    return lines


def generate_calendar(event_type, start_date, end_date):
    """生成宜或忌 ICS 文件"""

    calendar_name = CALENDAR_NAME[event_type]

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Huangli Calendar//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{ics_escape(calendar_name)}",
        "X-WR-TIMEZONE:Asia/Shanghai",
        "REFRESH-INTERVAL;VALUE=DURATION:P1D",
    ]

    current_date = start_date
    event_count = 0

    while current_date <= end_date:

        info = get_lunar_info(current_date)

        if info[event_type]:
            lines.extend(
                make_event(current_date, event_type, info)
            )
            event_count += 1

        current_date += timedelta(days=1)

    lines.append("END:VCALENDAR")

    # UTF-8 + CRLF + 75 字节折叠
    content = "\r\n".join(
        fold_line(line) for line in lines
    ) + "\r\n"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"huangli-{event_type}.ics"
    filepath = OUTPUT_DIR / filename

    filepath.write_text(content, encoding="utf-8", newline="")

    print(f"生成文件：{filepath}")
    print(f"事件数量：{event_count}")

    return event_count


def main():

    current_year = date.today().year

    start_year = current_year - 1
    end_year = current_year + 1

    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)

    print("=" * 50)
    print("黄历宜忌 ICS 生成器")
    print(f"年份范围：{start_year} - {end_year}")
    print(f"日期范围：{start_date} 至 {end_date}")
    print("=" * 50)

    yi_count = generate_calendar(
        "yi",
        start_date,
        end_date
    )

    ji_count = generate_calendar(
        "ji",
        start_date,
        end_date
    )

    print("=" * 50)
    print("生成完成")
    print(f"宜事件：{yi_count}")
    print(f"忌事件：{ji_count}")
    print("=" * 50)


if __name__ == "__main__":
    main()
