"""Génère un visuel DMS13 (1080x1350 PNG) au style de la marque.
Usage : python3 outils/generer_visuel.py config.json visuels/nom.png
config.json : {"theme":"navy"|"light", "tag":"ÉLECTRICITÉ",
  "titre":"Votre tableau électrique est-il <em>prêt</em> pour l'hiver ?",
  "grand_chiffre":"" (optionnel, ex "2"), "unite":"" (ex "ans"), "sous_titre":"" (optionnel),
  "puces":["...","..."], "symbole_puce":"⚠"|"✕"|"✓", "appel":"👉 Votre réponse en commentaire" (optionnel),
  "slogan":"CLIMATISATION · ÉLECTRICITÉ · PLOMBERIE"}
Le mot entre <em></em> ressort en orange. Titre : 4 lignes max, ~14 caractères par ligne.
"""
import json, sys, html, tempfile, os
from playwright.sync_api import sync_playwright
c = json.load(open(sys.argv[1])); out = sys.argv[2]
navy = c.get("theme","navy") == "navy"
bg, fg, sub, line = ("#0F2A44","#fff","#9FB4C8","#24476B") if navy else ("#F5F1EA","#0F2A44","#6B7C8C","#D9D0C2")
sym = html.escape(c.get("symbole_puce","⚠"))
puces = "".join(f'<div><span class="s">{sym}</span> {html.escape(p)}</div>' for p in c.get("puces",[]))
big = f'<div class="big">{html.escape(c["grand_chiffre"])} <small>{html.escape(c.get("unite",""))}</small></div>' if c.get("grand_chiffre") else ""
st = f'<div class="st">{html.escape(c["sous_titre"])}</div>' if c.get("sous_titre") else ""
appel = f'<div class="appel">{html.escape(c["appel"])}</div>' if c.get("appel") else ""
deco = '<div class="deco"></div>' if navy else ""
lw = 700 if navy else 900
c["titre"] = c["titre"].replace(" :", "&nbsp;:").replace(" ?", "&nbsp;?").replace(" !", "&nbsp;!")
doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:"Liberation Sans","DejaVu Sans",Arial,sans-serif;background:{bg};color:{fg}}}
.card{{width:1080px;height:1350px;position:relative;overflow:hidden;display:flex;flex-direction:column;padding:90px 80px}}
.card>*:not(.deco){{position:relative;z-index:1}}
.deco{{position:absolute;right:-160px;top:760px;width:480px;height:480px;border-radius:50%;z-index:0;
background:radial-gradient(circle at 35% 35%,#F28C28 0,#F28C28 30%,transparent 31%),radial-gradient(circle,#18395A 0,#18395A 70%,transparent 71%)}}
.tag{{align-self:flex-start;font-weight:700;font-size:30px;letter-spacing:4px;padding:14px 26px;border-radius:8px;background:#F28C28;color:#0F2A44}}
h1{{font-size:88px;line-height:1.08;font-weight:800;margin-top:60px;letter-spacing:-1px;max-width:900px}}
h1 em{{font-style:normal;color:#F28C28}}
.big{{font-size:240px;font-weight:800;color:#F28C28;line-height:1;margin-top:30px}}.big small{{font-size:70px;color:{fg}}}
.st{{font-size:34px;color:{sub};margin-top:16px}}
.list{{margin-top:44px;font-size:40px;line-height:1.35;color:{fg};opacity:.92;max-width:{lw}px}}.list div{{padding-left:46px;text-indent:-46px;margin-bottom:18px}}
.s{{color:#F28C28;font-weight:800}}
.appel{{margin-top:auto;font-size:34px;color:{sub}}}
.foot{{display:flex;justify-content:space-between;align-items:flex-end;margin-top:auto;padding-top:36px;border-top:3px solid {line}}}
.appel+.foot{{margin-top:40px}}
.brand{{font-size:58px;font-weight:800}}.brand span{{color:#F28C28}}
.sub{{font-size:24px;color:{sub};margin-top:6px;letter-spacing:1px}}
.contact{{text-align:right;font-size:30px;font-weight:700}}.contact div{{font-size:24px;color:{sub};font-weight:400;margin-top:6px}}
</style></head><body><div class="card">{deco}
<div class="tag">{html.escape(c.get("tag",""))}</div><h1>{c["titre"]}</h1>{big}{st}<div class="list">{puces}</div>{appel}
<div class="foot"><div><div class="brand">DMS<span>13</span></div><div class="sub">{html.escape(c.get("slogan","CLIMATISATION · ÉLECTRICITÉ · PLOMBERIE"))}</div></div>
<div class="contact">06 29 46 40 32<div>dms13-multiservices.com</div></div></div></div></body></html>"""
f = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8"); f.write(doc); f.close()
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width":1080,"height":1350})
    pg.goto("file://" + f.name); pg.wait_for_timeout(300); pg.screenshot(path=out); b.close()
os.unlink(f.name); print("OK", out)
