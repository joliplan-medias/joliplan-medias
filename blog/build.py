"""Génère le blog Joli Plan (site statique) dans docs/ à partir de blog/contenu/<langue>.json.

Usage : python3 blog/build.py
Charte : fond crème FAF6F1, vert 46573F, rose 9B4B5A, poudre EAC8C4 ; titres EB Garamond, texte Lato.
"""
import html
import json
import re
import shutil
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CONTENU = RACINE / "blog" / "contenu"
SORTIE = RACINE / "docs"
BASE = "https://joliplan-medias.github.io/joliplan-medias"  # à changer si un domaine est acheté
DOSSIERS_PINS = {"fr": "pins", "de": "pins-de", "es": "pins-es", "it": "pins-it", "uk": "pins-uk"}
LANG_HTML = {"fr": "fr", "de": "de", "es": "es", "it": "it", "uk": "en-GB"}



def e(texte):
    """Échappe le HTML et colle les nombres à leurs unités (10 000 €, 30 %)."""
    texte = re.sub(r"(\d) (?=\d{3}\b)", "\\1\u202f", texte)
    texte = re.sub(r"(\d) (?=[€%£])", "\\1\u00a0", texte)
    return html.escape(texte)


def page(lang, titre, description, chemin, corps, accueil_rel, image=None, schema=None):
    url = f"{BASE}/{chemin}"
    og_image = f'<meta property="og:image" content="{BASE}/{image}">' if image else ""
    ld = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>' if schema else ""
    return f"""<!doctype html>
<html lang="{LANG_HTML[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(titre)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
{og_image}
<link rel="icon" href="{accueil_rel}assets/icone.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,500;0,600;1,400&family=Lato:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{accueil_rel}assets/style.css">
{ld}
</head>
<body>
<header class="entete"><a class="logo" href="{accueil_rel}{lang}/"><img src="{accueil_rel}assets/icone.png" alt="" width="34" height="34"><span><em>Joli</em> Plan</span></a></header>
<main>
{corps}
</main>
<footer class="pied"><a class="logo" href="{accueil_rel}{lang}/"><img src="{accueil_rel}assets/icone.png" alt="" width="28" height="28"><span><em>Joli</em> Plan</span></a></footer>
</body>
</html>
"""


def bloc_section(s):
    out = [f"<h2>{e(s['titre'])}</h2>"]
    for p in s.get("paragraphes", []):
        out.append(f"<p>{e(p)}</p>")
    if "liste" in s:
        out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in s["liste"]) + "</ul>")
    if "liste_numerotee" in s:
        out.append('<ol class="etapes">' + "".join(f"<li>{e(x)}</li>" for x in s["liste_numerotee"]) + "</ol>")
    if "etapes" in s:
        out.append('<ol class="etapes">' + "".join(
            f"<li><strong>{e(a)}</strong> {e(b)}</li>" for a, b in s["etapes"]) + "</ol>")
    if "citation" in s:
        out.append(f'<blockquote class="modele">{e(s["citation"])}</blockquote>')
    if "tableau" in s:
        t = s["tableau"]
        tete = "".join(f"<th>{e(h)}</th>" for h in t["entetes"])
        lignes = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in l) + "</tr>" for l in t["lignes"])
        out.append(f'<div class="tableau"><table><thead><tr>{tete}</tr></thead><tbody>{lignes}</tbody></table></div>')
    return "\n".join(out)


def bloc_produit(c, appel):
    return f"""<aside class="produit">
<p class="appel">{e(appel)}</p>
<p>{e(c['texte_produit'])}</p>
<a class="bouton" href="{e(c['etsy'])}" rel="noopener">{e(c['cta_produit'])} ›</a>
</aside>"""


def construire_langue(c):
    lang = c["langue"]
    dossier = SORTIE / lang
    img_dir = SORTIE / "img" / lang
    img_dir.mkdir(parents=True, exist_ok=True)
    cartes = []
    for a in c["articles"]:
        src = RACINE / DOSSIERS_PINS[lang] / a["image"]
        shutil.copy2(src, img_dir / a["image"])
        chemin = f"{lang}/{a['slug']}/"
        image = f"img/{lang}/{a['image']}"
        sections = "\n".join(bloc_section(s) for s in a["sections"])
        corps = f"""<article class="article">
<p class="surtitre">{e(a['categorie'])}</p>
<h1>{e(a['titre'])}</h1>
<p class="chapeau">{e(a['intro'])}</p>
<figure class="visuel"><img src="../../{image}" alt="{e(a['image_alt'])}" width="1000" height="1500" loading="lazy"></figure>
{sections}
{bloc_produit(c, a['appel'])}
<p class="retour"><a href="../">← Tous les articles</a></p>
</article>"""
        schema = {"@context": "https://schema.org", "@type": "Article", "headline": a["titre"],
                  "description": a["description"], "datePublished": a["date"], "inLanguage": LANG_HTML[lang],
                  "image": f"{BASE}/{image}", "publisher": {"@type": "Organization", "name": "Joli Plan"}}
        (dossier / a["slug"]).mkdir(parents=True, exist_ok=True)
        (dossier / a["slug"] / "index.html").write_text(
            page(lang, a["titre"], a["description"], chemin, corps, "../../", image, schema), encoding="utf-8")
        cartes.append(f"""<a class="carte" href="{a['slug']}/"><img src="../{image}" alt="" loading="lazy" width="1000" height="1500"><span class="surtitre">{e(a['categorie'])}</span><span class="titre-carte">{e(a['titre'])}</span></a>""")
    corps = f"""<section class="accueil">
<p class="surtitre">Le carnet Joli Plan</p>
<h1>{e(c['accroche'])}</h1>
<div class="grille">{''.join(cartes)}</div>
{bloc_produit(c, "Tout votre mariage dans un seul fichier.")}
</section>"""
    (dossier / "index.html").write_text(
        page(lang, c["nom_site"], c["accroche"], f"{lang}/", corps, "../"), encoding="utf-8")
    return [f"{BASE}/{lang}/"] + [f"{BASE}/{lang}/{a['slug']}/" for a in c["articles"]]


def main():
    (SORTIE / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(RACINE / "blog" / "style.css", SORTIE / "assets" / "style.css")
    shutil.copy2(RACINE / "blog" / "icone.png", SORTIE / "assets" / "icone.png")
    urls = []
    for f in sorted(CONTENU.glob("*.json")):
        urls += construire_langue(json.loads(f.read_text(encoding="utf-8")))
    (SORTIE / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=fr/">'
        '<link rel="canonical" href="' + BASE + '/fr/"><title>Joli Plan</title>', encoding="utf-8")
    (SORTIE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (SORTIE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    (SORTIE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"{len(urls)} pages générées dans {SORTIE}")


if __name__ == "__main__":
    main()
