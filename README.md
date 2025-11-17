# 🏆 Scraper de Clubs de Football Français

Scraper pour extraire les données des clubs de football français depuis les sites officiels FFF (Fédération Française de Football).

## 🚀 Utilisation Rapide

### Scraper une plage de numéros SCL

```bash
# Scraper de 0 à 1000
python scripts/scrape_range.py 0 1000 clubs_france.csv

# Scraper de 1000 à 2000
python scripts/scrape_range.py 1000 2000 clubs_france.csv

# Scraper de 2000 à 3000
python scripts/scrape_range.py 2000 3000 clubs_france.csv
```

**Note** : Le fichier CSV est en mode append. Tous les résultats s'ajoutent au même fichier `clubs_france.csv`.

### Test rapide (50 clubs)

```bash
python tests/test_50_clubs.py
```

## 📋 Format de Sortie

Le fichier CSV contient les colonnes suivantes :
- `scl` : Numéro SCL
- `nom` : Nom du club
- `numero_affiliation` : Numéro d'affiliation
- `email` : Email du club
- `telephone` : Téléphone du club
- `adresse` : Adresse du club
- `url_detail` : URL de détail
- `temps_extraction` : Temps d'extraction en secondes

## ⚙️ Configuration

- **Timeout** : 5s (pour charger la page)
- **Délai Angular** : 0.3s (pour laisser Angular charger le contenu)
- **Pas de délai entre clubs** : Maximum de vitesse

## 📊 Statistiques

Chaque script affiche :
- Nombre de clubs trouvés
- Temps total et vitesse
- Qualité des données (emails, téléphones, adresses)
- Estimation pour 30000 clubs

## 📁 Structure du Projet

```
wrapping_clubs/
├── src/
│   ├── scraper_by_scl.py      # Scraper principal
│   └── scrape_to_csv.py       # Script alternatif
├── scripts/
│   ├── scrape_range.py        # Script pour scraper une plage
│   └── check_system.py        # Vérification des ressources système
├── tests/
│   └── test_50_clubs.py       # Test sur 50 clubs
└── clubs_france.csv           # Fichier CSV de sortie
```

## 🔧 Installation

```bash
# Installer les dépendances
pip install playwright beautifulsoup4 lxml

# Installer Playwright
python -m playwright install chromium
```

## 📝 Exemples

### Scraper plusieurs plages successivement

```bash
# Lancer dans l'ordre que vous voulez
python scripts/scrape_range.py 0 1000 clubs_france.csv
python scripts/scrape_range.py 1000 2000 clubs_france.csv
python scripts/scrape_range.py 2000 3000 clubs_france.csv
```

Tous les résultats seront dans `clubs_france.csv`.

## 🎯 Performance

- **Vitesse** : ~2-3 clubs/seconde
- **Temps estimé pour 30000 clubs** : ~3-4 heures
- **Taux de réussite** : ~70-80% (certains numéros SCL n'existent pas)

## 📖 Documentation

Voir `SCRAPING_GUIDE.md` pour plus de détails.
