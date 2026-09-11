# EE911 — site commercial

Site vitrine de EE911 (www.ee911.eu). Statique, sans framework ni ressource
externe (fonts système, aucun traceur) : `site/` contient les pages, le
`Dockerfile` les sert via nginx derrière le reverse proxy de l'infra.

- Application (exploitation) : https://map.ee911.eu — dépôt `ee911-app`.
- Inscription depuis le site : les CTA envoient vers
  `map.ee911.eu/login?mode=signup&email=…` (offre découverte : 1 site,
  5 étages ; -1 = illimité côté admin).

## Déploiement

Depuis le dépôt `infra` sur le serveur :

```bash
./scripts/deploy.sh ee911-site
```

(le script tire ce dépôt puis reconstruit le service `ee911-site`).

## Développement local

Ouvrir `site/index.html` dans un navigateur — aucune étape de build.

## À faire avant la mise en ligne définitive

- Compléter `site/mentions-legales.html` (raison sociale, RCS, directeur de
  la publication).
- Créer l'alias e-mail `contact@ee911.eu` (OVH) référencé par le site.
