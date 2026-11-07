"""Génère le blog Joli Plan (site statique) dans docs/ à partir de blog/contenu/<langue>.json.

Usage : python3 -I blog/build.py
Charte : fond crème FAF6F1, vert 46573F, rose 9B4B5A, poudre EAC8C4 ; titres EB Garamond, texte Lato.
Champs facultatifs d'une langue : "methode" (page Notre méthode), "gratuit" (page de téléchargement),
"legal" ({"mentions": {slug, lien, titre, description, paragraphes}, "confidentialite": {...}} : pages + liens du pied de page ; le pop-up MAIL10 ne s'affiche que si "confidentialite" existe).
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
import hashlib
VERSION_CSS = hashlib.md5((RACINE_BLOG := __import__("pathlib").Path(__file__).resolve().parent).joinpath("style.css").read_bytes()).hexdigest()[:8]
PIN_SVG = '<svg class="ico-pin" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z"/></svg>'
YOUTUBE = "https://www.youtube.com/@JoliPlan"
YT_LIBELLE = {"fr": "Suivre sur YouTube", "de": "Auf YouTube folgen", "es": "Seguir en YouTube", "it": "Seguici su YouTube", "uk": "Follow on YouTube"}
YT_SVG = '<svg class="ico-yt" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.500 0-9.400.5A3 3 0 0 0 .5 6.200C0 8.100 0 12 0 12s0 3.900.5 5.800a3 3 0 0 0 2.100 2.100c1.900.5 9.400.5 9.400.5s7.500 0 9.400-.5a3 3 0 0 0 2.100-2.100c.5-1.900.5-5.800.5-5.800s0-3.900-.5-5.800zM9.600 15.600V8.400l6.200 3.600-6.200 3.600z"/></svg>'
TIKTOK = {"fr": "https://www.tiktok.com/@joliplan"}
TT_SVG = '<svg class="ico-tt" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>'
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

CONTACT = "joliplan.contact@gmail.com"
POPUP = {
    "fr": {"titre": "-10 % sur votre organisateur de mariage", "texte": "Laissez votre e-mail : nous vous envoyons le code MAIL10 pour la boutique Etsy Joli Plan.", "champ": "Votre e-mail", "bouton": "Recevoir mon code", "consent": "J'accepte de recevoir mon code par e-mail et que mon adresse soit utilisée à cette seule fin.", "lien": "Confidentialité", "fermer": "Fermer", "sujet": "Code MAIL10", "corps": "Bonjour, je souhaite recevoir le code MAIL10 (-10 %). Mon e-mail : "},
    "de": {"titre": "10 % Rabatt auf Ihren Hochzeitsplaner", "texte": "Hinterlassen Sie Ihre E-Mail-Adresse: Wir senden Ihnen den Code MAIL10 für den Joli-Plan-Shop auf Etsy.", "champ": "Ihre E-Mail-Adresse", "bouton": "Code erhalten", "consent": "Ich bin damit einverstanden, den Code per E-Mail zu erhalten und dass meine Adresse nur dafür verwendet wird.", "lien": "Datenschutz", "fermer": "Schließen", "sujet": "Code MAIL10", "corps": "Guten Tag, ich möchte den Code MAIL10 (10 % Rabatt) erhalten. Meine E-Mail-Adresse: "},
    "es": {"titre": "10 % de descuento en tu planificador de boda", "texte": "Déjanos tu correo: te enviamos el código MAIL10 para la tienda Joli Plan en Etsy.", "champ": "Tu correo electrónico", "bouton": "Recibir mi código", "consent": "Acepto recibir mi código por correo y que mi dirección se use solo para ello.", "lien": "Privacidad", "fermer": "Cerrar", "sujet": "Código MAIL10", "corps": "Hola, quiero recibir el código MAIL10 (10 % de descuento). Mi correo: "},
    "it": {"titre": "10 % di sconto sul tuo organizer per il matrimonio", "texte": "Lascia la tua e-mail: ti inviamo il codice MAIL10 per il negozio Joli Plan su Etsy.", "champ": "La tua e-mail", "bouton": "Ricevi il mio codice", "consent": "Accetto di ricevere il codice via e-mail e che il mio indirizzo sia usato solo a questo scopo.", "lien": "Privacy", "fermer": "Chiudi", "sujet": "Codice MAIL10", "corps": "Buongiorno, vorrei ricevere il codice MAIL10 (10 % di sconto). La mia e-mail: "},
    "uk": {"titre": "10% off your wedding planner", "texte": "Leave your email and we will send you the code MAIL10 for the Joli Plan shop on Etsy.", "champ": "Your email", "bouton": "Send me my code", "consent": "I agree to receive my code by email and for my address to be used for that purpose only.", "lien": "Privacy policy", "fermer": "Close", "sujet": "Code MAIL10", "corps": "Hello, I would like to receive the code MAIL10 (10% off). My email: "},
}
POPUP_JS = """(function(){var b=document.getElementById('jp-popup');if(!b)return;var K='jp-popup-vu';
function vu(){try{return localStorage.getItem(K)}catch(x){return null}}
function marque(){try{localStorage.setItem(K,'1')}catch(x){}}
if(vu())return;var ouvert=false;
function ouvrir(){if(ouvert||vu())return;ouvert=true;b.hidden=false;var i=b.querySelector('input[type=email]');if(i)i.focus({preventScroll:true})}
function fermer(){b.hidden=true;marque()}
setTimeout(ouvrir,12000);
document.addEventListener('mouseout',function(ev){if(!ev.relatedTarget&&ev.clientY<=0)ouvrir()});
b.querySelector('.jp-x').addEventListener('click',fermer);
document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&!b.hidden)fermer()});
b.querySelector('form').addEventListener('submit',function(ev){ev.preventDefault();var f=ev.target;var m=f.email.value;
marque();b.hidden=true;location.href='mailto:'+f.dataset.a+'?subject='+encodeURIComponent(f.dataset.s)+'&body='+encodeURIComponent(f.dataset.c+m)});
})();"""


def bloc_popup(lang, rel, legal):
    """Pop-up -10 % (code MAIL10). N'apparaît que si la page de confidentialité existe dans la langue."""
    if "confidentialite" not in legal:
        return ""
    p = POPUP[lang]
    return f"""<div id="jp-popup" class="jp-popup" role="dialog" aria-modal="false" aria-labelledby="jp-popup-t" hidden>
<div class="jp-boite"><button type="button" class="jp-x" aria-label="{e(p['fermer'])}">×</button>
<p class="jp-titre" id="jp-popup-t">{e(p['titre'])}</p>
<p>{e(p['texte'])}</p>
<form data-a="{CONTACT}" data-s="{e(p['sujet'])}" data-c="{e(p['corps'])}">
<input type="email" name="email" required placeholder="{e(p['champ'])}" aria-label="{e(p['champ'])}" autocomplete="email">
<label class="jp-consent"><input type="checkbox" required> <span>{e(p['consent'])} <a href="{rel}{lang}/{legal['confidentialite']['slug']}/">{e(p['lien'])}</a></span></label>
<button type="submit" class="bouton bouton-vert">{e(p['bouton'])}</button></form></div></div>
<script>{POPUP_JS}</script>"""


