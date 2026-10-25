"""Génère le blog Joli Plan (site statique) dans docs/ à partir de blog/contenu/<langue>.json.

Usage : python3 -I blog/build.py
Charte : fond crème FAF6F1, vert 46573F, rose 9B4B5A, poudre EAC8C4 ; titres EB Garamond, texte Lato.
Champs facultatifs d'une langue : "methode" (page Notre méthode), "gratuit" (page de téléchargement).
Champs facultatifs d'un article : "maj" (date de mise à jour), "faq" (liste de [question, réponse]).
"""
import html
import json
import re
import shutil
from pathlib import Path

from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
CONTENU = RACINE / "blog" / "contenu"
SORTIE = RACINE / "docs"
BASE = "https://joliplanstudio.fr"
RAW = "https://raw.githubusercontent.com/joliplan-medias/joliplan-medias/main"
DOSSIERS_PINS = {"fr": "pins", "de": "pins-de", "es": "pins-es", "it": "pins-it", "uk": "pins-uk"}
PINTEREST = {"fr": "joliplan", "de": "JoliPlanDE", "es": "joliplanes", "it": "JoliplanIT", "uk": "joliplanUK"}
PIN_SVG = '<svg class="ico-pin" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z"/></svg>'
LANG_HTML = {"fr": "fr", "de": "de", "es": "es", "it": "it", "uk": "en-GB"}
MOTS = {
    "fr": {"sommaire": "Dans cet article", "faq": "Questions fréquentes", "lies": "À lire aussi",
           "tous": "Tous les articles", "maj": "Mis à jour le", "methode": "Notre méthode", "voir": "Voir sur Etsy", "pinterest": "Suivre sur Pinterest"},
    "de": {"sommaire": "In diesem Artikel", "faq": "Häufige Fragen", "lies": "Auch lesenswert",
           "tous": "Alle Artikel", "maj": "Aktualisiert am", "methode": "Unsere Methode", "voir": "Auf Etsy ansehen", "pinterest": "Auf Pinterest folgen"},
    "es": {"sommaire": "En este artículo", "faq": "Preguntas frecuentes", "lies": "También te puede interesar",
           "tous": "Todos los artículos", "maj": "Actualizado el", "methode": "Nuestro método", "voir": "Ver en Etsy", "pinterest": "Seguir en Pinterest"},
    "it": {"sommaire": "In questo articolo", "faq": "Domande frequenti", "lies": "Da leggere anche",
           "tous": "Tutti gli articoli", "maj": "Aggiornato il", "methode": "Il nostro metodo", "voir": "Vedi su Etsy", "pinterest": "Seguici su Pinterest"},
    "uk": {"sommaire": "In this article", "faq": "Frequently asked questions", "lies": "Read next",
           "tous": "All articles", "maj": "Updated on", "methode": "Our method", "voir": "View on Etsy", "pinterest": "Follow on Pinterest"},
}


def e(texte):
    """Échappe le HTML et colle les nombres à leurs unités (10 000 €, 30 %)."""
    texte = re.sub(r"(\d) (?=\d{3}\b)", "\\1\u202f", texte)
    texte = re.sub(r"(\d) (?=[€%£])", "\\1\u00a0", texte)
    return html.escape(texte)


def ancre(texte):
    t = texte.lower()
    for a, b in (("àâä", "a"), ("éèêë", "e"), ("îï", "i"), ("ôö", "o"), ("ùûü", "u"), ("ç", "c"), ("ñ", "n"), ("ß", "ss")):
        for c in a:
            t = t.replace(c, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def date_lisible(lang, iso):
    a, m, j = iso.split("-")
    return f"{j}/{m}/{a}" if lang != "uk" else f"{j}/{m}/{a}"


def page(lang, titre, description, chemin, corps, rel, image=None, schemas=(), type_og="article"):
    url = f"{BASE}/{chemin}"
    og_image = f'<meta property="og:image" content="{BASE}/{image}">' if image else ""
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)
    m = MOTS[lang]
    return f"""<!doctype html>
<html lang="{LANG_HTML[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="G9rWwfYWoguup7oxZGhsrxkV0AbY1BA-Clq9PowUfEY" />
<meta name="google-site-verification" content="MfwLf_DihL9en-TvD3F2wiAyQQc6AC1-1RUfTC8c9nc" />
<title>{e(titre)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(titre)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="{type_og}">
<meta property="og:url" content="{url}">
{og_image}
<link rel="icon" href="{rel}assets/icone.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,500;0,600;1,400&family=Lato:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}assets/style.css">
{ld}
</head>
<body>
<header class="entete"><a class="logo" href="{rel}{lang}/"><img src="{rel}assets/icone.png" alt="" width="34" height="34"><span><em>Joli</em> Plan</span></a><a class="lien-pinterest" href="https://www.pinterest.com/{PINTEREST[lang]}/" rel="noopener" target="_blank">{PIN_SVG}<span>{e(m['pinterest'])}</span></a></header>
<main>
{corps}
</main>
<footer class="pied"><a class="logo" href="{rel}{lang}/"><img src="{rel}assets/icone.png" alt="" width="28" height="28"><span><em>Joli</em> Plan</span></a><a class="lien-pied" href="{rel}{lang}/methode/">{e(m['methode'])}</a><a class="lien-pied" href="https://www.pinterest.com/{PINTEREST[lang]}/" rel="noopener" target="_blank">{PIN_SVG} Pinterest</a></footer>
<script async defer src="https://assets.pinterest.com/js/pinit.js" data-pin-hover="true" data-pin-tall="true" data-pin-round="true"></script>
</body>
</html>
"""


