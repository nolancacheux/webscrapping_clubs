"""
Script pour scraper une plage de numéros SCL
Surcharge les entrées existantes dans le CSV (évite les doublons)
Même format et délais que test_50_clubs.py
"""

import sys
import os
import csv
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper_by_scl import SCLScraper

def scrape_range(start_scl: int, end_scl: int, output_csv: str = "clubs_france.csv"):
    """
    Scrape une plage de numéros SCL et met à jour le CSV (surcharge les entrées existantes)
    
    Args:
        start_scl: Numéro SCL de début
        end_scl: Numéro SCL de fin
        output_csv: Fichier CSV de sortie (surcharge les entrées existantes)
    """
    
    print("=" * 60)
    print(f"🏆 SCRAPING PLAGE SCL {start_scl}-{end_scl}")
    print("=" * 60)
    print()
    
    # Liste des SCL à tester
    scl_list = list(range(start_scl, end_scl + 1))
    
    print(f"🔍 Scraping de {len(scl_list)} numéros scl")
    print(f"   Plage: {start_scl} - {end_scl}\n")
    print("⏱️  Démarrage du scraping...\n")
    
    start_time = time.time()
    
    # Charger les données existantes pour éviter les doublons
    existing_data = {}
    file_exists = os.path.exists(output_csv)
    
    if file_exists:
        try:
            with open(output_csv, 'r', encoding='utf-8', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    scl_key = row.get('scl', '').strip()
                    if scl_key and scl_key.isdigit():
                        existing_data[int(scl_key)] = row
        except Exception as e:
            print(f"⚠️  Erreur lors de la lecture du fichier existant: {e}")
            existing_data = {}
    
    with SCLScraper(headless=True, slow_mo=0) as scraper:
        clubs_found = []
        clubs_not_found = []
        
        # Collecter toutes les données (existantes + nouvelles)
        all_data = existing_data.copy()
        
        for i, scl in enumerate(scl_list, 1):
            club_start = time.time()
            print(f"  [{i}/{len(scl_list)}] Test scl={scl}...", end=" ", flush=True)
            
            try:
                club = scraper.extract_club_by_scl(scl)
                club_time = time.time() - club_start
                
                if club:
                    print(f"✅ {club.nom} ({club_time:.2f}s)")
                    print(f"       📋 Affiliation: {club.numero_affiliation}")
                    print(f"       📧 Email: {club.email or 'N/A'}")
                    print(f"       📞 Téléphone: {club.telephone or 'N/A'}")
                    print(f"       📍 Adresse: {club.adresse or 'N/A'}")
                    print(f"       🔗 URL: {club.url_detail}")
                    
                    # Mettre à jour ou créer l'entrée (surcharge si existe)
                    all_data[scl] = {
                        'scl': str(scl),
                        'nom': club.nom,
                        'numero_affiliation': club.numero_affiliation or '',
                        'email': club.email or '',
                        'telephone': club.telephone or '',
                        'adresse': club.adresse or '',
                        'url_detail': club.url_detail or '',
                        'temps_extraction': f"{club_time:.2f}"
                    }
                    
                    clubs_found.append({
                        'scl': scl,
                        'club': club,
                        'time': club_time
                    })
                else:
                    print(f"❌ Aucun club ({club_time:.2f}s)")
                    clubs_not_found.append(scl)
                    
                    # Mettre à jour ou créer l'entrée vide (surcharge si existe)
                    all_data[scl] = {
                        'scl': str(scl),
                        'nom': '',
                        'numero_affiliation': '',
                        'email': '',
                        'telephone': '',
                        'adresse': '',
                        'url_detail': '',
                        'temps_extraction': f"{club_time:.2f}"
                    }
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interruption utilisateur")
                break
            except Exception as e:
                club_time = time.time() - club_start
                print(f"❌ Erreur: {e} ({club_time:.2f}s)")
                clubs_not_found.append(scl)
            
            print()
        
        # Écrire toutes les données dans le CSV (surcharge complète)
        fieldnames = ['scl', 'nom', 'numero_affiliation', 'email', 'telephone', 'adresse', 'url_detail', 'temps_extraction']
        with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Trier par SCL pour un ordre cohérent
            for scl_key in sorted(all_data.keys()):
                writer.writerow(all_data[scl_key])
        
        total_time = time.time() - start_time
        avg_time = total_time / len(scl_list)
        speed = len(scl_list) / total_time
        
        print("=" * 60)
        print("📊 RÉSULTATS")
        print("=" * 60)
        print(f"✅ Clubs trouvés: {len(clubs_found)}/{len(scl_list)}")
        print(f"❌ Clubs non trouvés: {len(clubs_not_found)}")
        if clubs_not_found:
            print(f"   Numéros: {clubs_not_found[:10]}{'...' if len(clubs_not_found) > 10 else ''}")
        print()
        print("⏱️  PERFORMANCE")
        print(f"   Temps total: {total_time:.2f}s")
        print(f"   Temps moyen par club: {avg_time:.2f}s")
        print(f"   Vitesse: {speed:.2f} clubs/seconde")
        print(f"   Estimation pour 30000 clubs: {30000/speed/3600:.2f} heures")
        print()
        
        # Statistiques sur les données extraites
        if clubs_found:
            emails_found = sum(1 for c in clubs_found if c['club'].email)
            phones_found = sum(1 for c in clubs_found if c['club'].telephone)
            addresses_found = sum(1 for c in clubs_found if c['club'].adresse)
            
            print("📈 QUALITÉ DES DONNÉES")
            print(f"   Emails trouvés: {emails_found}/{len(clubs_found)} ({emails_found/len(clubs_found)*100:.1f}%)")
            print(f"   Téléphones trouvés: {phones_found}/{len(clubs_found)} ({phones_found/len(clubs_found)*100:.1f}%)")
            print(f"   Adresses trouvées: {addresses_found}/{len(clubs_found)} ({addresses_found/len(clubs_found)*100:.1f}%)")
            print()
        
        print(f"💾 Résultats sauvegardés dans: {output_csv}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape une plage de numéros SCL")
    parser.add_argument('start', type=int, help='Numéro SCL de début')
    parser.add_argument('end', type=int, help='Numéro SCL de fin')
    parser.add_argument('output', type=str, nargs='?', default='clubs_france.csv',
                       help='Fichier CSV de sortie (défaut: clubs_france.csv)')
    
    args = parser.parse_args()
    
    scrape_range(args.start, args.end, args.output)

