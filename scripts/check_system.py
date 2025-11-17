"""
Script pour vérifier les ressources système (RAM, CPU)
"""

import psutil
import platform

def check_system_resources():
    """Affiche les ressources système disponibles"""
    
    print("=" * 60)
    print("💻 RESSOURCES SYSTÈME")
    print("=" * 60)
    print()
    
    # Informations CPU
    print("🔧 CPU")
    print(f"   Nombre de cœurs physiques: {psutil.cpu_count(logical=False)}")
    print(f"   Nombre de cœurs logiques: {psutil.cpu_count(logical=True)}")
    print(f"   Fréquence CPU: {psutil.cpu_freq().current:.0f} MHz")
    print(f"   Utilisation CPU actuelle: {psutil.cpu_percent(interval=1):.1f}%")
    print()
    
    # Informations RAM
    ram = psutil.virtual_memory()
    print("💾 RAM")
    print(f"   RAM totale: {ram.total / (1024**3):.2f} GB")
    print(f"   RAM disponible: {ram.available / (1024**3):.2f} GB")
    print(f"   RAM utilisée: {ram.used / (1024**3):.2f} GB ({ram.percent:.1f}%)")
    print()
    
    # Recommandations pour le scraping
    print("=" * 60)
    print("📊 RECOMMANDATIONS POUR LE SCRAPING")
    print("=" * 60)
    print()
    
    # Calculer les recommandations basées sur les ressources
    ram_gb = ram.total / (1024**3)
    ram_available_gb = ram.available / (1024**3)
    cpu_cores = psutil.cpu_count(logical=True)
    
    # Estimation RAM par worker Playwright (~200-300 MB)
    ram_per_worker = 0.25  # GB
    # Utiliser 80% de la RAM disponible pour être agressif mais sûr
    max_workers_by_ram_available = int((ram_available_gb * 0.8) / ram_per_worker)
    # Ou 70% de la RAM totale si beaucoup de RAM disponible
    max_workers_by_ram_total = int((ram_gb * 0.7) / ram_per_worker)
    
    # Recommandation basée sur CPU (2-3x le nombre de cœurs logiques pour I/O bound)
    recommended_workers_cpu_conservative = cpu_cores * 2
    recommended_workers_cpu_aggressive = cpu_cores * 3
    
    # Prendre le minimum entre RAM disponible et CPU pour être sûr
    recommended_workers_conservative = min(max_workers_by_ram_available, recommended_workers_cpu_conservative, 50)
    # Plus agressif si beaucoup de RAM totale disponible
    recommended_workers_aggressive = min(max_workers_by_ram_total, recommended_workers_cpu_aggressive, 60)
    
    print(f"✅ Workers recommandés (conservatif): {recommended_workers_conservative}")
    print(f"✅ Workers recommandés (agressif): {recommended_workers_aggressive}")
    print(f"   (Basé sur: {cpu_cores} cœurs CPU, {ram_gb:.1f} GB RAM totale, {ram_available_gb:.1f} GB RAM disponible)")
    print()
    
    # Configurations suggérées
    print("⚙️  CONFIGURATIONS SUGGÉRÉES")
    print()
    
    if ram_gb >= 16 and cpu_cores >= 16:
        print("🚀 Configuration ULTRA RAPIDE (recommandée pour votre config):")
        ultra_workers = min(recommended_workers_aggressive, 40)
        print(f"   python src/scrape_all_parallel.py --workers {ultra_workers} --batch-size 400")
        print(f"   → Vitesse estimée: ~15-25 scl/s")
        print(f"   → Temps pour 30000 clubs: ~20-35 minutes")
        print()
        
        print("⚡ Configuration TRÈS RAPIDE:")
        very_fast_workers = min(recommended_workers_aggressive, 30)
        print(f"   python src/scrape_all_parallel.py --workers {very_fast_workers} --batch-size 300")
        print(f"   → Vitesse estimée: ~12-18 scl/s")
        print(f"   → Temps pour 30000 clubs: ~30-45 minutes")
        print()
    
    print("⚡ Configuration RAPIDE:")
    fast_workers = min(recommended_workers_conservative, 25)
    print(f"   python src/scrape_all_parallel.py --workers {fast_workers} --batch-size 200")
    print(f"   → Vitesse estimée: ~10-15 scl/s")
    print(f"   → Temps pour 30000 clubs: ~35-50 minutes")
    print()
    
    print("⚖️  Configuration ÉQUILIBRÉE:")
    balanced_workers = min(recommended_workers_conservative, 15)
    print(f"   python src/scrape_all_parallel.py --workers {balanced_workers} --batch-size 100")
    print(f"   → Vitesse estimée: ~7-10 scl/s")
    print(f"   → Temps pour 30000 clubs: ~50-70 minutes")
    print()
    
    # Avertissements
    if ram_available_gb < 3:
        print("⚠️  ATTENTION: RAM disponible faible (<3 GB)")
        print(f"   Avec seulement {ram_available_gb:.1f} GB disponible, limitez à {max_workers_by_ram_available} workers max")
        print("   Conseil: Fermez d'autres applications pour libérer de la RAM")
        print()
    elif ram_available_gb < 5:
        print("⚠️  NOTE: RAM disponible modérée")
        print(f"   {ram_available_gb:.1f} GB disponible - utilisez la config RAPIDE ou ÉQUILIBRÉE")
        print()
    
    if cpu_cores < 4:
        print("⚠️  ATTENTION: CPU limité (<4 cœurs)")
        print("   Recommandation: Utilisez max 8-10 workers")
        print()

if __name__ == "__main__":
    try:
        check_system_resources()
    except ImportError:
        print("⚠️  Le module 'psutil' n'est pas installé.")
        print("   Installation: pip install psutil")
        print()
        print("Informations système basiques:")
        print(f"   Système: {platform.system()} {platform.release()}")
        print(f"   Processeur: {platform.processor()}")

