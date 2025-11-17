"""
Script pour nettoyer et organiser le projet
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Nettoie et organise les fichiers du projet"""
    
    base_dir = Path(__file__).parent.parent
    print("=" * 60)
    print("🧹 NETTOYAGE DU PROJET")
    print("=" * 60)
    print()
    
    # 1. Créer le dossier pour les résultats de test
    test_results_dir = base_dir / "data" / "test_results"
    test_results_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Dossier créé/vérifié: {test_results_dir}")
    
    # 2. Déplacer les CSV de test
    csv_files = list(base_dir.glob("test_*.csv"))
    moved_csv = 0
    for csv_file in csv_files:
        dest = test_results_dir / csv_file.name
        shutil.move(str(csv_file), str(dest))
        print(f"  📦 Déplacé: {csv_file.name} -> data/test_results/")
        moved_csv += 1
    
    if moved_csv == 0:
        print("  ℹ️  Aucun CSV de test à déplacer")
    else:
        print(f"  ✅ {moved_csv} fichier(s) CSV déplacé(s)")
    print()
    
    # 3. Déplacer les JSON de test (sauf ceux dans data/)
    json_files = list(base_dir.glob("test_*.json"))
    moved_json = 0
    for json_file in json_files:
        # Ne pas déplacer ceux déjà dans data/
        if "data" not in str(json_file):
            dest = test_results_dir / json_file.name
            if dest.exists():
                # Si existe déjà, supprimer l'ancien
                json_file.unlink()
                print(f"  🗑️  Supprimé doublon: {json_file.name}")
            else:
                shutil.move(str(json_file), str(dest))
                print(f"  📦 Déplacé: {json_file.name} -> data/test_results/")
            moved_json += 1
    
    if moved_json == 0:
        print("  ℹ️  Aucun JSON de test à déplacer")
    else:
        print(f"  ✅ {moved_json} fichier(s) JSON déplacé(s)")
    print()
    
    # 4. Vérifier les fichiers obsolètes dans src/
    print("📁 Vérification des fichiers dans src/")
    src_dir = base_dir / "src"
    src_files = list(src_dir.glob("*.py"))
    
    # Fichiers à garder
    keep_files = {
        "scraper_by_scl.py",
        "scraper_by_scl_parallel.py",
        "scrape_all_parallel.py",
        "scrape_to_csv.py",
        "__init__.py"
    }
    
    obsolete_files = []
    for src_file in src_files:
        if src_file.name not in keep_files:
            obsolete_files.append(src_file)
    
    if obsolete_files:
        print(f"  ⚠️  {len(obsolete_files)} fichier(s) potentiellement obsolète(s):")
        for f in obsolete_files:
            print(f"     - {f.name}")
        print("  💡 Vérifiez manuellement avant de supprimer")
    else:
        print("  ✅ Tous les fichiers src/ sont à jour")
    print()
    
    # 5. Nettoyer les fichiers de documentation obsolètes dans docs/
    print("📚 Vérification de la documentation")
    docs_dir = base_dir / "docs"
    if docs_dir.exists():
        doc_files = list(docs_dir.glob("*.md"))
        # Fichiers de documentation à garder
        keep_docs = {
            "GUIDE_PARALLEL.md",
            "README.md"
        }
        
        obsolete_docs = []
        for doc_file in doc_files:
            if doc_file.name not in keep_docs:
                obsolete_docs.append(doc_file)
        
        if obsolete_docs:
            print(f"  ⚠️  {len(obsolete_docs)} fichier(s) de doc potentiellement obsolète(s):")
            for f in obsolete_docs:
                print(f"     - {f.name}")
            print("  💡 Vérifiez manuellement avant de supprimer")
        else:
            print("  ✅ Documentation à jour")
    print()
    
    # 6. Nettoyer les fichiers à la racine
    print("📄 Fichiers à la racine")
    root_files_to_check = [
        "PROJECT_STRUCTURE.md",
        "QUICK_START.md",
        "OPTIMISATIONS_VITESSE.md",
        "STRUCTURE_FINALE.md"
    ]
    
    found_root_files = []
    for fname in root_files_to_check:
        fpath = base_dir / fname
        if fpath.exists():
            found_root_files.append(fpath)
    
    if found_root_files:
        print(f"  ℹ️  {len(found_root_files)} fichier(s) de documentation à la racine:")
        for f in found_root_files:
            print(f"     - {f.name}")
        print("  💡 Considérez les déplacer dans docs/")
    else:
        print("  ✅ Racine propre")
    print()
    
    # 7. Résumé
    print("=" * 60)
    print("✅ NETTOYAGE TERMINÉ")
    print("=" * 60)
    print(f"📦 Fichiers de test organisés dans: data/test_results/")
    print(f"   - {moved_csv} CSV déplacé(s)")
    print(f"   - {moved_json} JSON déplacé(s)")
    print()
    print("💡 Prochaines étapes:")
    print("   1. Vérifiez les fichiers obsolètes signalés")
    print("   2. Organisez la documentation si nécessaire")
    print("   3. Lancez le scraping complet avec:")
    print("      python src/scrape_all_parallel.py --workers 20 --batch-size 200")

if __name__ == "__main__":
    cleanup_project()

