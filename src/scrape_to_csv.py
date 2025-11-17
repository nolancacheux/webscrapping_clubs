"""
Script pour scraper tous les clubs et sauvegarder en CSV
"""

import csv
import time
import os
import sys
from datetime import datetime

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper_by_scl import SCLScraper

def scrape_all_to_csv(max_scl: int = 30000, batch_size: int = 1000, 
                     output_file: str = "clubs_france.csv",
                     resume_from: int = 1,
                     workers: int = 1):
    """
    Scrape tous les clubs et sauvegarde en CSV
    
    Args:
        max_scl: Numéro scl maximum
        batch_size: Taille des lots pour affichage du progrès
        output_file: Fichier CSV de sortie
        resume_from: Reprendre depuis ce numéro scl
    """
    
    # Vérifier si le fichier existe déjà pour reprendre
    existing_scls = set()
    if os.path.exists(output_file) and resume_from == 1:
        print(f"📂 Fichier existant trouvé: {output_file}")
        print("   Lecture des numéros déjà traités...")
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('scl'):
                        existing_scls.add(int(row['scl']))
            print(f"   ✅ {len(existing_scls)} clubs déjà dans le fichier")
            if existing_scls:
                resume_from = max(existing_scls) + 1
                print(f"   🔄 Reprise depuis scl={resume_from}")
        except:
            print("   ⚠️  Impossible de lire le fichier, démarrage depuis le début")
    
    print("=" * 60)
    print("🏆 SCRAPING TOUS LES CLUBS DE FRANCE")
    print("=" * 60)
    print(f"📊 Plage: {resume_from} - {max_scl}")
    print(f"💾 Fichier de sortie: {output_file}")
    print("=" * 60)
    print()
    
    start_time = datetime.now()
    total_found = len(existing_scls)
    
    # Créer le fichier CSV avec les en-têtes si nouveau
    file_exists = os.path.exists(output_file) and len(existing_scls) > 0
    mode = 'a' if file_exists else 'w'
    
    with open(output_file, mode, encoding='utf-8', newline='') as csvfile:
        fieldnames = ['scl', 'nom', 'numero_affiliation', 'email', 'telephone', 'adresse', 'url_detail']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Écrire les en-têtes si nouveau fichier
        if not file_exists:
            writer.writeheader()
        
        with SCLScraper(headless=True, slow_mo=0) as scraper:
            current_batch = []
            
            for start_scl in range(resume_from, max_scl + 1, batch_size):
                end_scl = min(start_scl + batch_size - 1, max_scl)
                
                print(f"\n📦 Lot {start_scl}-{end_scl} ({end_scl - start_scl + 1} numéros)")
                print("-" * 60)
                
                batch_start_time = time.time()
                batch_clubs = 0
                
                for scl in range(start_scl, end_scl + 1):
                    # Vérifier si déjà traité
                    if scl in existing_scls:
                        continue
                    
                    try:
                        club_data = scraper.extract_club_by_scl(scl)
                        
                        if club_data:
                            # Écrire directement dans le CSV
                            writer.writerow({
                                'scl': scl,
                                'nom': club_data.nom,
                                'numero_affiliation': club_data.numero_affiliation or '',
                                'email': club_data.email or '',
                                'telephone': club_data.telephone or '',
                                'adresse': club_data.adresse or '',
                                'url_detail': club_data.url_detail or ''
                            })
                            csvfile.flush()  # Sauvegarder immédiatement
                            batch_clubs += 1
                            total_found += 1
                            
                            if batch_clubs <= 3:  # Afficher les 3 premiers
                                print(f"  ✅ scl={scl}: {club_data.nom}")
                        
                        # Afficher le progrès tous les 100
                        if (scl - start_scl) % 100 == 0:
                            progress = ((scl - start_scl) / (end_scl - start_scl + 1)) * 100
                            print(f"  📊 {progress:.0f}% - {batch_clubs} clubs trouvés dans ce lot")
                        
                    except KeyboardInterrupt:
                        print("\n\n⚠️  Interruption utilisateur")
                        print(f"💾 Fichier sauvegardé jusqu'à scl={scl-1}")
                        return
                    except Exception as e:
                        print(f"  ⚠️  Erreur pour scl={scl}: {e}")
                        continue
                
                batch_time = time.time() - batch_start_time
                print(f"\n  ✅ Lot terminé: {batch_clubs} clubs trouvés en {batch_time:.1f}s")
                
                # Statistiques
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = (end_scl - resume_from + 1) / elapsed if elapsed > 0 else 0
                remaining = max_scl - end_scl
                eta_seconds = remaining / rate if rate > 0 else 0
                
                print(f"  📊 Total: {total_found} clubs | Vitesse: {rate:.1f} scl/s | ETA: {eta_seconds/3600:.1f}h")
    
    total_time = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print("✅ SCRAPING TERMINÉ")
    print("=" * 60)
    print(f"📊 Statistiques:")
    print(f"   Clubs trouvés: {total_found}")
    print(f"   Numéros testés: {max_scl - resume_from + 1}")
    print(f"   Taux de réussite: {(total_found/(max_scl-resume_from+1)*100):.2f}%")
    print(f"   Temps total: {total_time/3600:.2f} heures")
    print(f"   Vitesse moyenne: {(max_scl-resume_from+1)/total_time:.2f} scl/s")
    print(f"\n💾 Fichier CSV sauvegardé: {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape tous les clubs de France en CSV")
    parser.add_argument('--max-scl', type=int, default=30000, 
                       help='Numéro scl maximum (défaut: 30000)')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='Taille des lots pour affichage (défaut: 1000)')
    parser.add_argument('--output', type=str, default='clubs_france.csv',
                       help='Fichier CSV de sortie (défaut: clubs_france.csv)')
    parser.add_argument('--resume-from', type=int, default=1,
                       help='Reprendre depuis ce numéro scl (défaut: 1)')
    
    args = parser.parse_args()
    
    scrape_all_to_csv(
        max_scl=args.max_scl,
        batch_size=args.batch_size,
        output_file=args.output,
        resume_from=args.resume_from
    )

