from flask import Flask, render_template_string, send_from_directory
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MAIN_DIR = BASE_DIR / "templates" / "main"

app = Flask(__name__)



@app.route("/")
def main_p436fge():
    MAIN_DIR = BASE_DIR / "templates" / "main"
    html_path = MAIN_DIR / "index.html"
    html = html_path.read_text(encoding="utf-8")
    return render_template_string(html, title="Ивентура")


# ---------- CSS из main ----------

@app.route("/main/global.css")
def main_csdafasdf():
    MAIN_DIR = BASE_DIR / "templates" / "main"
    return send_from_directory(MAIN_DIR, "global.css")

@app.route("/main/images/<path:filename>")
def main_imasdfasdfqewres(filename):
    MAIN_DIR = BASE_DIR / "templates" / "main"
    return send_from_directory(MAIN_DIR / "images", filename)
# ---------- Картинки из main/images ----------
@app.route("/info")
def main_54y5yge():
    MAIN_DIR = BASE_DIR / "templates" / "info"
    html_path = MAIN_DIR / "index.html"
    html = html_path.read_text(encoding="utf-8")
    return render_template_string(html, title="Ивентура")
@app.route("/info/images/<path:filename>")
def mai324234es(filename):
    MAIN_DIR = BASE_DIR / "templates" / "info"
    return send_from_directory(MAIN_DIR / "images", filename)

@app.route("/info/global.css")
def main_346hg():
    MAIN_DIR = BASE_DIR / "templates" / "info"
    return send_from_directory(MAIN_DIR, "global.css")
@app.route("/students")
def main_54sdf234e():
    MAIN_DIR = BASE_DIR / "templates" / "students"
    html_path = MAIN_DIR / "index.html"
    html = html_path.read_text(encoding="utf-8")
    return render_template_string(html, title="Ивентура")
@app.route("/students/images/<path:filename>")
def mai324sdes(filename):
    MAIN_DIR = BASE_DIR / "templates" / "students"
    return send_from_directory(MAIN_DIR / "images", filename)

@app.route("/students/global.css")
def maSDF246hg():
    MAIN_DIR = BASE_DIR / "templates" / "students"
    return send_from_directory(MAIN_DIR, "global.css")
@app.route("/colleges")
def maiAF123ge():
    MAIN_DIR = BASE_DIR / "templates" / "colleges"
    html_path = MAIN_DIR / "index.html"
    html = html_path.read_text(encoding="utf-8")
    return render_template_string(html, title="Ивентура")
@app.route("/colleges/images/<path:filename>")
def mai324sdf(filename):
    MAIN_DIR = BASE_DIR / "templates" / "colleges"
    return send_from_directory(MAIN_DIR / "images", filename)

@app.route("/colleges/global.css")
def main_321514g():
    MAIN_DIR = BASE_DIR / "templates" / "colleges"
    return send_from_directory(MAIN_DIR, "global.css")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
