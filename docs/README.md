# 🏆 Scraper de Clubs FFF - Mise à jour Google Sheets

Système automatisé pour scraper les informations des clubs de football français depuis les sites officiels des districts FFF et mettre à jour une Google Sheet.

## 📋 Prérequis

- Python 3.8+
- Compte Google avec accès à Google Sheets API
- Accès à la Google Sheet cible

## 🚀 Installation

1. **Cloner ou télécharger le projet**

2. **Installer les dépendances Python** :
```bash
pip install -r requirements.txt
```

3. **Installer les navigateurs Playwright** :
```bash
playwright install chromium
```

4. **Configurer Google Sheets API** :
   - Allez sur [Google Cloud Console](https://console.cloud.google.com/)
   - Créez un nouveau projet ou sélectionnez un projet existant
   - Activez l'API Google Sheets et Google Drive
   - Créez un compte de service :
     - Allez dans "IAM & Admin" > "Service Accounts"
     - Cliquez sur "Create Service Account"
     - Donnez un nom (ex: "fff-scraper")
     - Cliquez sur "Create and Continue"
     - Accordez le rôle "Editor" ou "Viewer" selon vos besoins
     - Cliquez sur "Done"
   - Créez une clé JSON :
     - Cliquez sur le compte de service créé
     - Allez dans l'onglet "Keys"
     - Cliquez sur "Add Key" > "Create new key"
     - Sélectionnez "JSON"
     - Téléchargez le fichier et renommez-le `credentials.json`
     - Placez-le à la racine du projet
   - Partagez votre Google Sheet avec l'email du compte de service :
     - Ouvrez votre Google Sheet
     - Cliquez sur "Partager" (Share)
     - Ajoutez l'email du compte de service (visible dans le fichier credentials.json, champ `client_email`)
     - Donnez-lui les droits "Éditeur" (Editor)

## 📝 Utilisation

### Étape 1 : Générer le fichier JSON des districts

Vérifie et génère le fichier `districts_urls.json` avec toutes les URLs valides :

```bash
python verify_districts.py
```

⚠️ **Note** : Cette étape peut prendre plusieurs minutes car elle teste chaque URL. Le fichier `districts_urls.json` sera créé avec uniquement les districts valides.

### Étape 2 : Scraper et mettre à jour (Mode test)

Test sur les 5 premiers clubs de la Gironde sans mettre à jour Google Sheets :

```bash
python main.py --district Gironde --sheet Gironde --limit 5 --dry-run
```

### Étape 3 : Scraper et mettre à jour (Mode production)

Scrape tous les clubs de la Gironde et met à jour la Google Sheet :

```bash
python main.py --district Gironde --sheet Gironde
```

### Options disponibles

```bash
python main.py --help
```

Options principales :
- `--district` : Nom du district à scraper (défaut: Gironde)
- `--sheet` : Nom de la feuille Google Sheets (défaut: Gironde)
- `--limit` : Limite le nombre de clubs à scraper (utile pour les tests)
- `--credentials` : Chemin vers credentials.json (défaut: credentials.json)
- `--spreadsheet-url` : URL de la Google Sheet
- `--dry-run` : Mode test (scrape mais ne met pas à jour)
- `--headless` : Mode headless du navigateur (défaut: True)

### Exemples

**Test sur un autre district** :
```bash
python main.py --district Paris_IDF --sheet "Paris IDF" --limit 3 --dry-run
```

**Scraping complet avec navigateur visible** :
```bash
python main.py --district Gironde --headless False
```

## 📁 Structure du projet

```
wrapping_clubs/
├── verify_districts.py          # Script de vérification des URLs de districts
├── scraper_clubs.py             # Script de scraping avec Playwright
├── google_sheets_integration.py # Module d'intégration Google Sheets
├── main.py                      # Script principal d'orchestration
├── requirements.txt             # Dépendances Python
├── README.md                    # Ce fichier
├── credentials.json             # Fichier de credentials Google (à créer)
└── districts_urls.json          # Fichier généré avec les URLs valides
```

## 🔍 Fonctionnalités

### Scraping

- ✅ Extraction automatique de la liste des clubs depuis chaque district
- ✅ Extraction des détails de chaque club :
  - Nom du club
  - Numéro d'affiliation
  - Email officiel (@lfna.fr, @lpiff.fr, etc.)
  - Téléphone du siège
  - Adresse postale (Siège social)
- ✅ Gestion des erreurs et rate-limiting pour ne pas surcharger les serveurs
- ✅ Support de différents formats de pages (Gironde, Paris IDF, etc.)

### Intégration Google Sheets

- ✅ Lecture des données existantes
- ✅ Matching intelligent des clubs (normalisation des noms)
- ✅ Mise à jour uniquement des champs vides (préserve les données existantes)
- ✅ Ajout automatique des nouveaux clubs
- ✅ Préservation des colonnes de suivi (`Date d'envoi`, `Réponses`, etc.)

## ⚙️ Configuration

### Structure attendue de la Google Sheet

La feuille doit contenir au minimum ces colonnes :
- `Club` : Nom du club
- `Email` : Email du club
- `Téléphone` : Téléphone du club
- `Nom` : Nom du contact (peut être vide)
- `Prénom` : Prénom du contact (peut être vide)
- `Rôle` : Rôle du contact (peut être vide)

Les colonnes suivantes sont préservées mais non modifiées :
- `Date d'envoi`
- `Réponses`
- `Date de relance`
- `Portable`
- etc.

## 🐛 Dépannage

### Erreur "districts_urls.json non trouvé"
Exécutez d'abord `python verify_districts.py` pour générer le fichier.

### Erreur "credentials.json non trouvé"
Vérifiez que vous avez bien créé le fichier `credentials.json` depuis Google Cloud Console et qu'il est à la racine du projet.

### Erreur "Permission denied" sur Google Sheets
Assurez-vous d'avoir partagé la Google Sheet avec l'email du compte de service (visible dans `credentials.json`).

### Le scraper ne trouve pas les clubs
- Vérifiez que l'URL du district est correcte dans `districts_urls.json`
- Essayez avec `--headless False` pour voir ce qui se passe
- Les sites FFF peuvent avoir changé leur structure HTML

### Rate limiting / Blocage
Le script inclut des délais entre les requêtes. Si vous êtes bloqué :
- Augmentez le `slow_mo` dans `scraper_clubs.py`
- Ajoutez des `time.sleep()` supplémentaires
- Utilisez un VPN si nécessaire

## 📊 Format des données scrapées

Les données sont sauvegardées en JSON avec cette structure :

```json
{
  "nom": "A. S. SAFRAN BORDEAUX",
  "numero_affiliation": "26798",
  "email_officiel": "123456@lfna.fr",
  "email_principal": null,
  "telephone": "0556123456",
  "adresse": "123 Rue Example, 33000 Bordeaux",
  "url_detail": "https://gironde.fff.fr/recherche-clubs?scl=26798"
}
```

## ⚠️ Avertissements

- **Respect des conditions d'utilisation** : Assurez-vous de respecter les conditions d'utilisation des sites FFF lors du scraping.
- **Rate limiting** : Le script inclut des délais pour éviter de surcharger les serveurs. Ne modifiez pas ces délais pour aller plus vite.
- **Données sensibles** : Ne partagez jamais votre fichier `credentials.json`. Ajoutez-le au `.gitignore` si vous utilisez Git.

## 📝 Notes

- Le matching des clubs utilise une normalisation des noms (suppression des accents, espaces, etc.) pour trouver les correspondances même si les noms diffèrent légèrement.
- Les mises à jour ne remplacent jamais les données existantes, elles complètent uniquement les champs vides.
- Les colonnes de suivi manuel (`Date d'envoi`, `Réponses`, etc.) ne sont jamais modifiées.

## 🤝 Contribution

Pour améliorer le scraper :
1. Testez sur différents districts
2. Ajoutez des sélecteurs CSS pour les districts non supportés
3. Améliorez le matching des noms de clubs
4. Ajoutez la gestion d'autres champs si nécessaire

## 📄 Licence

Ce projet est fourni tel quel pour usage personnel/professionnel.

