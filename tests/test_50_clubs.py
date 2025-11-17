"""
Test sur 50 clubs pour vérifier la vitesse et l'exactitude
Génère un fichier CSV avec les résultats
"""

import sys
import os
import csv
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper_by_scl import SCLScraper

def test_50_clubs():
    """Test sur 50 clubs avec mesure de vitesse et génération CSV"""
    
    print("=" * 60)
    print("🧪 TEST SUR PLAGE SCL 5000-5050 - VITESSE ET EXACTITUDE")
    print("=" * 60)
    print()
    
    # Tester la plage scl de 5000 à 5050 (51 numéros)
    test_scls = list(range(5000, 5051))
    
    print(f"🔍 Test sur {len(test_scls)} numéros scl")
    print(f"   Plage: {min(test_scls)} - {max(test_scls)}\n")
    print("⏱️  Démarrage du test...\n")
    
    start_time = time.time()
    csv_file = "test_50_clubs_results.csv"
    
    with SCLScraper(headless=True, slow_mo=0) as scraper:
        clubs_found = []
        clubs_not_found = []
        
        # Ouvrir le fichier CSV en mode écriture
        with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
            fieldnames = ['scl', 'nom', 'numero_affiliation', 'email', 'telephone', 'adresse', 'url_detail', 'temps_extraction']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, scl in enumerate(test_scls, 1):
                club_start = time.time()
                print(f"  [{i}/{len(test_scls)}] Test scl={scl}...", end=" ", flush=True)
                
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
                        
                        # Écrire dans le CSV
                        writer.writerow({
                            'scl': scl,
                            'nom': club.nom,
                            'numero_affiliation': club.numero_affiliation or '',
                            'email': club.email or '',
                            'telephone': club.telephone or '',
                            'adresse': club.adresse or '',
                            'url_detail': club.url_detail or '',
                            'temps_extraction': f"{club_time:.2f}"
                        })
                        csvfile.flush()  # Sauvegarder immédiatement
                        
                        clubs_found.append({
                            'scl': scl,
                            'club': club,
                            'time': club_time
                        })
                    else:
                        print(f"❌ Aucun club ({club_time:.2f}s)")
                        clubs_not_found.append(scl)
                        
                        # Écrire quand même dans le CSV avec les infos disponibles
                        writer.writerow({
                            'scl': scl,
                            'nom': '',
                            'numero_affiliation': '',
                            'email': '',
                            'telephone': '',
                            'adresse': '',
                            'url_detail': '',
                            'temps_extraction': f"{club_time:.2f}"
                        })
                        csvfile.flush()
                    
                except KeyboardInterrupt:
                    print("\n\n⚠️  Interruption utilisateur")
                    break
                except Exception as e:
                    club_time = time.time() - club_start
                    print(f"❌ Erreur: {e} ({club_time:.2f}s)")
                    clubs_not_found.append(scl)
                
                print()
        
        total_time = time.time() - start_time
        avg_time = total_time / len(test_scls)
        speed = len(test_scls) / total_time
        
        print("=" * 60)
        print("📊 RÉSULTATS")
        print("=" * 60)
        print(f"✅ Clubs trouvés: {len(clubs_found)}/{len(test_scls)}")
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
        
        print(f"💾 Résultats sauvegardés dans: {csv_file}")

if __name__ == "__main__":
    test_50_clubs()

