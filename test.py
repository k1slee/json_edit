import json
import sys
import os

MONTH_NAMES = {
    1: "январь", 2: "февраль", 3: "март", 4: "апрель",
    5: "май", 6: "июнь", 7: "июль", 8: "август",
    9: "сентябрь", 10: "октябрь", 11: "ноябрь", 12: "декабрь"
}

def pretty_report(data):
    lines = []

    # Общая информация
    agent_info = data["pckagent"]["pckagentinfo"]
    lines.append("=== Общая информация ===")
    lines.append(f"Дата создания: {agent_info['dcreate']}")
    lines.append(f"Год: {agent_info['ngod']}")
    lines.append(f"Исполнитель: {agent_info['vexec']}")
    lines.append(f"УНП: {agent_info['vunp']}")
    lines.append(f"Телефон: {agent_info['vphn']}")
    lines.append("")

    # Все сотрудники
    for doc in data["pckagent"]["docagent"]:
        info = doc["docagentinfo"]
        lines.append( f"ФИО: {info['vfam']} {info['vname']} {info['votch']} | " f"Док: {info['cvdoc']} | " f"ЛН: {info['cln']} | " f"Страна: {info['cstranf']} | " f"ТС: {info['nrate']}%" )

        months_data = {}

        for block_name in ["tar4", "tar5", "tar7", "tar8", "tar9", "tar14"]:
            if block_name in doc:
                for t in doc[block_name]:
                    month = t["nmonth"]
                    if month not in months_data:
                        months_data[month] = []
                    if "tar4sum" in t:
                        for s in t["tar4sum"]:
                            if s["nsum"] != 0:
                                months_data[month].append(f"К{s['ncode']}={s['nsum']}")
                    if "tar5sum" in t:
                        for s in t["tar5sum"]:
                            if s["nsum"] != 0:
                                months_data[month].append(f"К{s['ncode']}={s['nsum']}")
                    if "tar7sum" in t:
                        for s in t["tar7sum"]:
                            if s["nsumv"] != 0:
                                months_data[month].append(f"К{s['ncode']}={s['nsumv']}")
                    if "tar8sum" in t:
                        for s in t["tar8sum"]:
                            if s["nsumv"] != 0:
                                months_data[month].append(f"К{s['ncode']}={s['nsumv']}")
                    if "tar9sum" in t:
                        for s in t["tar9sum"]:
                            if s["nsumv"] != 0:
                                months_data[month].append(f"К{s['ncode']}={s['nsumv']}")
                    if "nsumt" in t and t["nsumt"] != 0:
                        months_data[month].append(f"ПН={t['nsumt']}")
                    if "nsumdiv" in t and t["nsumdiv"] != 0:
                        months_data[month].append(f"Дивиденды={t['nsumdiv']}")

        for month, codes in sorted(months_data.items()):
            month_name = MONTH_NAMES.get(month, str(month))
            line = f"{month_name.capitalize()}: " + ", ".join(codes)
            lines.append(line)

        lines.append("")

    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python script.py <имя_файла.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    report_text = pretty_report(data)

    base, _ = os.path.splitext(input_file)
    output_file = base + ".txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"Отчёт сохранён в файл {output_file}")
