# Puente RSS para Chambas Torreón
# Lee las vacantes de Trabajos Medio Tiempo Torreón (WordPress JSON API)
# y las sirve como feed RSS 2.0 para el panel "Empleos en Telegram".
# Uso en Replit (Python): crear un Repl de Python, pegar este archivo como
# main.py, instalar dependencias (pip install flask requests) y ejecutar.

from flask import Flask, Response
import requests
import html
import re
from datetime import datetime
from email.utils import format_datetime
import xml.sax.saxutils as sax

app = Flask(__name__)

SRC = ("https://www.trabajosmediotiempotorreon.com.mx"
       "/wp-json/wp/v2/posts?per_page=20"
       "&_fields=date,title,excerpt,link")


def clean(text):
    """Quita etiquetas HTML y escapa el texto para XML."""
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return sax.escape(text)


@app.route("/")
def rss():
    try:
        posts = requests.get(SRC, timeout=20).json()
    except Exception:
        posts = []
    items = []
    for p in posts:
        title = clean(p.get("title", {}).get("rendered", "Sin título"))
        link = p.get("link", "")
        desc = clean(p.get("excerpt", {}).get("rendered", ""))
        try:
            dt = datetime.fromisoformat(p["date"].replace("Z", "+00:00"))
            pub = format_datetime(dt)
        except Exception:
            pub = ""
        items.append(
            "<item>"
            f"<title>{title}</title>"
            f"<link>{link}</link>"
            f"<description>{desc}</description>"
            f"<pubDate>{pub}</pubDate>"
            f"<guid>{link}</guid>"
            "</item>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>'
        "<title>Vacantes Torreón — Trabajos Medio Tiempo Torreón</title>"
        "<link>https://www.trabajosmediotiempotorreon.com.mx/</link>"
        "<description>Vacantes locales de Torreón publicadas en "
        "Trabajos Medio Tiempo Torreón.</description>"
        + "".join(items)
        + "</channel></rss>"
    )
    return Response(xml, mimetype="application/rss+xml; charset=utf-8")


@app.route("/feed")
def feed_alias():
    return rss()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
