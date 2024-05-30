# -*- coding: utf-8 -*-
# !/usr/bin/env python3

"""01_scrapping_textiles.py

* Extraction (web scrapping) des informations sur les textiles
à partir du site http://weaving.dcs.bbk.ac.uk/TextileProductSearch.php
dans une structure intermédiaire JSON.

N.B. : On utilise Selenium pour automatiser le navigateur et
lui faire exécuter des actions (comme cliquer sur un bouton,
remplir un formulaire, etc.). Requis car le site ne dispose pas
d'une API REST pour récupérer les données et utilise du JavaScript
et du PHP pour générer dynamiquement le contenu de la page.

Input: http://weaving.dcs.bbk.ac.uk/TextileProductSearch.php
Output: textiles.json

Date: 2023-10-20
"""

import time
import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from lxml import html
from tqdm import tqdm


if __name__ == '__main__':
    # Début du programme
    # Définir le type de navigateur
    BROWSER_TYPE = 'chrome' # mettre 'firefox' sinon
    # Définir le nombre de pages à parcourir
    TOTAL_PAGE = 118
    # Définir le nombre de textiles à récupérer
    TOTAL_TEXTILES = 700
    # Création d'une instance de navigateur
    browser = webdriver.Chrome() if BROWSER_TYPE == 'chrome' else webdriver.Firefox()
    # Attendre que le navigateur soit complètement chargé
    browser.implicitly_wait(30)
    # Accéder à la page (en l'occurence le script va accéder à la page de recherche de textiles)
    browser.get("http://weaving.dcs.bbk.ac.uk/TextileProductSearch.php")
    # Attendre que la page soit complètement chargée
    browser.implicitly_wait(10)
    # On crée une structure de données pour stocker les informations sur les textiles
    # et sur laquelle on pourra itérer pour traiter les données plus tard
    # Exemple :
    # textiles = {
    #     'textile_id': {
    #         'image_ref': 'image_ref', # pour récupérer l'image
    #         'description': 'description', # pour récupérer la description
    #         'details': 'details' # pour récupérer les détails
    #     },
    #     ...
    # }
    textiles = {}
    browser.implicitly_wait(10)
    # barre de progression pour
    # suivre l'avancement du script (peut être long dans certains cas)
    for page in tqdm(range(1, TOTAL_PAGE)):
        # Attendre que la page soit complètement chargée
        time.sleep(10)  # On peut augmenter le délai en cas d'erreur de chargement
        # Récupérer le contenu actuel de la page
        content = browser.page_source
        # Parser le contenu de la page
        tree = html.fromstring(content)
        # Récupérer les liens des textiles
        links = tree.xpath(
            "/html/body/div[@id='container']/div[@id='content']/div[@id='contentTextProdSearch']/div[@id='gallery']/div[@id='images']/table/tbody/tr/td/a")
        # Itérer sur les liens des textiles de la page
        # et récupérer les informations sur les textiles qui nous intéressent
        ## Récupération de l'ensemble des références des images dans le json intermédiaire
        for link in links:
            textiles[link.get('data-textileid')] = {
                'image_ref': [filename.split('/')[-1] for filename in link.xpath('.//@data-imgcsv')[0].split(';')],
                'description': link.get('data-description'),
                'details': link.get('data-details')
            }
        # Cliquer sur le bouton next pour accéder à la page suivante (sauf pour la dernière page)
        if page != TOTAL_PAGE-1:
            browser.implicitly_wait(20)
            WebDriverWait(browser, 100).until(EC.visibility_of_element_located(
                (By.XPATH, "//a[contains(@class, 'numbering') and text() = 'next']"))).click()
    # on écrit les données dans un fichier json
    with open('textiles.json', 'w') as outfile:
        json.dump(textiles, outfile, ensure_ascii=False, indent=4)
    # ~TESTS~ [OPT.]
    """
    # Le nombre total de textiles récupérés est-il correct ?
    assert TOTAL_TEXTILES == len(textiles)
    # Est-ce qu'il n'y a pas de doublons ?
    assert TOTAL_TEXTILES == len(set(textiles.keys()))
    """
    print("Fin du programme de scrapping des textiles.")