def liens_legaux(lang, rel, legal):
    return "".join(f'<a class="lien-pied" href="{rel}{lang}/{legal[k]["slug"]}/">{e(legal[k]["lien"])}</a>'
                   for k in ("mentions", "confidentialite") if k in legal)


def page(lang, titre, description, chemin, corps, rel, image=None, schemas=(), type_og="article", legal=None):
    legal = legal or {}
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
<link rel="stylesheet" href="{rel}assets/style.css?v={VERSION_CSS}">
{ld}
</head>
<body>
<header class="entete"><a class="logo" href="{rel}{lang}/"><img src="{rel}assets/icone.png" alt="" width="34" height="34"><span><em>Joli</em> Plan</span></a><span class="reseaux"><a class="lien-pinterest" href="https://www.pinterest.com/{PINTEREST[lang]}/" rel="noopener" target="_blank">{PIN_SVG}<span>{e(m['pinterest'])}</span></a><a class="lien-youtube" href="{YOUTUBE}" rel="noopener" target="_blank">{YT_SVG}<span>{e(YT_LIBELLE[lang])}</span></a>{('<a class="lien-tiktok" href="' + TIKTOK[lang] + '" rel="noopener" target="_blank" ">' + TT_SVG + '<span>Suivre sur TikTok</span></a>') if lang in TIKTOK else ''}</span></header>
<main>
{corps}
</main>
<footer class="pied"><a class="logo" href="{rel}{lang}/"><img src="{rel}assets/icone.png" alt="" width="28" height="28"><span><em>Joli</em> Plan</span></a><a class="lien-pied" href="{rel}{lang}/methode/">{e(m['methode'])}</a><a class="lien-pied" href="https://www.pinterest.com/{PINTEREST[lang]}/" rel="noopener" target="_blank">{PIN_SVG} Pinterest</a><a class="lien-pied" href="{YOUTUBE}" rel="noopener" target="_blank">{YT_SVG} YouTube</a>{('<a class="lien-pied" href="' + TIKTOK[lang] + '" rel="noopener" target="_blank">' + TT_SVG + ' TikTok</a>') if lang in TIKTOK else ''}{liens_legaux(lang, rel, legal)}</footer>
{bloc_popup(lang, rel, legal)}
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
            page(lang, a["titre"], a["description"], chemin, corps, "../../", image_web(lang, a["image"]), schemas, legal=c.get("legal")),
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
        page(lang, c["nom_site"], c["accroche"], f"{lang}/", corps, "../", type_og="website", legal=c.get("legal")), encoding="utf-8")
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
            page(lang, me["titre"], me["description"], f"{lang}/methode/", corps, "../../", type_og="website", legal=c.get("legal")),
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
            page(lang, g["titre"], g["description"], f"{lang}/{g['slug']}/", corps, "../../", type_og="website", legal=c.get("legal")),
            encoding="utf-8")
        urls.append(f"{BASE}/{lang}/{g['slug']}/")
    legal = c.get("legal", {})
    for cle in ("mentions", "confidentialite"):
        if cle not in legal:
            continue
        L = legal[cle]
        corps = f"""<article class="article">
<p class="surtitre">Joli Plan</p>
<h1>{e(L['titre'])}</h1>
{''.join(f'<h2>{e(x[0])}</h2><p>{e(x[1])}</p>' if isinstance(x, list) else f'<p>{e(x)}</p>' for x in L['paragraphes'])}
<p class="retour"><a href="../">← {e(m['tous'])}</a></p>
</article>"""
        (dossier / L["slug"]).mkdir(parents=True, exist_ok=True)
        (dossier / L["slug"] / "index.html").write_text(
            page(lang, L["titre"], L["description"], f"{lang}/{L['slug']}/", corps, "../../", type_og="website", legal=legal),
            encoding="utf-8")
        urls.append(f"{BASE}/{lang}/{L['slug']}/")
    return urls


