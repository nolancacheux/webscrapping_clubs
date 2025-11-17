"""
Script pour vérifier et générer le fichier JSON des URLs de districts FFF valides.
Vérifie que chaque URL retourne un status 200 avant de l'ajouter au JSON.
"""

import requests
import json
import time
from typing import Dict

# Liste des districts français avec leurs noms probables
DISTRICTS = {
    "Ain": "ain",
    "Aisne": "aisne",
    "Allier": "allier",
    "Alpes_de_Haute_Provence": "alpes-haute-provence",
    "Hautes_Alpes": "hautes-alpes",
    "Alpes_Maritimes": "alpes-maritimes",
    "Ardeche": "ardeche",
    "Ardennes": "ardennes",
    "Ariege": "ariege",
    "Aube": "aube",
    "Aude": "aude",
    "Aveyron": "aveyron",
    "Bouches_du_Rhone": "bouches-du-rhone",
    "Calvados": "calvados",
    "Cantal": "cantal",
    "Charente": "charente",
    "Charente_Maritime": "charente-maritime",
    "Cher": "cher",
    "Correze": "correze",
    "Corse": "corse",
    "Cote_d_Or": "cote-d-or",
    "Cotes_d_Armor": "cotes-d-armor",
    "Creuse": "creuse",
    "Dordogne": "dordogne",
    "Doubs": "doubs",
    "Drome": "drome",
    "Eure": "eure",
    "Eure_et_Loir": "eure-et-loir",
    "Finistere": "finistere",
    "Gard": "gard",
    "Haute_Garonne": "haute-garonne",
    "Gers": "gers",
    "Gironde": "gironde",
    "Herault": "herault",
    "Ille_et_Vilaine": "ille-et-vilaine",
    "Indre": "indre",
    "Indre_et_Loire": "indre-et-loire",
    "Isere": "isere",
    "Jura": "jura",
    "Landes": "landes",
    "Loir_et_Cher": "loir-et-cher",
    "Loire": "loire",
    "Haute_Loire": "haute-loire",
    "Loire_Atlantique": "loire-atlantique",
    "Loiret": "loiret",
    "Lot": "lot",
    "Lot_et_Garonne": "lot-et-garonne",
    "Lozere": "lozere",
    "Maine_et_Loire": "maine-et-loire",
    "Manche": "manche",
    "Marne": "marne",
    "Haute_Marne": "haute-marne",
    "Mayenne": "mayenne",
    "Meurthe_et_Moselle": "meurthe-et-moselle",
    "Meuse": "meuse",
    "Morbihan": "morbihan",
    "Moselle": "moselle",
    "Nievre": "nievre",
    "Nord": "nord",
    "Oise": "oise",
    "Orne": "orne",
    "Pas_de_Calais": "pas-de-calais",
    "Puy_de_Dome": "puy-de-dome",
    "Pyrenees_Atlantiques": "pyrenees-atlantiques",
    "Hautes_Pyrenees": "hautes-pyrenees",
    "Pyrenees_Orientales": "pyrenees-orientales",
    "Bas_Rhin": "bas-rhin",
    "Haut_Rhin": "haut-rhin",
    "Rhone": "rhone",
    "Haute_Saone": "haute-saone",
    "Saone_et_Loire": "saone-et-loire",
    "Sarthe": "sarthe",
    "Savoie": "savoie",
    "Haute_Savoie": "haute-savoie",
    "Paris_IDF": "paris-idf",
    "Seine_Maritime": "seine-maritime",
    "Seine_et_Marne": "seine-et-marne",
    "Yvelines": "yvelines",
    "Deux_Sevres": "deux-sevres",
    "Somme": "somme",
    "Tarn": "tarn",
    "Tarn_et_Garonne": "tarn-et-garonne",
    "Var": "var",
    "Vaucluse": "vaucluse",
    "Vendee": "vendee",
    "Vienne": "vienne",
    "Haute_Vienne": "haute-vienne",
    "Vosges": "vosges",
    "Yonne": "yonne",
    "Territoire_de_Belfort": "territoire-de-belfort",
    "Essonne": "essonne",
    "Hauts_de_Seine": "hauts-de-seine",
    "Seine_Saint_Denis": "seine-saint-denis",
    "Val_de_Marne": "val-de-marne",
    "Val_d_Oise": "val-d-oise",
    "Guadeloupe": "guadeloupe",
    "Martinique": "martinique",
    "Guyane": "guyane",
    "Reunion": "reunion",
    "Mayotte": "mayotte",
}

# Variantes possibles pour certains districts
VARIANTES = {
    "Paris_IDF": ["paris-idf", "parisidf", "idf"],
    "Loire_Atlantique": ["loire-atlantique", "district44"],
    "Nord": ["nord", "district59"],
    "Pas_de_Calais": ["pas-de-calais", "district62"],
}


def verify_url(url: str, timeout: int = 10) -> bool:
    """
    Vérifie si une URL retourne un status 200.
    
    Args:
        url: URL à vérifier
        timeout: Timeout en secondes
        
    Returns:
        True si l'URL est valide (status 200), False sinon
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False


def find_valid_url(district_name: str, base_name: str) -> str:
    """
    Trouve l'URL valide pour un district en testant différentes variantes.
    
    Args:
        district_name: Nom du district (clé)
        base_name: Nom de base pour l'URL
        
    Returns:
        URL valide ou None
    """
    # Test de la variante principale
    url = f"https://{base_name}.fff.fr/les-clubs/"
    print(f"  Test: {url}")
    if verify_url(url):
        print(f"  ✅ URL valide trouvée!")
        return url
    
    # Test des variantes si disponibles
    if district_name in VARIANTES:
        for variante in VARIANTES[district_name]:
            if variante != base_name:
                url = f"https://{variante}.fff.fr/les-clubs/"
                print(f"  Test variante: {url}")
                if verify_url(url):
                    print(f"  ✅ URL valide trouvée (variante)!")
                    return url
    
    return None


def generate_districts_json(output_file: str = "districts_urls.json"):
    """
    Génère le fichier JSON des districts avec leurs URLs valides.
    
    Args:
        output_file: Nom du fichier de sortie
    """
    valid_districts: Dict[str, str] = {}
    
    print("🔍 Vérification des URLs des districts FFF...\n")
    
    total = len(DISTRICTS)
    current = 0
    
    for district_name, base_name in DISTRICTS.items():
        current += 1
        print(f"[{current}/{total}] {district_name}...")
        
        url = find_valid_url(district_name, base_name)
        
        if url:
            valid_districts[district_name] = url
        else:
            print(f"  ⚠️  Aucune URL valide trouvée pour {district_name}")
        
        # Rate limiting pour ne pas surcharger les serveurs
        time.sleep(1)
        print()
    
    # Sauvegarde du JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(valid_districts, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Fichier généré: {output_file}")
    print(f"📊 Districts valides trouvés: {len(valid_districts)}/{total}")
    
    return valid_districts


if __name__ == "__main__":
    generate_districts_json()

