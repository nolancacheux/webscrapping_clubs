"""
Scraper optimisé utilisant directement les numéros d'affiliation (scl)
pour accéder aux pages de détail des clubs.
"""

import json
import time
from typing import List, Optional
from playwright.sync_api import sync_playwright, Page, Browser
from dataclasses import dataclass
import re


@dataclass
class ClubData:
    """Structure de données pour un club"""
    nom: str
    numero_affiliation: Optional[str] = None
    email: Optional[str] = None  # Coalesce: email_principal ou email_officiel
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    url_detail: Optional[str] = None
    
    # Champs internes pour extraction (non utilisés dans la sortie finale)
    email_officiel: Optional[str] = None
    email_principal: Optional[str] = None


class SCLScraper:
    """Scraper utilisant les numéros d'affiliation (scl)"""
    
    def __init__(self, headless: bool = True, slow_mo: int = 0):
        """
        Initialise le scraper.
        
        Args:
            headless: Mode headless du navigateur
            slow_mo: Délai entre les actions (ms)
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def __enter__(self):
        """Context manager entry"""
        self.playwright = sync_playwright().start()
        launch_options = {
            'slow_mo': self.slow_mo
        }
        if self.headless:
            launch_options['headless'] = True
        
        try:
            self.browser = self.playwright.chromium.launch(**launch_options)
        except Exception as e:
            if 'headless_shell' in str(e) or 'Executable doesn\'t exist' in str(e):
                print("⚠️  Problème avec chromium_headless_shell, utilisation de chromium normal...")
                launch_options.pop('headless', None)
                self.browser = self.playwright.chromium.launch(**launch_options)
            else:
                raise
        
        self.page = self.browser.new_page()
        self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def extract_club_by_scl(self, scl: int, base_url: str = "https://gironde.fff.fr") -> Optional[ClubData]:
        """
        Extrait les données d'un club par son numéro d'affiliation.
        
        Args:
            scl: Numéro d'affiliation du club
            base_url: URL de base du district (peu importe, le scl est unique)
            
        Returns:
            Objet ClubData avec les informations extraites, ou None si le club n'existe pas
        """
        url = f"{base_url}/recherche-clubs?scl={scl}"
        
        try:
            # Utiliser "domcontentloaded" au lieu de "networkidle" pour éviter les attentes infinies
            # Certaines pages peuvent avoir des requêtes réseau qui ne se terminent jamais
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=5000)  # Timeout de 5s pour fiabilité
            except Exception as e:
                # Si timeout, essayer une fois de plus
                try:
                    self.page.goto(url, wait_until="domcontentloaded", timeout=5000)  # Timeout de 5s pour fiabilité
                except:
                    return None
            # Attendre un peu pour que le contenu Angular se charge
            time.sleep(0.3)  # Délai de 0.3s pour laisser Angular charger le contenu
            
            # Vérifier si la page contient un club valide
            # Si le club n'existe pas, la page peut être vide ou contenir un message d'erreur
            page_text = self.page.content()
            
            # Chercher le numéro d'affiliation dans la page
            affil_match = re.search(r'N[°\s]*affiliation[:\s]*(\d+)', page_text, re.IGNORECASE)
            if not affil_match:
                # Pas de club trouvé à ce numéro
                return None
            
            numero_affiliation = affil_match.group(1)
            
            # Extraire le nom du club d'abord pour vérifier si c'est un vrai club
            nom = None
            try:
                # Stratégie 1: Chercher dans le h1 avec la structure Angular (app-club)
                # Structure: <h1>CLUB DISTRICT GERS</h1><h2>N°affiliation: 6504</h2>
                try:
                    # Chercher le h1 dans le composant Angular app-club
                    h1_elements = self.page.query_selector_all('app-club h1, .club-title h1, h1')
                    for h1 in h1_elements:
                        text = h1.inner_text().strip()
                        text_lower = text.lower()
                        
                        # Filtrer les éléments de navigation
                        excluded = ['accueil', 'gironde', 'paris', 'ensemble', 'écrivons']
                        is_excluded = any(word in text_lower for word in excluded)
                        
                        # Exclure "district de la" mais pas "club district" ou "club ligue"
                        if 'district de la' in text_lower or ('district de' in text_lower and 'club district' not in text_lower):
                            is_excluded = True
                        
                        # Ne pas exclure si c'est "CLUB LIGUE" (ex: "CLUB LIGUE ALSACE")
                        if 'club ligue' in text_lower:
                            is_excluded = False
                        
                        if (text and len(text) > 5 and len(text) < 100 and
                            not is_excluded and
                            any(c.isalpha() for c in text)):
                            nom = text
                            break
                except Exception as e:
                    # Ignorer les erreurs dans cette stratégie
                    pass
                
                # Stratégie 2: Chercher le nom dans le contenu HTML avec regex
                if not nom:
                    excluded_words = ['accueil', 'gironde', 'paris', 
                                     'ensemble', 'écrivons', 'résultats', 'calendrier']
                    # Ne pas exclure "ligue" si c'est dans "CLUB LIGUE"
                    
                    nom_patterns = [
                        # Pattern 1: Nom dans h1 avant h2 avec "N°affiliation"
                        r'<h1[^>]*>([A-Z][A-Z\s\.\-\']{5,80}?)</h1>\s*<h2[^>]*>N[°\s]*affiliation',
                        # Pattern 2: Nom avant "N°affiliation" dans h2
                        r'<h2[^>]*>([A-Z][A-Z\s\.\-\']{5,80}?)</h2>\s*N[°\s]*affiliation[:\s]*\d+',
                        # Pattern 3: Nom en majuscules avant "N°affiliation" (texte brut)
                        r'([A-Z][A-Z\s\.\-\']{5,80}?)\s*N[°\s]*affiliation[:\s]*\d+',
                    ]
                    
                    for pattern in nom_patterns:
                        match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                        if match:
                            potential_nom = match.group(1).strip()
                            potential_nom_lower = potential_nom.lower()
                            
                            # Filtrer les faux positifs
                            # Exclure seulement si c'est "District de la X" ou "Ligue de X", pas "CLUB DISTRICT X"
                            is_excluded = False
                            for word in excluded_words:
                                if word in potential_nom_lower:
                                    # Vérifier le contexte - si c'est "district de la" ou "ligue de", exclure
                                    if word == 'district' and ('district de la' in potential_nom_lower or 
                                                               'district de' in potential_nom_lower and 
                                                               'club district' not in potential_nom_lower):
                                        is_excluded = True
                                        break
                                    elif word != 'district':  # Pour les autres mots, exclure directement
                                        is_excluded = True
                                        break
                            
                            if (len(potential_nom) > 5 and len(potential_nom) < 100 and
                                not is_excluded and
                                any(c.isalpha() for c in potential_nom) and
                                (len(potential_nom.split()) > 1 or len(potential_nom) > 8)):
                                nom = potential_nom
                                break
                
                # Stratégie 2: Chercher dans les éléments HTML près du numéro d'affiliation
                if not nom:
                    # Trouver l'élément qui contient le numéro d'affiliation
                    try:
                        affil_element = self.page.query_selector('text=/N[°\\s]*affiliation/i')
                        if affil_element:
                            # Chercher le h2 le plus proche AVANT le numéro d'affiliation
                            all_h2 = self.page.query_selector_all('h2')
                            
                            # Obtenir la position du numéro d'affiliation
                            affil_box = affil_element.bounding_box()
                            if affil_box:
                                affil_y = affil_box['y']
                                
                                # Trouver le h2 le plus proche au-dessus
                                closest_h2 = None
                                min_distance = float('inf')
                                
                                for h2 in all_h2:
                                    h2_box = h2.bounding_box()
                                    if h2_box:
                                        h2_y = h2_box['y']
                                        # H2 doit être au-dessus (y plus petit) et proche
                                        if h2_y < affil_y and (affil_y - h2_y) < 300:
                                            distance = affil_y - h2_y
                                            if distance < min_distance:
                                                min_distance = distance
                                                closest_h2 = h2
                                
                                if closest_h2:
                                    text = closest_h2.inner_text().strip()
                                    text_lower = text.lower()
                                    
                                    # Filtrer les éléments de navigation
                                    # Ne pas exclure "district" si c'est dans "CLUB DISTRICT X"
                                    excluded_words = ['accueil', 'ligue', 'gironde', 'paris', 
                                                     'ensemble', 'écrivons', 'résultats', 'calendrier',
                                                     'équipes', 'staff', 'terrains', 'siège social']
                                    is_excluded = False
                                    for word in excluded_words:
                                        if word in text_lower:
                                            is_excluded = True
                                            break
                                    # Exclure "district de la" mais pas "club district"
                                    if 'district de la' in text_lower or 'district de' in text_lower:
                                        if 'club district' not in text_lower:
                                            is_excluded = True
                                    
                                    if (text and len(text) > 5 and len(text) < 100 and
                                        not is_excluded and
                                        any(c.isalpha() for c in text) and
                                        (len(text.split()) > 1 or len(text) > 8)):
                                        nom = text
                    except:
                        pass
                    
                    # Si toujours pas trouvé, chercher tous les h2 et filtrer
                    if not nom:
                        excluded_words = ['accueil', 'ligue', 'gironde', 'paris', 
                                         'ensemble', 'écrivons', 'n°affiliation', 'résultats',
                                         'calendrier', 'équipes', 'staff', 'terrains', 'siège social',
                                         'installations', 'rencontres', 'prochaines', 'dernières']
                        
                        h2_elements = self.page.query_selector_all('h2')
                        for h2 in h2_elements:
                            text = h2.inner_text().strip()
                            text_lower = text.lower()
                            
                            is_navigation = False
                            for word in excluded_words:
                                if word in text_lower:
                                    is_navigation = True
                                    break
                            # Exclure "district de la" mais pas "club district"
                            if 'district de la' in text_lower or ('district de' in text_lower and 'club district' not in text_lower):
                                is_navigation = True
                            
                            if (text and len(text) > 5 and len(text) < 100 and
                                not is_navigation and
                                any(c.isalpha() for c in text) and
                                (len(text.split()) > 1 or len(text) > 8)):
                                nom = text
                                break
                    
                    # Si pas trouvé, chercher dans les autres éléments
                    if not nom:
                        excluded_words = ['accueil', 'ligue', 'gironde', 'paris', 
                                         'ensemble', 'écrivons', 'résultats', 'calendrier',
                                         'équipes', 'staff', 'terrains', 'siège social']
                        
                        nom_selectors = [
                            'h1:not([class*="title"]):not([class*="slogan"])',
                            '[class*="club-name"]',
                            '[class*="name-club"]',
                            'strong',
                        ]
                        for selector in nom_selectors:
                            try:
                                elements = self.page.query_selector_all(selector)
                                for element in elements:
                                    text = element.inner_text().strip()
                                    text_lower = text.lower()
                                    
                                    is_excluded = False
                                    for word in excluded_words:
                                        if word in text_lower:
                                            is_excluded = True
                                            break
                                    # Exclure "district de la" mais pas "club district"
                                    if 'district de la' in text_lower or ('district de' in text_lower and 'club district' not in text_lower):
                                        is_excluded = True
                                    
                                    if (text and len(text) > 5 and len(text) < 100 and
                                        not is_excluded and
                                        any(c.isalpha() for c in text) and
                                        (len(text.split()) > 1 or len(text) > 8)):
                                        nom = text
                                        break
                                if nom:
                                    break
                            except:
                                continue
                
                # Stratégie 3: Chercher dans le titre de la page
                if not nom:
                    title = self.page.title()
                    if title:
                        # Extraire le nom du titre (généralement avant le premier | ou -)
                        title_parts = re.split(r'[|\-]', title)
                        if title_parts:
                            potential_nom = title_parts[0].strip()
                            if (len(potential_nom) > 5 and 
                                'recherche' not in potential_nom.lower() and
                                'district' not in potential_nom.lower()):
                                nom = potential_nom
            except Exception as e:
                print(f"      ⚠️  Erreur extraction nom: {e}")
                pass
            
            if not nom:
                return None
            
            # Accepter le numéro d'affiliation "0" si un nom de club valide a été trouvé
            # (ex: "CLUB FEDERATION FRANCAISE DE FOOTBALL" a affiliation 0)
            # Le numéro "0" est valide pour certains clubs spéciaux comme la FFF elle-même
            if numero_affiliation == "0" and nom:
                # C'est valide, continuer avec l'extraction
                pass
            elif not numero_affiliation:
                return None
            
            # Extraire les emails (amélioré pour trouver tous les types)
            email_principal = None
            email_officiel = None
            email_autre = None
            
            # Chercher "Email principal" d'abord (priorité 1)
            email_patterns_principal = [
                r'Email principal[:\s]*([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'<b>Email principal</b>\s*:\s*([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'Email principal[:\s]*([^\s<>]+@[^\s<>]+)',
            ]
            
            for pattern in email_patterns_principal:
                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    email_principal = match.group(1).strip()
                    break
            
            # Chercher "Email officiel" (priorité 2)
            email_patterns_officiel = [
                r'Email officiel[:\s]*([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'<b>Email officiel</b>\s*:\s*([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            ]
            
            for pattern in email_patterns_officiel:
                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    email_officiel = match.group(1).strip()
                    break
            
            # Chercher "Email autre" (priorité 3)
            email_patterns_autre = [
                r'Email autre[:\s]*([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'<b>Email autre</b>\s*:\s*([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'Email autre[:\s]*([^\s<>]+@[^\s<>]+)',
            ]
            
            for pattern in email_patterns_autre:
                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    # Peut contenir plusieurs emails séparés par des virgules
                    emails_str = match.group(1).strip()
                    # Prendre le premier email si plusieurs
                    email_autre = emails_str.split(',')[0].strip()
                    break
            
            # Coalesce: email_principal > email_officiel > email_autre
            email = email_principal or email_officiel or email_autre
            
            # Extraire le téléphone (amélioré pour trouver tous les types)
            telephone_travail = None
            telephone_domicile = None
            telephone_autre = None
            mobile_personnel = None
            
            # Chercher "Téléphone travail" (priorité 1)
            # Patterns améliorés pour capturer les numéros avec espaces et formats courts
            phone_patterns_travail = [
                r'Téléphone travail\s*:\s*([0-9\s\.\-\(\)]{6,})',
                r'<b>Téléphone travail</b>\s*:\s*([0-9\s\.\-\(\)]{6,})',
                r'Téléphone travail[:\s]+([0-9\s\.\-\(\)]{6,})',
            ]
            
            for pattern in phone_patterns_travail:
                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    phone_raw = match.group(1).strip()
                    # Nettoyer et extraire uniquement les chiffres
                    phone_clean = re.sub(r'[^\d]', '', phone_raw)
                    # Accepter les numéros de 6 chiffres minimum (certains numéros courts existent)
                    if len(phone_clean) >= 6:
                        telephone_travail = phone_clean
                        break
            
            # Chercher "Téléphone domicile" (priorité 2)
            phone_patterns_domicile = [
                r'Téléphone domicile\s*:\s*([0-9\s\.\-\(\)]{6,})',
                r'<b>Téléphone domicile</b>\s*:\s*([0-9\s\.\-\(\)]{6,})',
                r'Téléphone domicile[:\s]+([0-9\s\.\-\(\)]{6,})',
            ]
            
            for pattern in phone_patterns_domicile:
                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    phone_raw = match.group(1).strip()
                    phone_clean = re.sub(r'[^\d]', '', phone_raw)
                    if len(phone_clean) >= 6:
                        telephone_domicile = phone_clean
                        break
            
            # Chercher "Mobile personnel" (priorité 3)
            phone_patterns_mobile = [
                r'Mobile personnel\s*:\s*([0-9\s\.\-\(\)]{6,})',
                r'<b>Mobile personnel</b>\s*:\s*([0-9\s\.\-\(\)]{6,})',
                r'Mobile personnel[:\s]+([0-9\s\.\-\(\)]{6,})',
            ]
            
            for pattern in phone_patterns_mobile:
                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    phone_raw = match.group(1).strip()
                    phone_clean = re.sub(r'[^\d]', '', phone_raw)
                    if len(phone_clean) >= 6:
                        mobile_personnel = phone_clean
                        break
            
            # Chercher "Téléphone autre" (priorité 4) - peut y en avoir plusieurs
            phone_patterns_autre = [
                r'Téléphone autre\s*:\s*([0-9\s\.\-\(\)]{6,})',
                r'<b>Téléphone autre</b>\s*:\s*([0-9\s\.\-\(\)]{6,})',
                r'Téléphone autre[:\s]+([0-9\s\.\-\(\)]{6,})',
            ]
            
            for pattern in phone_patterns_autre:
                # Chercher toutes les occurrences (peut y en avoir plusieurs)
                matches = re.finditer(pattern, page_text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    phone_raw = match.group(1).strip()
                    phone_clean = re.sub(r'[^\d]', '', phone_raw)
                    if len(phone_clean) >= 6:
                        # Prendre le premier trouvé
                        if not telephone_autre:
                            telephone_autre = phone_clean
                        break
                if telephone_autre:
                    break
            
            # Chercher "Téléphone" générique (priorité 5)
            if not telephone_travail and not telephone_domicile and not mobile_personnel and not telephone_autre:
                phone_patterns_generic = [
                    r'Téléphone\s*:\s*([0-9\s\.\-\(\)]{6,})',
                    r'Tel\s*:\s*([0-9\s\.\-\(\)]{6,})',
                ]
                
                for pattern in phone_patterns_generic:
                    match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                    if match:
                        phone_raw = match.group(1).strip()
                        phone_clean = re.sub(r'[^\d]', '', phone_raw)
                        if len(phone_clean) >= 6:
                            telephone_autre = phone_clean
                            break
            
            # Coalesce: travail > domicile > mobile > autre
            telephone = telephone_travail or telephone_domicile or mobile_personnel or telephone_autre
            
            # Extraire l'adresse (Siège social)
            adresse = None
            # Chercher dans la structure Angular spécifique
            try:
                # Structure: <span class="title-ground">Siège social</span><br><b>Adresse :</b><span> Route de lavacant   - 32000 - AUCH </span>
                # Chercher directement le span avec l'adresse après "Adresse :"
                address_span = self.page.query_selector('.txt-map-siege b:contains("Adresse") + span', timeout=1000)
                if address_span:
                    adresse = address_span.inner_text().strip()
                else:
                    # Fallback: chercher dans tous les spans
                    address_elements = self.page.query_selector_all('.txt-map-siege span', timeout=1000)
                    for elem in address_elements[:10]:  # Limiter à 10 pour éviter les boucles longues
                        try:
                            text = elem.inner_text().strip()
                            if 'adresse' in text.lower() and len(text) > 15:
                                # Extraire l'adresse après "Adresse :"
                                match = re.search(r'Adresse\s*:\s*(.+)', text, re.IGNORECASE)
                                if match:
                                    adresse = match.group(1).strip()
                                    break
                        except:
                            continue
            except:
                pass
            
            # Fallback: regex dans le HTML
            if not adresse:
                # Pattern pour trouver l'adresse après "Adresse :"
                address_patterns = [
                    r'<b>Adresse\s*:</b>\s*<span[^>]*>([^<]+)</span>',
                    r'Adresse\s*:\s*([^<\n]+(?:-\s*\d{5}\s*-\s*[A-Z\s]+)?)',
                    r'Siège social[:\s]*([^<]+)',
                ]
                
                for pattern in address_patterns:
                    address_match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                    if address_match:
                        adresse = re.sub(r'<[^>]+>', '', address_match.group(1)).strip()
                        # Nettoyer l'adresse
                        adresse = re.sub(r'\s+', ' ', adresse)
                        if len(adresse) > 10:  # Vérifier que c'est une adresse valide
                            break
            
            club_data = ClubData(
                nom=nom,
                numero_affiliation=numero_affiliation,
                email=email,  # Coalesce: email_principal ou email_officiel
                telephone=telephone,
                adresse=adresse,
                url_detail=url,
                email_officiel=email_officiel,  # Gardé pour référence interne
                email_principal=email_principal  # Gardé pour référence interne
            )
            
            return club_data
            
        except Exception as e:
            # Ne pas afficher les erreurs de timeout, c'est normal pour les numéros invalides
            if "timeout" not in str(e).lower() and "timeout" not in str(type(e)).lower():
                print(f"      ⚠️  Erreur pour scl={scl}: {e}")
            return None
    
    def scrape_range(self, start_scl: int, end_scl: int, base_url: str = "https://gironde.fff.fr", 
                     progress_interval: int = 100) -> List[ClubData]:
        """
        Scrape une plage de numéros d'affiliation.
        
        Args:
            start_scl: Numéro de début
            end_scl: Numéro de fin
            base_url: URL de base du district
            progress_interval: Afficher le progrès tous les N clubs
            
        Returns:
            Liste des clubs trouvés
        """
        clubs_data = []
        total = end_scl - start_scl + 1
        
        print(f"🔢 Scraping des numéros scl de {start_scl} à {end_scl} ({total} clubs à tester)\n")
        
        for scl in range(start_scl, end_scl + 1):
            if (scl - start_scl) % progress_interval == 0:
                progress = ((scl - start_scl) / total) * 100
                print(f"  📊 Progression: {progress:.1f}% ({scl - start_scl}/{total}) - {len(clubs_data)} clubs trouvés")
            
            club_data = self.extract_club_by_scl(scl, base_url)
            
            if club_data:
                clubs_data.append(club_data)
                if len(clubs_data) <= 5 or (scl - start_scl) % progress_interval == 0:
                    print(f"    ✅ scl={scl}: {club_data.nom}")
        
        print(f"\n✅ Scraping terminé: {len(clubs_data)} clubs trouvés sur {total} testés")
        return clubs_data


def main():
    """Fonction principale pour tester le scraper par scl"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape les clubs FFF par numéro d'affiliation")
    parser.add_argument('--start', type=int, default=1, help='Numéro scl de début')
    parser.add_argument('--end', type=int, default=100, help='Numéro scl de fin')
    parser.add_argument('--base-url', type=str, default='https://gironde.fff.fr', 
                       help='URL de base (peu importe, le scl est unique)')
    parser.add_argument('--headless', action='store_true', help='Mode headless')
    parser.add_argument('--output', type=str, default='clubs_scl_scraped.json', 
                       help='Fichier de sortie JSON')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏆 SCRAPING PAR NUMÉRO D'AFFILIATION (SCL)")
    print("=" * 60)
    print(f"Plage: {args.start} - {args.end}")
    print(f"URL de base: {args.base_url}")
    print("=" * 60)
    print()
    
    with SCLScraper(headless=args.headless if args.headless else True, slow_mo=0) as scraper:
        clubs_data = scraper.scrape_range(args.start, args.end, args.base_url)
        
        # Sauvegarder les résultats
        if clubs_data:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump([club.__dict__ for club in clubs_data], f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Résultats sauvegardés dans: {args.output}")
            print(f"\n📊 Statistiques:")
            print(f"   Clubs trouvés: {len(clubs_data)}")
            print(f"   Taux de réussite: {(len(clubs_data)/(args.end-args.start+1)*100):.2f}%")
            
            # Afficher quelques exemples
            print(f"\n📋 Exemples de clubs trouvés:")
            for club in clubs_data[:5]:
                print(f"   - {club.nom} (scl: {club.numero_affiliation})")
                if club.email_officiel:
                    print(f"     📧 {club.email_officiel}")
                if club.telephone:
                    print(f"     📞 {club.telephone}")
        else:
            print("\n⚠️  Aucun club trouvé dans cette plage")


if __name__ == "__main__":
    main()