ETSY = {
    "fr": "https://joliplanstudio.etsy.com/fr/listing/4601909838/planificateur-de-mariage-excel-en",
    "de": "https://joliplanstudio.etsy.com/fr/listing/4601915163/mariage-en-allemagne-tableur-en-allemand",
    "es": "https://joliplanstudio.etsy.com/fr/listing/4601934679/mariage-en-espagne-tableur-en-espagnol",
    "it": "https://joliplanstudio.etsy.com/fr/listing/4601940305/mariage-en-italie-tableur-en-italien",
    "uk": "https://joliplanstudio.etsy.com/fr/listing/4602243958/uk-wedding-planner-spreadsheet-excel",
    "evjf": "https://joliplanstudio.etsy.com/fr/listing/4606707119/organisateur-de-mariage-kit-evjf-evg-o",
}
BOUTIQUE = "https://joliplanstudio.etsy.com"
ICONES = {
    "dl": '<path d="M12 3v12m0 0l-4-4m4 4l4-4M4 20h16"/>',
    "lock": '<rect x="5" y="11" width="14" height="9" rx="1"/><path d="M8 11V8a4 4 0 018 0v3"/>',
    "grid": '<rect x="4" y="4" width="16" height="16" rx="1"/><path d="M4 10h16M10 4v16"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
}


