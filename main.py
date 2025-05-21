from fastapi import FastAPI, Request
from bot import send_alert
import logging
import hashlib
import time

app = FastAPI()

logging.basicConfig(level=logging.INFO)

sent_fingerprints = {}


@app.post("/grafana-alert")
async def grafana_webhook(request: Request):
    payload = await request.json()
    logging.info(f"✅ Получен webhook от Grafana: {payload}")

    alerts = payload.get("alerts", [])
    for alert in alerts:
        status = alert.get("status", "firing").upper()
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        summary = annotations.get("summary", "Нет описания")
        value_string = alert.get("valueString", "")
        starts_at = alert.get("startsAt", "")[:19].replace("T", " ")

        service = labels.get("service", labels.get("job", "Неизвестный сервис"))
        level = labels.get("level", "Неизвестный уровень")

        # panel_url = alert.get("panelURL")
        # grafana_link = f"\n\n🔗 [Открыть в Grafana]({panel_url})" if panel_url else ""

        fingerprint_raw = f"{status}-{service}-{level}-{summary}"
        fingerprint = hashlib.md5(fingerprint_raw.encode()).hexdigest()

        now = time.time()
        if fingerprint in sent_fingerprints:
            if now - sent_fingerprints[fingerprint] < 600:
                logging.info(f"🔁 Пропущено повторное уведомление: {fingerprint_raw}")
                continue

        sent_fingerprints[fingerprint] = now

        msg = (
            f"🚨 *[{status}]* {labels.get('alertname', 'Алерт без названия')}\n"
            f"📦 Сервис: {service} | Уровень: {level}\n"
            f"🕒 Время: {starts_at}\n"
            f"📊 Значения: {value_string or 'Нет данных'}\n\n"
            f"📝 Описание:\n{summary}"
        )
        await send_alert(msg)

    return {"ok": True}