def bloc_section(s):
    out = [f'<h2 id="{ancre(s["titre"])}">{e(s["titre"])}</h2>']
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


def bloc_gratuit(c, rel):
    g = c.get("gratuit")
    if not g:
        return ""
    return f"""<aside class="gratuit">
<p class="surtitre">{e(g['surtitre'])}</p>
<p class="appel">{e(g['accroche'])}</p>
<a class="bouton bouton-vert" href="{rel}{c['langue']}/{g['slug']}/">{e(g['cta_page'])} ›</a>
</aside>"""


def image_web(lang, nom):
    """Copie l'épingle en WebP léger pour le site ; renvoie le chemin relatif à docs/."""
    src = RACINE / DOSSIERS_PINS[lang] / nom
    dest = SORTIE / "img" / lang / (Path(nom).stem + ".webp")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or dest.stat().st_mtime < src.stat().st_mtime:
        Image.open(src).convert("RGB").resize((800, 1200), Image.LANCZOS).save(dest, "WEBP", quality=82)
    return f"img/{lang}/{dest.name}"


def figure(lang, a, rel):
    web = image_web(lang, a["image"])
    pin = f"{RAW}/{DOSSIERS_PINS[lang]}/{a['image']}"
    return (f'<figure class="visuel"><img src="{rel}{web}" alt="{e(a["image_alt"])}" width="800" height="1200" '
            f'loading="lazy" data-pin-media="{pin}" data-pin-description="{e(a["titre"])}"></figure>')


