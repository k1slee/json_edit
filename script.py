#!/usr/bin/env python3
import json
from pathlib import Path
from calendar import month_name
import argparse

# --- Настройки маппинга ---
MAPPING = {
    "K201": {"section": "tar4", "code": 201, "field": "nsum"},
    "K503": {"section": "tar5", "code": 503, "field": "nsum"},
    "K620": {"section": "tar7", "code": 620, "field": "nsumv"},
    "PN":   {"section": "tar14", "code": None, "field": "nsumt"},
}
pn_multiplier = 1.0  # при необходимости скорректируйте

def find_code_value(month_obj, code, field):
    if not month_obj:
        return None
    for key, val in month_obj.items():
        if isinstance(val, list) and val and isinstance(val[0], dict) and 'ncode' in val[0]:
            for item in val:
                if item.get('ncode') == code:
                    return item.get(field)
    return None

def month_index_to_name(n):
    try:
        # month_name возвращает английские названия, заменим на русские вручную
        rus = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }
        return rus.get(int(n), f"Месяц{n}")
    except Exception:
        return f"Месяц{n}"

def format_value(value):
    if value is None or value == "":
        return ""
    if isinstance(value, (int, float)):
        if isinstance(value, float):
            s = f"{value:.2f}".rstrip('0').rstrip('.')
            return s
        return str(value)
    try:
        fv = float(value)
        s = f"{fv:.2f}".rstrip('0').rstrip('.')
        return s
    except Exception:
        return str(value)

def process_json(data):
    out_lines = []
    pck = data.get("pckagent") or {}
    info = pck.get("pckagentinfo", {})
    docagents = pck.get("docagent", [])

    created = info.get("dcreate") or ""
    year = info.get("ngod") or ""
    executor = info.get("vexec") or ""
    unp = info.get("vunp") or ""
    phone = info.get("vphn") or ""

    out_lines.append("=== Общая информация ===")
    out_lines.append(f"Дата создания: {created}")
    out_lines.append(f"Год: {year}")
    out_lines.append(f"Исполнитель: {executor}")
    out_lines.append(f"УНП: {unp}")
    out_lines.append(f"Телефон: {phone}")
    out_lines.append("")

    for doc in docagents:
        info = doc.get("docagentinfo", {})
        fam = info.get("vfam", "").strip()
        name = info.get("vname", "").strip()
        otch = info.get("votch", "").strip()
        cvdoc = info.get("cvdoc", "")
        cln = info.get("cln", "")
        cstranf = info.get("cstranf", "")
        nrate = info.get("nrate", "")

        fio = " ".join(part for part in (fam, name, otch) if part)
        header = f"{fio} | Док: {cvdoc} | ЛН: {cln} | Страна: {cstranf} | ТС: {nrate}%"
        out_lines.append(header)
        fields_line = []

        income_val = doc.get("ntsumincome")
        income_str = format_value(income_val)
        if income_str != "" and float(income_str) != 0:
            fields_line.append(f"ntsumincome: {income_str}")

        exemp_val = doc.get("ntsumexemp")
        exemp_str = format_value(exemp_val)
        if exemp_str != "" and float(exemp_str) != 0:
            fields_line.append(f"ntsumexemp: {exemp_str}")

        stand_val = doc.get("nsumstand")
        stand_str = format_value(stand_val)
        if stand_str != "" and float(stand_str) != 0:
            fields_line.append(f"nsumstand: {stand_str}")

        soc_val = doc.get("ntsumsoc")
        soc_str = format_value(soc_val)
        if soc_str != "" and float(soc_str) != 0:
            fields_line.append(f"ntsumsoc: {soc_str}")

        prop_val = doc.get("ntsumprop")
        prop_str = format_value(prop_val)
        if prop_str != "" and float(prop_str) != 0:
            fields_line.append(f"ntsumprop: {prop_str}")

        calc_val = doc.get("ntsumcalcincome")
        calc_str = format_value(calc_val)
        if calc_str != "" and float(calc_str) != 0:
            fields_line.append(f"ntsumcalcincome: {calc_str}")

        if fields_line:
            out_lines.append(" | ".join(fields_line))



    

        sections = {k: v for k, v in doc.items() if isinstance(v, list)}

        for month_idx in range(1, 13):
            parts = []
            for label, cfg in MAPPING.items():
                section_name = cfg["section"]
                code = cfg["code"]
                field = cfg["field"]

                section = sections.get(section_name, [])
                month_obj = next((m for m in section if int(m.get("nmonth", 0)) == month_idx), None)

                value = None
                if code is None:
                    if month_obj:
                        value = month_obj.get(field)
                else:
                    value = find_code_value(month_obj, code, field)

                if label == "PN" and value is not None:
                    try:
                        value = float(value) * pn_multiplier
                    except Exception:
                        pass

                val_str = format_value(value)
                if val_str != "" and float(val_str) != 0:
                    parts.append(f"{label}={val_str}")

            if parts:
                out_lines.append(f"{month_index_to_name(month_idx)}: " + ", ".join(parts))

        out_lines.append("")

    return "\n".join(out_lines)

def convert_file(input_path: Path):
    try:
        text = input_path.read_text(encoding="utf-8-sig")
        data = json.loads(text)
    except Exception as e:
        print(f"Ошибка чтения или парсинга {input_path}: {e}")
        return

    report = process_json(data)
    output_path = input_path.with_suffix(".txt")
    output_path.write_text(report, encoding="utf-8")
    print(f"Готово: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Конвертация JSON в текстовый отчёт с тем же именем файла.")
    parser.add_argument("files", nargs="+", help="Пути к JSON файлам")
    args = parser.parse_args()

    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f"Файл не найден: {p}")
            continue
        convert_file(p)

if __name__ == "__main__":
    main()
