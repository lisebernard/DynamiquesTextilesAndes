# -*- coding: utf-8 -*-
# !/usr/bin/env python3

"""02_clean_textiles.py

* Traitement des données récupérées par le script précédent 01_scrapping_textiles.py
et création d'une vue nettoyée des données sous forme d'une dataframe.
* Téléchargement en local des images dans un dossier
images durant le pré-traitement des données.

Date: 2023-10-20

* Modification du script par Lise Bernard pour télécharger l'ensemble des images pour chaque pièce textile et modifications du nom des colonnes

Input: textiles.json
Output: textiles.csv, images_jpg/ (contient les photographies téléchargées), images_png/ (contient les schémas téléchargés)

Date: 2023-11-07
"""
import os

import json
from bs4 import BeautifulSoup
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm   


def download_image_jpg(image_url: str) -> str:
   
    image_name = image_url.split('/')[-1]
    image_path = os.path.join(IMAGES_DIR_jpg, image_name)
    # si l'image n'existe pas déjà
    if not os.path.exists(image_path):
        # télécharger l'image
        response = requests.get(image_url, stream=True)
        # sauvegarder l'image
        with open(image_path, 'wb') as outfile:
            outfile.write(response.content)
    return image_name

def download_image_png(image_url: str) -> str:
   
    image_name = image_url.split('/')[-1]
    image_path = os.path.join(IMAGES_DIR_png, image_name)
    # si l'image n'existe pas déjà
    if not os.path.exists(image_path):
        # télécharger l'image
        response = requests.get(image_url, stream=True)
        # sauvegarder l'image
        with open(image_path, 'wb') as outfile:
            outfile.write(response.content)
    return image_name


def fast_download_process_image(data_to_download: dict) -> None:
    """Télécharger les images en parallèle."""
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = []
        for key, value in data_to_download.items() :
            image_refs = value.get("image_ref", [])
            for image_ref in image_refs:
                image_url = f"http://weaving.dcs.bbk.ac.uk/SVN/image/g/{image_ref}"
                #Distinction entre images jpg et images png
                if image_url.split(".")[-1] == "jpg" :
                    futures.append(
                        executor.submit(download_image_jpg, image_url)
                    )
                if image_url.split(".")[-1] == "png" :
                    futures.append(
                        executor.submit(download_image_png, image_url)
                    )
    print("Téléchargement des images finalisé")


def get_column_name(span):
    """Génère le nom de colonne à partir d'une balise span.
    """
    return f"{span.get_text(strip=True).rstrip(':').lower()}"


def get_links_for_span(span, next_span=None):
    """Récupère tous les liens associés à un élément span donné.
    On considère ici que le span avec la classe 'detail' est le titre de la colonne
    puis les a suivants sont les valeurs de la colonne.
    """
    if next_span:
        return [link for link in span.find_all_next('a')
                if link.find_previous('span', class_='detail') == span and
                link.find_next('span', class_='detail') == next_span]
    return span.find_all_next('a')


def extract_row(key: str, value: dict) -> dict:
    """
    Extrait les informations d'une entrée du dictionnaire pour créer un enregistrement de
    la future dataframe.
    """
    row = {
        "ID": key,
        "description": BeautifulSoup(value["description"], 'html.parser').text,
        "image": value["image_ref"]
    }

    soup = BeautifulSoup(value["details"], 'html.parser')
    spans = soup.find_all('span', class_='detail')

    for i, span in enumerate(spans):
        next_span = spans[i + 1] if i < len(spans) - 1 else None
        links = get_links_for_span(span, next_span)
        values = [link.get_text(strip=True) for link in links]
        row[get_column_name(span)] = ", ".join(values)

    return row


def process_data(data_dict: dict) -> list[dict]:
    """Traite le dictionnaire de données et retourne une liste d'enregistrements
    pour la future dataframe.
    """
    return [extract_row(key, value) for key, value in tqdm(data_dict.items(), desc='Processing data...')]


def save_as_csv(rows: list[dict], sep: str = ';', encoding: str = 'utf-8', index: bool = False) -> None:
    """Sauvegarde la liste des d'enregistrements sous forme d'un fichier CSV.
    """
    df = pd.DataFrame(rows)
    df.to_csv('textiles.csv', index=index, sep=sep, encoding=encoding)


if __name__ == '__main__':
    # Début du programme
    # dossier par défaut dans lequel on va sauvegarder les images 
    # distinction entre les jpg (photographies) et les png (schématisation des motifs).
    IMAGES_DIR_jpg = 'images_jpg/'
    IMAGES_DIR_png = 'images_png/'
    JSON_FILE = 'textiles.json'
    # créer le dossier s'il n'existe pas
    if not os.path.exists(IMAGES_DIR_jpg):
        os.makedirs(IMAGES_DIR_jpg)

    if not os.path.exists(IMAGES_DIR_png):
        os.makedirs(IMAGES_DIR_png)

    # charger les données depuis le fichier json
    with open(JSON_FILE, 'r') as infile:
        data_dict = json.load(infile)

    # ** Étape 1 : télécharger les images **
    fast_download_process_image(data_dict)

    # ** Étape 2 : pré-traitement des données **
    # Contient les futures enregistrements de la dataframe
    rows = process_data(data_dict)
    save_as_csv(rows)

    print("Fin du programme de pré-traitement des données.")