def icone(k):
    return f'<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONES[k]}</svg>'


def construire_accueil_fr(urls):
    """Nouvelle page d'accueil (racine du site), version française. Les autres langues gardent leur accueil actuel."""
    fr = json.loads((CONTENU / "fr.json").read_text(encoding="utf-8"))
    dest = SORTIE / "img" / "accueil"
    dest.mkdir(parents=True, exist_ok=True)
    for src in (RACINE / "blog" / "accueil").glob("*.jpg"):
        Image.open(src).convert("RGB").save(dest / (src.stem + ".webp"), "WEBP", quality=82)
    shutil.copy2(RACINE / "blog" / "home.css", SORTIE / "assets" / "home.css")
    css_v = hashlib.md5((RACINE / "blog" / "home.css").read_bytes()).hexdigest()[:8]
    langues = [("fr", "FR", "./"), ("de", "DE", "de/"), ("es", "ES", "es/"), ("it", "IT", "it/"), ("uk", "EN", "uk/")]
    sel = "".join(f'<a href="{h}" hreflang="{LANG_HTML[c]}" lang="{LANG_HTML[c]}"{" aria-current=\"page\"" if c == "fr" else ""}>{l}</a>' for c, l, h in langues)
    cartes = [
        ("france", "Français", "France", "fr"), ("allemagne", "Deutsch", "Deutschland", "de"), ("espagne", "Español", "España", "es"),
        ("italie", "Italiano", "Italia", "it"), ("uk", "English", "United Kingdom", "uk"), ("evjf", "Français", "EVJF · EVG", "evjf"),
    ]
    html_cartes = "".join(
        f'<a class="pays" href="{ETSY[k]}" target="_blank" rel="noopener"><img src="img/accueil/{img}.webp" alt="" width="720" height="900" loading="lazy">'
        f'<div><small>{lg}</small><h3>{nom}</h3><span>Voir sur Etsy</span></div></a>' for img, lg, nom, k in cartes)
    arts = fr["articles"][:3]
    html_j = "".join(
        f'<a href="fr/{a["slug"]}/"><img src="{image_web("fr", a["image"])}" alt="{e(a["image_alt"])}" width="800" height="1200" loading="lazy">'
        f'<small>{e(a["categorie"])}</small><h3>{e(a["titre"])}</h3></a>' for a in arts)
    feuille = ("""<div class="sh" aria-hidden="true"><div class="t"><small>SAMEDI 12 JUIN 2027</small><b>Le mariage de Camille &amp; Julien</b><span>238 jours</span></div>
<div class="k"><div><small>BUDGET RÉGLÉ</small><em>26 %</em><i>7 650 € sur 29 159 €</i></div><div class="r"><small>INVITÉS CONFIRMÉS</small><em>24 / 30</em><i>5 en attente</i></div><div><small>PRÉPARATIFS</small><em>18 %</em><i>14 étapes sur 80</i></div><div><small>PROCHAIN PAIEMENT</small><em>08/10/2026</em><i>480 € à régler</i></div></div>
<div class="c"><div><h6>Cette semaine : 3 choses seulement</h6><p>Envoyer les pré-faire-part <span>15/09</span></p><p>Visite du lieu <span>20/09</span></p><p>Créer la page du mariage <span>05/10</span></p></div>
<div><h6>Prochains paiements</h6><p>Les Jardins d'Iris <b>480 €</b></p><p>Saveurs &amp; Sens <b>2 750 €</b></p><p>Château des Tilleuls <b>3 800 €</b></p></div></div></div>""")
    lignes = [("Lieu de réception", "5 500 à 6 500 € pour 100 invités", "5 100 €", "5 500 €"), ("Traiteur &amp; boissons", "110 € par invité, boissons comprises", "10 200 €", "8 250 €"),
              ("Photographe", "800 à 3 500 € ; souvent 1 300 €", "1 300 €", "1 900 €"), ("Fleurs &amp; décoration", "300 à 2 500 € ; souvent 950 €", "1 120 €", "—"),
              ("Robe &amp; accessoires", "300 à 3 000 € ; souvent 1 650 €", "1 400 €", "1 700 €"), ("Faire-part &amp; papeterie", "150 à 800 € ; souvent 425 €", "516 €", "540 €")]
    budget = ('<div class="sh bud" aria-hidden="true"><div class="t"><b>Budget</b></div><div class="tbl"><table><tr><th>Poste</th><th>Prix courant en France</th><th>Conseillé</th><th>Prévu</th></tr>'
              + "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in lignes) + "</table></div></div>")
    titre = "Planificateur de mariage Excel et Google Sheets | Joli Plan"
    desc = "Planificateur de mariage en Excel et Google Sheets : budget, invités, mairie et planning du jour J. Un fichier pour chaque pays, avec exemple rempli."
    schema = {"@context": "https://schema.org", "@type": "Organization", "name": "Joli Plan", "url": BASE + "/", "logo": BASE + "/assets/icone.png",
              "sameAs": [BOUTIQUE, "https://www.pinterest.com/joliplan/", YOUTUBE]}
    page_html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="G9rWwfYWoguup7oxZGhsrxkV0AbY1BA-Clq9PowUfEY" />
<meta name="google-site-verification" content="MfwLf_DihL9en-TvD3F2wiAyQQc6AC1-1RUfTC8c9nc" />
<title>{e(titre)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}/">
<meta property="og:title" content="{e(titre)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE}/">
<meta property="og:image" content="{BASE}/img/accueil/france.webp">
<link rel="icon" href="assets/icone.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=EB+Garamond:ital,wght@0,400;0,500;1,500&family=Jost:wght@300;400;500&family=Lato:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/home.css?v={css_v}">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
<div class="bandeau">Planificateurs de mariage Excel &amp; Google Sheets · Téléchargement immédiat</div>
<div class="w"><nav class="nav"><a class="logo" href="./"><img src="assets/icone.png" alt="" width="36" height="36"><span><em>Joli</em> <b>Plan</b></span></a>
<ul class="menu"><li><a href="#collection">Planificateurs</a></li><li><a href="#budget">Le fichier</a></li><li><a href="fr/">Journal</a></li><li><a href="fr/methode/">Notre méthode</a></li></ul>
<div class="droite"><div class="langues" aria-label="Langue">{sel}</div><a class="btn petit" href="{ETSY['fr']}" target="_blank" rel="noopener">Etsy</a></div></nav></div>
<main>
<div class="w"><div class="hero"><div><div class="kicker">Planificateur de mariage · France</div><h1>Votre mariage,<br><i>enfin simple.</i></h1>
<p>Budget, invités, démarches de mairie et planning du jour J, réunis dans un seul fichier élégant, pensé pour les traditions françaises.</p>
<div class="actions"><a class="btn" href="{ETSY['fr']}" target="_blank" rel="noopener">Découvrir le planificateur</a><a class="btn clair" href="#budget">Voir un aperçu</a></div>
<ul class="mini"><li>Exemple rempli inclus</li><li>Service client en français</li></ul></div>
<div class="ordi"><div class="ecran">{feuille}</div><div class="socle"></div></div></div></div>
<div class="confiance"><div class="w"><div>{icone('dl')}<span><b>Immédiat</b>Téléchargement après l'achat</span></div><div>{icone('lock')}<span><b>Sécurisé</b>Paiement protégé par Etsy</span></div><div>{icone('grid')}<span><b>Compatible</b>Excel et Google Sheets</span></div><div>{icone('chat')}<span><b>Humain</b>Service client en français</span></div></div></div>
<section id="budget"><div class="w"><div class="deux"><div><div class="kicker">Le budget</div><h2>Il se calcule <i>tout seul.</i></h2>
<p>Pour chaque poste, les prix courants en France et un budget conseillé. Vous saisissez vos devis, le reste se met à jour.</p>
<ul class="liste"><li><b>1</b>21 postes, du lieu aux alliances</li><li><b>2</b>L'écart avec votre budget global, en direct</li><li><b>3</b>Acomptes et soldes datés</li></ul></div>{budget}</div></div></section>
<section class="alt centre"><div class="w"><div class="kicker">Pourquoi Joli Plan</div><h2>Pensé pour la France, <i>pas traduit.</i></h2>
<div class="cmp"><div><h3>Un modèle traduit</h3><p>Dates à l'américaine</p><p>Aucune démarche de mairie</p><p>Ni vin d'honneur, ni brunch</p><p>Prix d'un autre pays</p></div>
<div class="oui"><h3>Joli Plan</h3><p>Dates jj/mm/aaaa, montants en euros</p><p>Dossier de mairie pas à pas</p><p>Vin d'honneur, brunch, témoins</p><p>Prix courants en France par poste</p></div></div></div></section>
<section id="collection" class="centre"><div class="w"><div class="kicker">La collection</div><h2>Un planificateur <i>par pays</i></h2><div class="cartes">{html_cartes}</div></div></section>
<section class="alt centre"><div class="w"><div class="kicker">Mode d'emploi</div><h2>Prêt en <i>3 étapes</i></h2>
<div class="etapes"><div><em>1</em><h3>Téléchargez</h3><p>Le fichier est à vous dès l'achat.</p></div><div><em>2</em><h3>Ouvrez</h3><p>Dans Excel ou Google Sheets, sur ordinateur, tablette ou téléphone.</p></div><div><em>3</em><h3>Remplissez</h3><p>Écrivez dans les cases blanches, le reste se calcule.</p></div></div></div></section>
<section><div class="w"><div class="entete-j"><div><div class="kicker">Le journal</div><h2 style="margin-bottom:0">Des réponses, <i>simplement</i></h2></div><a class="btn clair petit" href="fr/" style="margin:0">Tous les articles</a></div><div class="journal">{html_j}</div></div></section>
<section class="final centre"><div class="w"><div class="kicker">Votre plus beau jour</div><h2>Profitez, <i>tout est prêt.</i></h2><a class="btn" href="{ETSY['fr']}" target="_blank" rel="noopener">Découvrir le planificateur</a></div></section>
</main>
<footer class="pied"><div class="w"><div class="g"><div><a class="logo" href="./"><img src="assets/icone.png" alt="" width="36" height="36"><span><em>Joli</em> <b>Plan</b></span></a><p style="max-width:280px;line-height:1.7">Planificateurs de mariage premium, adaptés aux coutumes de chaque pays.</p></div>
<div><h4>Planificateurs</h4><a href="{ETSY['fr']}" target="_blank" rel="noopener">France</a><a href="{ETSY['de']}" target="_blank" rel="noopener">Deutschland</a><a href="{ETSY['es']}" target="_blank" rel="noopener">España</a><a href="{ETSY['it']}" target="_blank" rel="noopener">Italia</a><a href="{ETSY['uk']}" target="_blank" rel="noopener">United Kingdom</a></div>
<div><h4>Suivre</h4><a href="https://www.pinterest.com/joliplan/" target="_blank" rel="noopener">Pinterest</a><a href="{YOUTUBE}" target="_blank" rel="noopener">YouTube</a><a href="{TIKTOK['fr']}" target="_blank" rel="noopener">TikTok</a><a href="{BOUTIQUE}" target="_blank" rel="noopener">Boutique Etsy</a></div>
<div><h4>Infos</h4><a href="fr/methode/">Notre méthode</a><a href="fr/">Journal</a>{liens_legaux("fr", "", fr.get("legal", {})).replace('class="lien-pied" ', "")}</div></div>
<div class="copy"><span>© 2026 Joli Plan</span><span>FR · DE · ES · IT · EN</span></div></div></footer>
</body>
</html>
"""
    (SORTIE / "index.html").write_text(page_html, encoding="utf-8")
    urls.insert(0, BASE + "/")


def main():
    (SORTIE / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(RACINE / "blog" / "style.css", SORTIE / "assets" / "style.css")
    shutil.copy2(RACINE / "blog" / "icone.png", SORTIE / "assets" / "icone.png")
    urls = []
    for f in sorted(CONTENU.glob("*.json")):
        urls += construire_langue(json.loads(f.read_text(encoding="utf-8")))
    construire_accueil_fr(urls)
    (SORTIE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (SORTIE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    (SORTIE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"{len(urls)} pages générées dans {SORTIE}")


if __name__ == "__main__":
    main()