def construire_langue(c):
    lang = c["langue"]
    m = MOTS[lang]
    dossier = SORTIE / lang
    articles = sorted(c["articles"], key=lambda a: a.get("maj", a["date"]), reverse=True)
    urls = []
    for i, a in enumerate(articles):
        chemin = f"{lang}/{a['slug']}/"
        sommaire = "".join(f'<li><a href="#{ancre(s["titre"])}">{e(s["titre"])}</a></li>' for s in a["sections"])
        faq = a.get("faq", [])
        if faq:
            sommaire += f'<li><a href="#faq">{e(m["faq"])}</a></li>'
        sections = "\n".join(bloc_section(s) for s in a["sections"])
        faq_html = ""
        if faq:
            faq_html = f'<h2 id="faq">{e(m["faq"])}</h2>' + "".join(
                f"<details><summary>{e(q)}</summary><p>{e(r)}</p></details>" for q, r in faq)
        autres = [x for x in articles if x is not a][:3]
        lies = "".join(f'<li><a href="../{x["slug"]}/">{e(x["titre"])}</a></li>' for x in autres)
        maj = a.get("maj", a["date"])
        corps = f"""<article class="article">
<p class="surtitre">{e(a['categorie'])}</p>
<h1>{e(a['titre'])}</h1>
<p class="date">{e(m['maj'])} {date_lisible(lang, maj)}</p>
<p class="chapeau">{e(a['intro'])}</p>
<p class="cta-haut"><a href="{e(c['etsy'])}" rel="noopener">{e(c['cta_produit'])} ›</a></p>
<nav class="sommaire"><p>{e(m['sommaire'])}</p><ol>{sommaire}</ol></nav>
{figure(lang, a, "../../")}
{sections}
{bloc_produit(c, a['appel'])}
{faq_html}
{bloc_gratuit(c, "../../")}
<nav class="lies"><h2>{e(m['lies'])}</h2><ul>{lies}</ul></nav>
<p class="retour"><a href="../">← {e(m['tous'])}</a></p>
</article>"""
        image_png = f"{RAW}/{DOSSIERS_PINS[lang]}/{a['image']}"
        schemas = [{"@context": "https://schema.org", "@type": "Article", "headline": a["titre"],
                    "description": a["description"], "datePublished": a["date"], "dateModified": maj,
                    "inLanguage": LANG_HTML[lang], "image": image_png,
                    "author": {"@type": "Organization", "name": "Joli Plan", "url": f"{BASE}/{lang}/methode/"},
                    "publisher": {"@type": "Organization", "name": "Joli Plan"}}]
        if faq:
            schemas.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]})
        (dossier / a["slug"]).mkdir(parents=True, exist_ok=True)
        (dossier / a["slug"] / "index.html").write_text(
            page(lang, a["titre"], a["description"], chemin, corps, "../../", image_web(lang, a["image"]), schemas),
            encoding="utf-8")
        urls.append(f"{BASE}/{chemin}")

    cartes = "".join(
        f'<a class="carte" href="{a["slug"]}/"><img src="../{image_web(lang, a["image"])}" alt="" loading="lazy" '
        f'width="800" height="1200"><span class="surtitre">{e(a["categorie"])}</span>'
        f'<span class="titre-carte">{e(a["titre"])}</span></a>' for a in articles)
    corps = f"""<section class="accueil">
<p class="surtitre">{e(c['nom_site'])}</p>
<h1>{e(c['accroche'])}</h1>
{bloc_gratuit(c, "../")}
<div class="grille">{cartes}</div>
{bloc_produit(c, c.get('appel_accueil', c['texte_produit']))}
</section>"""
    (dossier / "index.html").write_text(
        page(lang, c["nom_site"], c["accroche"], f"{lang}/", corps, "../", type_og="website"), encoding="utf-8")
    urls.insert(0, f"{BASE}/{lang}/")

    if "methode" in c:
        me = c["methode"]
        corps = f"""<article class="article">
<p class="surtitre">Joli Plan</p>
<h1>{e(me['titre'])}</h1>
{''.join(f'<p>{e(p)}</p>' for p in me['paragraphes'])}
{bloc_produit(c, me.get('appel', c['texte_produit']))}
<p class="retour"><a href="../">← {e(m['tous'])}</a></p>
</article>"""
        (dossier / "methode").mkdir(parents=True, exist_ok=True)
        (dossier / "methode" / "index.html").write_text(
            page(lang, me["titre"], me["description"], f"{lang}/methode/", corps, "../../", type_og="website"),
            encoding="utf-8")
        urls.append(f"{BASE}/{lang}/methode/")

    if "gratuit" in c:
        g = c["gratuit"]
        fichier = RACINE / "blog" / "fichiers" / g["fichier"]
        (SORTIE / "fichiers").mkdir(parents=True, exist_ok=True)
        shutil.copy2(fichier, SORTIE / "fichiers" / g["fichier"])
        corps = f"""<article class="article">
<p class="surtitre">{e(g['surtitre'])}</p>
<h1>{e(g['titre'])}</h1>
<p class="chapeau">{e(g['intro'])}</p>
<p><a class="bouton bouton-vert" href="../../fichiers/{e(g['fichier'])}" download>{e(g['cta_telecharger'])}</a></p>
<h2>{e(g['titre_contenu'])}</h2>
<ul>{''.join(f'<li>{e(x)}</li>' for x in g['contenu'])}</ul>
<h2>{e(g['titre_complet'])}</h2>
<p>{e(g['texte_complet'])}</p>
{bloc_produit(c, g['appel'])}
<p class="retour"><a href="../">← {e(m['tous'])}</a></p>
</article>"""
        (dossier / g["slug"]).mkdir(parents=True, exist_ok=True)
        (dossier / g["slug"] / "index.html").write_text(
            page(lang, g["titre"], g["description"], f"{lang}/{g['slug']}/", corps, "../../", type_og="website"),
            encoding="utf-8")
        urls.append(f"{BASE}/{lang}/{g['slug']}/")
    return urls


def main():
    (SORTIE / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(RACINE / "blog" / "style.css", SORTIE / "assets" / "style.css")
    shutil.copy2(RACINE / "blog" / "icone.png", SORTIE / "assets" / "icone.png")
    urls = []
    for f in sorted(CONTENU.glob("*.json")):
        urls += construire_langue(json.loads(f.read_text(encoding="utf-8")))
    (SORTIE / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=fr/">'
        '<meta name="google-site-verification" content="G9rWwfYWoguup7oxZGhsrxkV0AbY1BA-Clq9PowUfEY" /><meta name="google-site-verification" content="MfwLf_DihL9en-TvD3F2wiAyQQc6AC1-1RUfTC8c9nc" />'
        '<link rel="canonical" href="' + BASE + '/fr/"><title>Joli Plan</title>', encoding="utf-8")
    (SORTIE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (SORTIE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    (SORTIE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"{len(urls)} pages générées dans {SORTIE}")


if __name__ == "__main__":
    main()
