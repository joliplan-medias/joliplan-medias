# Blog Joli Plan · méthode

Site : https://joliplanstudio.fr/ (GitHub Pages, branche main, dossier /docs).
Générateur : `python3 -I blog/build.py` lit `blog/contenu/<langue>.json` et écrit `docs/`. Ne jamais modifier `docs/` à la main.
Charte : fond crème FAF6F1, vert 46573F, rose 9B4B5A, poudre EAC8C4 ; titres EB Garamond, texte Lato (voir `blog/style.css`).

## Langues et liens Etsy (toujours le lien du même pays)
- fr : https://joliplanstudio.etsy.com/fr/listing/4601909838/planificateur-de-mariage-excel-en · images `pins/`
- de : https://joliplanstudio.etsy.com/fr/listing/4601915163/mariage-en-allemagne-tableur-en-allemand · `pins-de/`
- es : https://joliplanstudio.etsy.com/fr/listing/4601934679/mariage-en-espagne-tableur-en-espagnol · `pins-es/`
- it : https://joliplanstudio.etsy.com/fr/listing/4601940305/mariage-en-italie-tableur-en-italien · `pins-it/`
- uk : https://joliplanstudio.etsy.com/fr/listing/4602243958/uk-wedding-planner-spreadsheet-excel · `pins-uk/`

## Un article
- Format : voir `blog/contenu/fr.json` (champs slug, date, categorie, titre, description, image, image_alt, intro, sections, appel). Types de section : paragraphes, liste, liste_numerotee, etapes, citation, tableau. Toujours 2 questions dans "faq" (réponses courtes, tirées de l'article). "maj" = date de mise à jour quand on corrige un article.
- Par langue : "methode" (page Notre méthode, traduite de fr.json) et, si un fichier gratuit existe pour la langue dans blog/fichiers/, "gratuit" (même structure que fr.json). Ne jamais proposer en téléchargement un fichier d'une autre langue.
- Chaque semaine, si des articles existants n'ont pas de "faq" ou si la langue n'a pas de "methode", les ajouter (avec la même relecture).
- Sujet : une épingle déjà publiée et vérifiée de la même langue (textes dans /mnt/project-files/visuels/ et /mnt/project-files/video/*/TEXT*-EPINGLES-*.md, JSON dans /mnt/project-files/visuels/sources/). L'image de l'article = cette épingle (fichier du dossier pins de la langue). Jamais deux articles sur la même épingle.
- 300 à 700 mots, utile seul (la réponse complète, pas un teaser). Chiffres repris exactement de l'épingle ou de l'exemple rempli du tableur. Démarches administratives : uniquement ce qui est vérifié sur la source officielle du pays, citée dans un paragraphe « Source ».
- Mots interdits (METHODE-VIDEOS.md §5) : faux avis, étoiles, « best-seller », remboursement, garanties, promesses impossibles, « gratis/offert » pour un bonus (dire « inclus »), « moyenne/Durchschnitt » sans source, « avertit/warnt ». Pas de prix dans l'article.
- Slug : mots-clés dans la langue de l'article, minuscules, tirets, sans accents.
- Relecture : 2 sous-agents indépendants (langue ; faits/sources) pour chaque langue autre que le français, appliquer leurs corrections.

## Référencement (étude du 25/10/2026)
- Titre ≤ 60 caractères, mot-clé de la vraie recherche en tête (ex. « Budget mariage 100 personnes : … », « Hochzeit Checkliste : … »). Description ≤ 155 caractères.
- Les gens cherchent surtout « modèle/tableau Excel gratuit » et « budget N personnes/invités ». Préférer ces sujets aux démarches administratives (dominées par les mairies et administrations).
- Pages « budget » : reprendre exactement les chiffres d'une épingle budget vérifiée de la langue (jamais inventer). Un tableau différent par page.
- Ne jamais retirer la balise google-site-verification de build.py (Search Console validée le 25/10/2026).

## Cadence
- Démarrage d'une langue : 5 articles. Ensuite 1 article par langue et par semaine.
- Google pénalise les pages en masse quasi identiques : chaque article répond à une question différente.

## Contrôle avant push
1. `python3 -I blog/build.py` sans erreur.
2. Capture Playwright en 390 px de large de chaque nouvelle page, regardée avec Read : rien de coupé, charte respectée.
3. Commit + push sur main, puis WebFetch de l'URL publique de chaque nouvel article (le proxy bloque curl vers github.io).
