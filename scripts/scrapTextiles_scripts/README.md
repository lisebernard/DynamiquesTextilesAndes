## Installation

* Requis : 
  - Python 3.8 ou +
  - Un navigateur web Firefox ou Chrome

1. Installation des dépendances :

```bash
#virtualenv -p python3.9 venv
#source venv/bin/activate
conda create -n "webScrappingWCP" python=3.9
conda activate webScrappingWCP

conda install -c conda-forge jupyterlab
conda install -c conda-forge notebook

pip install -r requirements.txt
```

2. Lancer les scripts (dans l'ordre):

```bash
python3 scrapping_textiles.py # Ceci ouvre un navigateur web (ne pas fermer), 
# attendre la fin du scrapping (environ 20-30 minutes) puis fermer le navigateur
# Pour voir le résultat de ce script, ouvrir le fichier textiles.json
python3 clean_textiles.py # Télécharge les images dans images/ et proposition de nettoyage des données dans 
# une dataframe (textiles.csv)
```