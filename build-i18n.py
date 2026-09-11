# -*- coding: utf-8 -*-
"""Génère les versions EN/DE/NL/IT du site à partir de site/index.html (FR,
source de vérité). Remplacement de chaînes exactes (espaces/retours à la
ligne tolérés), tri par longueur décroissante pour éviter les collisions de
sous-chaînes. Toute chaîne du dictionnaire introuvable fait échouer le build :
si la page FR évolue, la table doit suivre.

Usage : python build-i18n.py
Sortie : site/en/index.html, site/de/index.html, site/nl/index.html,
         site/it/index.html (commitées — le Dockerfile ne fait que copier).
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "site", "index.html")
LANGS = ["en", "de", "nl", "it"]

# { chaîne FR : (EN, DE, NL, IT) }
TR = {
  # ---- head ----
  "EE911 — Plans d'évacuation et d'intervention conformes, en ligne": (
    "EE911 — Compliant evacuation and fire response plans, online",
    "EE911 — Normgerechte Flucht- und Feuerwehrpläne, online",
    "EE911 — Conforme ontruimings- en interventieplannen, online",
    "EE911 — Piani di evacuazione e di intervento conformi, online"),
  "Créez vos plans d'évacuation et plans d'intervention conformes (NF X 08-070, ISO 23601, DIN 14095) dans votre navigateur : import photo intelligent, DXF/DWG, pictogrammes ISO 7010, export PDF. Offre découverte gratuite.": (
    "Create compliant evacuation and fire response plans (ISO 23601, DIN 14095) in your browser: smart photo import, DXF/DWG, ISO 7010 pictograms, PDF export. Free starter offer.",
    "Erstellen Sie normgerechte Flucht- und Rettungspläne sowie Feuerwehrpläne (ISO 23601, DIN 14095, ASR A2.3) im Browser: intelligenter Foto-Import, DXF/DWG, ISO-7010-Piktogramme, PDF-Export. Kostenloses Einstiegsangebot.",
    "Maak conforme ontruimings- en interventieplannen (ISO 23601, NEN 1414) in uw browser: slimme foto-import, DXF/DWG, ISO 7010-pictogrammen, PDF-export. Gratis kennismakingsaanbod.",
    "Crea piani di evacuazione e piani di intervento conformi (ISO 23601) nel browser: importazione foto intelligente, DXF/DWG, pittogrammi ISO 7010, esportazione PDF. Offerta di prova gratuita."),
  "EE911 — Plans d'évacuation conformes, en ligne": (
    "EE911 — Compliant evacuation plans, online",
    "EE911 — Normgerechte Fluchtpläne, online",
    "EE911 — Conforme ontruimingsplannen, online",
    "EE911 — Piani di evacuazione conformi, online"),
  "L'éditeur en ligne des plans d'évacuation et d'intervention. Import photo et DWG, socle ISO 23601 adapté pays par pays, export PDF. Gratuit pour démarrer : 1 site, 5 étages.": (
    "The online editor for evacuation and fire response plans. Photo and DWG import, ISO 23601 base adapted country by country, PDF export. Free to start: 1 site, 5 floors.",
    "Der Online-Editor für Flucht- und Feuerwehrpläne. Foto- und DWG-Import, ISO-23601-Basis je Land angepasst, PDF-Export. Kostenlos starten: 1 Standort, 5 Etagen.",
    "De online editor voor ontruimings- en interventieplannen. Foto- en DWG-import, ISO 23601-basis per land aangepast, PDF-export. Gratis starten: 1 locatie, 5 verdiepingen.",
    "L'editor online dei piani di evacuazione e di intervento. Import di foto e DWG, base ISO 23601 adattata paese per paese, esportazione PDF. Inizio gratuito: 1 sito, 5 piani."),
  # ---- topbar ----
  "Fonctionnalités": ("Features", "Funktionen", "Functies", "Funzionalità"),
  "Conformité": ("Compliance", "Normkonformität", "Conformiteit", "Conformità"),
  "Offres": ("Pricing", "Angebote", "Aanbod", "Offerte"),
  "Se connecter": ("Log in", "Anmelden", "Inloggen", "Accedi"),
  "Créer un compte": ("Create an account", "Konto erstellen", "Account aanmaken", "Crea un account"),
  # ---- hero ----
  "Sécurité incendie · Obligation réglementaire": (
    "Fire safety · Regulatory requirement",
    "Brandschutz · Gesetzliche Pflicht",
    "Brandveiligheid · Wettelijke verplichting",
    "Sicurezza antincendio · Obbligo normativo"),
  "Vos plans d'évacuation, conformes et à jour,<br>sans bureau d'études.": (
    "Your evacuation plans, compliant and up to date,<br>without an engineering firm.",
    "Ihre Fluchtpläne — normgerecht und aktuell,<br>ohne Planungsbüro.",
    "Uw ontruimingsplannen, conform en actueel,<br>zonder studiebureau.",
    "I vostri piani di evacuazione, conformi e aggiornati,<br>senza studio tecnico."),
  "EE911 est l'éditeur en ligne des plans d'évacuation et des plans d'intervention. Photographiez un plan existant ou importez votre DWG : l'application reconstruit les murs, les portes et les pictogrammes, vous ajustez, vous exportez en PDF prêt à afficher.": (
    "EE911 is the online editor for evacuation and fire response plans. Photograph an existing plan or import your DWG: the app rebuilds walls, doors and pictograms — you adjust, you export a display-ready PDF.",
    "EE911 ist der Online-Editor für Flucht- und Rettungspläne sowie Feuerwehrpläne. Fotografieren Sie einen bestehenden Plan oder importieren Sie Ihre DWG: Die Anwendung rekonstruiert Wände, Türen und Piktogramme — Sie passen an und exportieren ein aushangfertiges PDF.",
    "EE911 is de online editor voor ontruimings- en interventieplannen. Fotografeer een bestaand plan of importeer uw DWG: de applicatie reconstrueert muren, deuren en pictogrammen — u past aan en exporteert een ophangklare PDF.",
    "EE911 è l'editor online dei piani di evacuazione e di intervento. Fotografate una planimetria esistente o importate il vostro DWG: l'applicazione ricostruisce muri, porte e pittogrammi — voi rifinite ed esportate un PDF pronto da affiggere."),
  "votre@email-professionnel.fr": ("your@work-email.com", "ihre@firmen-mail.de", "uw@zakelijke-mail.nl", "vostra@email-aziendale.it"),
  "Adresse e-mail": ("Email address", "E-Mail-Adresse", "E-mailadres", "Indirizzo e-mail"),
  "Créer mon compte": ("Create my account", "Mein Konto erstellen", "Mijn account aanmaken", "Crea il mio account"),
  "Offre découverte : 1 site et 5 étages inclus, sans carte bancaire.": (
    "Starter offer: 1 site and 5 floors included, no credit card required.",
    "Einstiegsangebot: 1 Standort und 5 Etagen inklusive, ohne Kreditkarte.",
    "Kennismakingsaanbod: 1 locatie en 5 verdiepingen inbegrepen, zonder creditcard.",
    "Offerta di prova: 1 sito e 5 piani inclusi, senza carta di credito."),
  # ---- vignette SVG ----
  "PLAN D'ÉVACUATION": ("EVACUATION PLAN", "FLUCHT- UND RETTUNGSPLAN", "ONTRUIMINGSPLAN", "PIANO DI EVACUAZIONE"),
  "Bâtiment A · Niveau 1 · Éch. 1:200": (
    "Building A · Level 1 · Scale 1:200", "Gebäude A · Ebene 1 · M. 1:200",
    "Gebouw A · Niveau 1 · Schaal 1:200", "Edificio A · Piano 1 · Scala 1:200"),
  "Escalier d'évacuation": ("Escape stairs", "Nottreppe", "Vluchttrap", "Scala di emergenza"),
  "Escalier": ("Stairs", "Treppe", "Trap", "Scala"),
  "Bureaux 101–102": ("Offices 101–102", "Büros 101–102", "Kantoren 101–102", "Uffici 101–102"),
  "Bureaux 103–104": ("Offices 103–104", "Büros 103–104", "Kantoren 103–104", "Uffici 103–104"),
  "Salle de réunion": ("Meeting room", "Besprechungsraum", "Vergaderzaal", "Sala riunioni"),
  "Sanitaires": ("Restrooms", "Sanitärräume", "Sanitair", "Servizi"),
  "Open space": ("Open plan", "Großraumbüro", "Kantoortuin", "Open space"),
  "Local technique": ("Utility room", "Technikraum", "Technische ruimte", "Locale tecnico"),
  "Accueil": ("Reception", "Empfang", "Receptie", "Reception"),
  "POINT DE RASSEMBLEMENT": ("ASSEMBLY POINT", "SAMMELSTELLE", "VERZAMELPLAATS", "PUNTO DI RACCOLTA"),
  "LÉGENDE": ("LEGEND", "LEGENDE", "LEGENDA", "LEGENDA"),
  "Issue de secours": ("Emergency exit", "Notausgang", "Nooduitgang", "Uscita di emergenza"),
  "Extincteur": ("Fire extinguisher", "Feuerlöscher", "Brandblusser", "Estintore"),
  "RIA": ("Fire hose reel", "Wandhydrant", "Brandslanghaspel", "Naspo"),
  "Alarme incendie": ("Fire alarm", "Brandmelder", "Brandmelder", "Allarme antincendio"),
  "Premiers secours": ("First aid", "Erste Hilfe", "EHBO", "Primo soccorso"),
  "Rassemblement": ("Assembly point", "Sammelstelle", "Verzamelplaats", "Punto di raccolta"),
  "Vous êtes ici": ("You are here", "Sie sind hier", "U bent hier", "Voi siete qui"),
  "Cheminement": ("Escape route", "Fluchtweg", "Vluchtroute", "Percorso di esodo"),
  "Compartimentage": ("Fire compartment", "Brandabschnitt", "Brandcompartiment", "Compartimentazione"),
  "Conforme NF X 08-070": ("ISO 23601 compliant", "Nach DIN ISO 23601", "Conform ISO 23601 / NEN 1414", "Conforme ISO 23601"),
  "ACCIDENT": ("ACCIDENT", "UNFALL", "ONGEVAL", "INFORTUNIO"),
  "Prévenez les secours": ("Call emergency services", "Notruf absetzen", "Waarschuw de hulpdiensten", "Chiamate i soccorsi"),
  "Tél : 15 · 18 · 112": ("Tel: 112", "Tel.: 112", "Tel.: 112", "Tel: 112 · 118"),
  "INCENDIE": ("FIRE", "BRAND", "BRAND", "INCENDIO"),
  "Déclenchez l'alarme": ("Sound the alarm", "Alarm auslösen", "Sla alarm", "Attivate l'allarme"),
  "Attaquez le feu": ("Fight the fire", "Feuer bekämpfen", "Blus de brand", "Spegnete il fuoco"),
  "sans prendre de risque": ("without taking risks", "ohne Eigengefährdung", "zonder risico te nemen", "senza correre rischi"),
  "ÉVACUATION": ("EVACUATION", "FLUCHT", "ONTRUIMING", "EVACUAZIONE"),
  "Évacuez calmement": ("Evacuate calmly", "Ruhig bleiben", "Ontruim rustig", "Evacuate con calma"),
  "Pas d'ascenseur": ("Do not use lifts", "Keine Aufzüge benutzen", "Geen lift gebruiken", "Non usate l'ascensore"),
  "Point de rassemblement": ("Go to the assembly point", "Sammelstelle aufsuchen", "Naar de verzamelplaats", "Al punto di raccolta"),
  "Mise à jour : 09/2026": ("Updated: 09/2026", "Stand: 09/2026", "Bijgewerkt: 09/2026", "Aggiornato: 09/2026"),
  "Urgences : 18 · 112": ("Emergency: 112", "Notruf: 112", "Noodnummer: 112", "Emergenze: 112 · 115"),
  "Généré avec EE911 — map.ee911.eu": (
    "Generated with EE911 — map.ee911.eu", "Erstellt mit EE911 — map.ee911.eu",
    "Gemaakt met EE911 — map.ee911.eu", "Generato con EE911 — map.ee911.eu"),
  # ---- bandeau normes ----
  "Socle <strong>ISO 23601</strong> — la norme internationale des plans d'évacuation": (
    "Built on <strong>ISO 23601</strong> — the international standard for evacuation plans",
    "Basis <strong>ISO 23601</strong> — die internationale Norm für Fluchtpläne",
    "Basis <strong>ISO 23601</strong> — de internationale norm voor ontruimingsplannen",
    "Base <strong>ISO 23601</strong> — la norma internazionale dei piani di evacuazione"),
  "Plans d'évacuation <strong>et</strong> plans d'intervention": (
    "Evacuation <strong>and</strong> fire response plans",
    "Flucht- <strong>und</strong> Feuerwehrpläne",
    "Ontruimings- <strong>en</strong> interventieplannen",
    "Piani di evacuazione <strong>e</strong> piani di intervento"),
  "<strong>NF X 08-070</strong> · <strong>ASR A2.3 / DIN 14095</strong> · adaptations par pays": (
    "<strong>NF X 08-070</strong> · <strong>ASR A2.3 / DIN 14095</strong> · country-specific adaptations",
    "<strong>ASR A2.3 / DIN 14095</strong> · <strong>NF X 08-070</strong> · Anpassung je Land",
    "<strong>NEN 1414</strong> · <strong>NF X 08-070</strong> · aanpassing per land",
    "<strong>D.Lgs. 81/2008</strong> · <strong>NF X 08-070</strong> · adattamenti per paese"),
  # ---- fonctionnalités ----
  "Tout ce qu'un plan réglementaire exige, rien de superflu": (
    "Everything a regulatory plan requires, nothing superfluous",
    "Alles, was ein normgerechter Plan verlangt — nichts Überflüssiges",
    "Alles wat een regelgevend plan vereist, niets overbodigs",
    "Tutto ciò che un piano a norma richiede, niente di superfluo"),
  "📷 Import photo intelligent": ("📷 Smart photo import", "📷 Intelligenter Foto-Import", "📷 Slimme foto-import", "📷 Import foto intelligente"),
  "Photographiez le plan affiché dans votre bâtiment : l'analyse mesure les traits au pixel, reconstruit les murs et cloisons, détecte les portes et repère les pictogrammes existants. Vous obtenez un plan éditable, pas une image figée.": (
    "Photograph the plan displayed in your building: the analysis measures lines to the pixel, rebuilds walls and partitions, detects doors and locates existing pictograms. You get an editable plan, not a frozen image.",
    "Fotografieren Sie den ausgehängten Plan: Die Analyse vermisst Linien pixelgenau, rekonstruiert Wände und Trennwände, erkennt Türen und findet vorhandene Piktogramme. Sie erhalten einen bearbeitbaren Plan, kein starres Bild.",
    "Fotografeer het opgehangen plan: de analyse meet lijnen tot op de pixel, reconstrueert muren en wanden, detecteert deuren en herkent bestaande pictogrammen. U krijgt een bewerkbaar plan, geen star beeld.",
    "Fotografate la planimetria affissa nel vostro edificio: l'analisi misura i tratti al pixel, ricostruisce muri e tramezzi, rileva le porte e individua i pittogrammi esistenti. Ottenete un piano modificabile, non un'immagine statica."),
  "📐 Import DXF / DWG": ("📐 DXF / DWG import", "📐 DXF-/DWG-Import", "📐 DXF/DWG-import", "📐 Import DXF / DWG"),
  "Partez du plan de l'architecte : les calques utiles sont convertis en objets de l'éditeur, à l'échelle. Les gros fichiers sont pris en charge.": (
    "Start from the architect's drawing: the relevant layers are converted into editor objects, to scale. Large files are supported.",
    "Starten Sie vom Architektenplan: Die relevanten Layer werden maßstabsgetreu in Editor-Objekte umgewandelt. Große Dateien werden unterstützt.",
    "Vertrek van de architectuurtekening: de relevante lagen worden op schaal omgezet in editor-objecten. Grote bestanden worden ondersteund.",
    "Partite dal disegno dell'architetto: i layer utili sono convertiti in oggetti dell'editor, in scala. I file di grandi dimensioni sono supportati."),
  "🧰 Éditeur métier": ("🧰 Purpose-built editor", "🧰 Fachlicher Editor", "🧰 Vakgerichte editor", "🧰 Editor specializzato"),
  "Murs, portes, escaliers, cheminements d'évacuation, zones et compartiments, point « Vous êtes ici » : chaque objet est métier, duplicable et modifiable. Pictogrammes ISO 7010 intégrés.": (
    "Walls, doors, stairs, escape routes, zones and compartments, “You are here” marker: every object is domain-aware, duplicable and editable. ISO 7010 pictograms built in.",
    "Wände, Türen, Treppen, Fluchtwege, Zonen und Brandabschnitte, „Sie sind hier“-Punkt: Jedes Objekt ist fachlich, duplizierbar und editierbar. ISO-7010-Piktogramme integriert.",
    "Muren, deuren, trappen, vluchtroutes, zones en compartimenten, “U bent hier”-punt: elk object is vakspecifiek, dupliceerbaar en bewerkbaar. ISO 7010-pictogrammen ingebouwd.",
    "Muri, porte, scale, percorsi di esodo, zone e compartimenti, punto “Voi siete qui”: ogni oggetto è specializzato, duplicabile e modificabile. Pittogrammi ISO 7010 integrati."),
  "🗂️ Templates par typologie": ("🗂️ Templates by building type", "🗂️ Vorlagen je Gebäudetyp", "🗂️ Sjablonen per gebouwtype", "🗂️ Modelli per tipologia"),
  "Tour de bureaux, commerce, hôtel, site multi-zones, grand ERP, plan d'intervention : chaque template pré-remplit le cartouche, la légende et les réglages typiques — y compris les consignes particulières (hôtellerie).": (
    "Office tower, retail, hotel, multi-zone site, large public building, fire response plan: each template pre-fills the title block, the legend and the typical settings — including special instructions (hotels).",
    "Bürohochhaus, Handel, Hotel, Mehrzonen-Standort, große Versammlungsstätte, Feuerwehrplan: Jede Vorlage füllt Schriftfeld, Legende und typische Einstellungen vor — inklusive besonderer Hinweise (Hotellerie).",
    "Kantoortoren, winkel, hotel, multi-zone locatie, groot publiek gebouw, interventieplan: elk sjabloon vult het titelblok, de legenda en de typische instellingen vooraf in — inclusief bijzondere richtlijnen (hotels).",
    "Torre uffici, commercio, hotel, sito multi-zona, grande edificio pubblico, piano di intervento: ogni modello precompila il cartiglio, la legenda e le impostazioni tipiche — incluse le istruzioni particolari (hotel)."),
  "🚒 Plans d'intervention": ("🚒 Fire response plans", "🚒 Feuerwehrpläne", "🚒 Interventieplannen", "🚒 Piani di intervento"),
  "Le document destiné aux secours : SSI, coupures, vannes, accès pompiers, chargés d'intervention — avec sa mise en page dédiée, distincte du plan d'évacuation.": (
    "The document for emergency services: fire alarm system, shut-offs, valves, fire brigade access, response team — with its own layout, distinct from the evacuation plan.",
    "Das Dokument für die Einsatzkräfte: Brandmeldeanlage, Abschaltungen, Absperrventile, Feuerwehrzufahrt, Brandschutzhelfer — mit eigenem Layout, getrennt vom Fluchtplan.",
    "Het document voor de hulpdiensten: brandmeldcentrale, afsluitingen, afsluiters, brandweertoegang, interventieploeg — met een eigen lay-out, apart van het ontruimingsplan.",
    "Il documento per i soccorsi: impianto di rivelazione, sezionamenti, valvole, accesso dei vigili del fuoco, addetti antincendio — con impaginazione dedicata, distinta dal piano di evacuazione."),
  "🏢 Multi-sites, multi-étages": ("🏢 Multi-site, multi-floor", "🏢 Mehrere Standorte und Etagen", "🏢 Multi-locatie, multi-verdieping", "🏢 Multi-sito, multi-piano"),
  "Organisez sociétés, sites, bâtiments et étages ; composez un plan multi-emprises regroupant plusieurs niveaux sur une page. Invitez votre équipe avec des rôles (admin, éditeur, lecteur).": (
    "Organise companies, sites, buildings and floors; compose a multi-footprint plan grouping several levels on one page. Invite your team with roles (admin, editor, viewer).",
    "Organisieren Sie Unternehmen, Standorte, Gebäude und Etagen; erstellen Sie einen Mehrfach-Grundriss mit mehreren Ebenen auf einer Seite. Laden Sie Ihr Team mit Rollen ein (Admin, Editor, Leser).",
    "Organiseer bedrijven, locaties, gebouwen en verdiepingen; stel een plan samen met meerdere niveaus op één pagina. Nodig uw team uit met rollen (admin, editor, lezer).",
    "Organizzate società, siti, edifici e piani; componete un piano multi-impronta con più livelli su una pagina. Invitate il vostro team con ruoli (admin, editor, lettore)."),
  "📄 Export prêt à afficher": ("📄 Display-ready export", "📄 Aushangfertiger Export", "📄 Ophangklare export", "📄 Esportazione pronta da affiggere"),
  "PDF et PNG au format A3/A4, portrait ou paysage, avec cartouche réglementaire complet : consignes, point de rassemblement, légende, échelle, dates de conception et de mise à jour, coordonnées GPS.": (
    "PDF and PNG in A3/A4, portrait or landscape, with a complete regulatory title block: instructions, assembly point, legend, scale, design and update dates, GPS coordinates.",
    "PDF und PNG in A3/A4, Hoch- oder Querformat, mit vollständigem Schriftfeld: Verhaltensregeln, Sammelstelle, Legende, Maßstab, Erstellungs- und Aktualisierungsdatum, GPS-Koordinaten.",
    "PDF en PNG in A3/A4, staand of liggend, met volledig regelgevend titelblok: richtlijnen, verzamelplaats, legenda, schaal, ontwerp- en bijwerkdatum, GPS-coördinaten.",
    "PDF e PNG in A3/A4, verticale o orizzontale, con cartiglio normativo completo: istruzioni, punto di raccolta, legenda, scala, date di progettazione e aggiornamento, coordinate GPS."),
  "🔒 Sécurité": ("🔒 Security", "🔒 Sicherheit", "🔒 Beveiliging", "🔒 Sicurezza"),
  "Double authentification (TOTP) pour tous les comptes, données hébergées en Europe, aucun traceur tiers sur ce site.": (
    "Two-factor authentication (TOTP) for every account, data hosted in Europe, no third-party trackers on this site.",
    "Zwei-Faktor-Authentifizierung (TOTP) für alle Konten, Datenhaltung in Europa, keine Dritt-Tracker auf dieser Website.",
    "Tweefactorauthenticatie (TOTP) voor elk account, data gehost in Europa, geen trackers van derden op deze site.",
    "Autenticazione a due fattori (TOTP) per tutti gli account, dati ospitati in Europa, nessun tracker di terze parti su questo sito."),
  # ---- étapes ----
  "De la photo au plan affiché, en quatre étapes": (
    "From photo to displayed plan, in four steps",
    "Vom Foto zum ausgehängten Plan — in vier Schritten",
    "Van foto tot opgehangen plan, in vier stappen",
    "Dalla foto al piano affisso, in quattro passaggi"),
  "<strong>Créez votre compte</strong><span>Gratuit, avec votre e-mail professionnel.</span>": (
    "<strong>Create your account</strong><span>Free, with your work email.</span>",
    "<strong>Konto erstellen</strong><span>Kostenlos, mit Ihrer Firmen-E-Mail.</span>",
    "<strong>Maak uw account aan</strong><span>Gratis, met uw zakelijke e-mail.</span>",
    "<strong>Create il vostro account</strong><span>Gratuito, con la vostra e-mail aziendale.</span>"),
  "<strong>Décrivez votre site</strong><span>Société, bâtiment, étages — le cartouche s'en déduit.</span>": (
    "<strong>Describe your site</strong><span>Company, building, floors — the title block follows.</span>",
    "<strong>Standort beschreiben</strong><span>Unternehmen, Gebäude, Etagen — das Schriftfeld folgt daraus.</span>",
    "<strong>Beschrijf uw locatie</strong><span>Bedrijf, gebouw, verdiepingen — het titelblok volgt eruit.</span>",
    "<strong>Descrivete il vostro sito</strong><span>Società, edificio, piani — il cartiglio ne deriva.</span>"),
  "<strong>Importez ou dessinez</strong><span>Photo du plan existant, DWG, ou dessin direct dans l'éditeur.</span>": (
    "<strong>Import or draw</strong><span>Photo of the existing plan, DWG, or draw directly in the editor.</span>",
    "<strong>Importieren oder zeichnen</strong><span>Foto des bestehenden Plans, DWG oder direktes Zeichnen im Editor.</span>",
    "<strong>Importeer of teken</strong><span>Foto van het bestaande plan, DWG, of rechtstreeks tekenen in de editor.</span>",
    "<strong>Importate o disegnate</strong><span>Foto della planimetria esistente, DWG, o disegno diretto nell'editor.</span>"),
  "<strong>Exportez et affichez</strong><span>PDF conforme, à mettre à jour en deux clics à chaque changement.</span>": (
    "<strong>Export and display</strong><span>Compliant PDF, updated in two clicks whenever something changes.</span>",
    "<strong>Exportieren und aushängen</strong><span>Normgerechtes PDF, bei jeder Änderung in zwei Klicks aktualisiert.</span>",
    "<strong>Exporteer en hang op</strong><span>Conforme PDF, bij elke wijziging in twee klikken bijgewerkt.</span>",
    "<strong>Esportate e affiggete</strong><span>PDF conforme, aggiornabile in due clic a ogni modifica.</span>"),
  # ---- conformité ----
  "Conçu à partir des normes, pays par pays": (
    "Built from the standards, country by country",
    "Aus den Normen entwickelt — Land für Land",
    "Opgebouwd vanuit de normen, land per land",
    "Costruito a partire dalle norme, paese per paese"),
  "Le socle commun est l'ISO 23601, la norme internationale des plans d'évacuation. Par-dessus, EE911 adapte le cartouche, les mentions obligatoires, les consignes, les numéros d'urgence et la langue du plan au pays du bâtiment.": (
    "The common base is ISO 23601, the international standard for evacuation plans. On top of it, EE911 adapts the title block, mandatory notices, instructions, emergency numbers and the plan's language to the building's country.",
    "Die gemeinsame Basis ist ISO 23601, die internationale Norm für Fluchtpläne. Darauf passt EE911 Schriftfeld, Pflichtangaben, Verhaltensregeln, Notrufnummern und die Sprache des Plans an das Land des Gebäudes an.",
    "De gemeenschappelijke basis is ISO 23601, de internationale norm voor ontruimingsplannen. Daarbovenop past EE911 het titelblok, de verplichte vermeldingen, de richtlijnen, de noodnummers en de taal van het plan aan het land van het gebouw aan.",
    "La base comune è la ISO 23601, la norma internazionale dei piani di evacuazione. Su di essa EE911 adatta cartiglio, menzioni obbligatorie, istruzioni, numeri di emergenza e lingua del piano al paese dell'edificio."),
  "Code du travail (art. R4227-39), NF X 08-070 pour les plans schématiques, MS 41 pour les plans d'intervention en ERP. Consignes incendie, numéros d'urgence 18 · 112, point de rassemblement, espaces d'attente sécurisés.": (
    "Labour Code (art. R4227-39), NF X 08-070 for schematic plans, MS 41 for fire response plans in public buildings. Fire instructions, emergency numbers 18 · 112, assembly point, refuge areas.",
    "Arbeitsgesetzbuch (Art. R4227-39), NF X 08-070 für schematische Pläne, MS 41 für Feuerwehrpläne in Versammlungsstätten. Brandschutzordnung, Notruf 18 · 112, Sammelstelle, sichere Wartebereiche.",
    "Arbeidswetboek (art. R4227-39), NF X 08-070 voor schematische plannen, MS 41 voor interventieplannen in publieke gebouwen. Brandrichtlijnen, noodnummers 18 · 112, verzamelplaats, veilige wachtruimtes.",
    "Codice del lavoro (art. R4227-39), NF X 08-070 per i piani schematici, MS 41 per i piani di intervento negli edifici pubblici. Istruzioni antincendio, numeri di emergenza 18 · 112, punto di raccolta, spazi d'attesa sicuri."),
  "Flucht- und Rettungsplan selon ASR A2.3 et DIN ISO 23601 ; Feuerwehrplan selon DIN 14095. Textes du plan en allemand, Notruf 112.": (
    "Flucht- und Rettungsplan per ASR A2.3 and DIN ISO 23601; Feuerwehrplan per DIN 14095. Plan texts in German, emergency number 112.",
    "Flucht- und Rettungsplan nach ASR A2.3 und DIN ISO 23601; Feuerwehrplan nach DIN 14095. Plantexte auf Deutsch, Notruf 112.",
    "Flucht- und Rettungsplan volgens ASR A2.3 en DIN ISO 23601; Feuerwehrplan volgens DIN 14095. Planteksten in het Duits, noodnummer 112.",
    "Flucht- und Rettungsplan secondo ASR A2.3 e DIN ISO 23601; Feuerwehrplan secondo DIN 14095. Testi del piano in tedesco, numero di emergenza 112."),
  "Arrêté royal du 7 juillet 1994 (normes de base), plans bilingues français / néerlandais, numéros 112 · 100.": (
    "Royal Decree of 7 July 1994 (basic standards), bilingual French / Dutch plans, numbers 112 · 100.",
    "Königlicher Erlass vom 7. Juli 1994 (Basisnormen), zweisprachige Pläne Französisch / Niederländisch, Notruf 112 · 100.",
    "Koninklijk Besluit van 7 juli 1994 (basisnormen), tweetalige plannen Frans / Nederlands, nummers 112 · 100.",
    "Regio Decreto del 7 luglio 1994 (norme di base), piani bilingui francese / olandese, numeri 112 · 100."),
  "D.Lgs. 81/2008 (sécurité au travail) et D.M. du 2 septembre 2021 (gestion de la sécurité incendie) : planimetrie di emergenza sur le socle ISO 23601, textes en italien, numéros 112 · 115.": (
    "Legislative Decree 81/2008 (workplace safety) and Ministerial Decree of 2 September 2021 (fire safety management): emergency plans on the ISO 23601 base, texts in Italian, numbers 112 · 115.",
    "Gesetzesdekret 81/2008 (Arbeitsschutz) und Ministerialdekret vom 2. September 2021 (Brandschutzmanagement): Notfallpläne auf ISO-23601-Basis, Texte auf Italienisch, Notruf 112 · 115.",
    "Wetsdecreet 81/2008 (arbeidsveiligheid) en Ministerieel Besluit van 2 september 2021 (brandveiligheidsbeheer): noodplannen op ISO 23601-basis, teksten in het Italiaans, nummers 112 · 115.",
    "D.Lgs. 81/2008 (sicurezza sul lavoro) e D.M. 2 settembre 2021 (gestione della sicurezza antincendio): planimetrie di emergenza sulla base ISO 23601, testi in italiano, numeri 112 · 115."),
  "🇫🇷 France": ("🇫🇷 France", "🇫🇷 Frankreich", "🇫🇷 Frankrijk", "🇫🇷 Francia"),
  "🇩🇪 Allemagne": ("🇩🇪 Germany", "🇩🇪 Deutschland", "🇩🇪 Duitsland", "🇩🇪 Germania"),
  "🇧🇪 Belgique": ("🇧🇪 Belgium", "🇧🇪 Belgien", "🇧🇪 België", "🇧🇪 Belgio"),
  "🇮🇹 Italie": ("🇮🇹 Italy", "🇮🇹 Italien", "🇮🇹 Italië", "🇮🇹 Italia"),
  "🇪🇺 Et au-delà": ("🇪🇺 And beyond", "🇪🇺 Und darüber hinaus", "🇪🇺 En verder", "🇪🇺 E oltre"),
  "L'ISO 23601 et les pictogrammes ISO 7010 sont reconnus dans toute l'Europe : Suisse, Luxembourg et les autres pays s'appuient sur le même socle. Un pays vous manque dans la liste ? Il s'ajoute sur simple demande, avec ses mentions et sa langue.": (
    "ISO 23601 and ISO 7010 pictograms are recognised across Europe: Switzerland, Luxembourg and other countries rely on the same base. Missing a country? It can be added on request, with its notices and language.",
    "ISO 23601 und ISO-7010-Piktogramme sind europaweit anerkannt: Schweiz, Luxemburg und weitere Länder bauen auf derselben Basis auf. Fehlt ein Land? Es wird auf Anfrage ergänzt — mit seinen Pflichtangaben und seiner Sprache.",
    "ISO 23601 en ISO 7010-pictogrammen worden in heel Europa erkend: Zwitserland, Luxemburg en andere landen steunen op dezelfde basis. Mist u een land? Het wordt op verzoek toegevoegd, met zijn vermeldingen en taal.",
    "La ISO 23601 e i pittogrammi ISO 7010 sono riconosciuti in tutta Europa: Svizzera, Lussemburgo e altri paesi si basano sulla stessa base. Manca un paese? Si aggiunge su richiesta, con le sue menzioni e la sua lingua."),
  "La responsabilité de l'affichage et de la mise à jour des plans incombe à l'exploitant ; EE911 fournit l'outil et les gabarits conformes, pas une prestation de bureau de contrôle.": (
    "Displaying and updating the plans remains the operator's responsibility; EE911 provides the tool and compliant templates, not an inspection service.",
    "Aushang und Aktualisierung der Pläne liegen in der Verantwortung des Betreibers; EE911 liefert das Werkzeug und normgerechte Vorlagen, keine Prüfdienstleistung.",
    "Het ophangen en bijwerken van de plannen blijft de verantwoordelijkheid van de exploitant; EE911 levert het gereedschap en conforme sjablonen, geen keuringsdienst.",
    "L'affissione e l'aggiornamento dei piani restano responsabilità del gestore; EE911 fornisce lo strumento e i modelli conformi, non un servizio di ente di controllo."),
  # ---- modèle simple ----
  "Un modèle simple": ("A simple model", "Ein einfaches Modell", "Een eenvoudig model", "Un modello semplice"),
  "<strong>1 site et 5 étages inclus, gratuitement</strong>, avec toutes les fonctionnalités : éditeur, imports photo et DXF/DWG, plans d'évacuation et d'intervention, exports PDF, membres illimités.": (
    "<strong>1 site and 5 floors included, free</strong>, with every feature: editor, photo and DXF/DWG imports, evacuation and fire response plans, PDF exports, unlimited members.",
    "<strong>1 Standort und 5 Etagen inklusive — kostenlos</strong>, mit allen Funktionen: Editor, Foto- und DXF/DWG-Import, Flucht- und Feuerwehrpläne, PDF-Export, unbegrenzte Mitglieder.",
    "<strong>1 locatie en 5 verdiepingen inbegrepen, gratis</strong>, met alle functies: editor, foto- en DXF/DWG-import, ontruimings- en interventieplannen, PDF-export, onbeperkt leden.",
    "<strong>1 sito e 5 piani inclusi, gratuitamente</strong>, con tutte le funzionalità: editor, import foto e DXF/DWG, piani di evacuazione e di intervento, esportazioni PDF, membri illimitati."),
  "Besoin de plus de sites, d'étages ou de fonctionnalités ? Votre accès s'étend sur simple demande.": (
    "Need more sites, floors or features? Your access is extended on request.",
    "Mehr Standorte, Etagen oder Funktionen? Ihr Zugang wird auf Anfrage erweitert.",
    "Meer locaties, verdiepingen of functies nodig? Uw toegang wordt op verzoek uitgebreid.",
    "Servono più siti, piani o funzionalità? Il vostro accesso si estende su semplice richiesta."),
  "Nous contacter": ("Contact us", "Kontakt aufnehmen", "Neem contact op", "Contattateci"),
  # ---- CTA final + footer ----
  "Votre prochain plan d'évacuation est à cinq minutes.": (
    "Your next evacuation plan is five minutes away.",
    "Ihr nächster Fluchtplan ist fünf Minuten entfernt.",
    "Uw volgende ontruimingsplan is vijf minuten verwijderd.",
    "Il vostro prossimo piano di evacuazione è a cinque minuti."),
  "Commencer gratuitement": ("Start for free", "Kostenlos starten", "Gratis starten", "Inizia gratis"),
  "© 2026 EE911 — Tous droits réservés": ("© 2026 EE911 — All rights reserved", "© 2026 EE911 — Alle Rechte vorbehalten", "© 2026 EE911 — Alle rechten voorbehouden", "© 2026 EE911 — Tutti i diritti riservati"),
  "Application": ("App", "Anwendung", "Applicatie", "Applicazione"),
  "Mentions légales": ("Legal notice", "Impressum", "Juridische vermeldingen", "Note legali"),
}

IDX = {"en": 0, "de": 1, "nl": 2, "it": 3}


def build(lang: str, src: str) -> str:
    out = src
    # Chemins relatifs (page dans un sous-répertoire) + attribut lang + og:url
    out = out.replace('lang="fr"', f'lang="{lang}"')
    out = out.replace('href="styles.css"', 'href="../styles.css"')
    out = out.replace('href="favicon.svg"', 'href="../favicon.svg"')
    out = out.replace('href="mentions-legales.html"', 'href="../mentions-legales.html"')
    out = out.replace('content="https://www.ee911.eu/"',
                      f'content="https://www.ee911.eu/{lang}/"')
    # Traductions, plus longues d'abord (évite les collisions de sous-chaînes)
    for fr in sorted(TR, key=len, reverse=True):
        target = TR[fr][IDX[lang]]
        pattern = re.compile(r"\s+".join(re.escape(w) for w in fr.split()))
        out, n = pattern.subn(target.replace("\\", r"\\"), out)
        if n == 0:
            raise SystemExit(f"[{lang}] chaîne introuvable dans index.html : {fr!r}")
    return out


def main() -> None:
    with io.open(SRC, encoding="utf-8") as f:
        src = f.read()
    for lang in LANGS:
        out_dir = os.path.join(ROOT, "site", lang)
        os.makedirs(out_dir, exist_ok=True)
        html = build(lang, src)
        with io.open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        print(f"site/{lang}/index.html : OK")


if __name__ == "__main__":
    main()
