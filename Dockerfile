# Utilisez une image de base officielle de Python
FROM python:3.11

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt .

# Installer les dépendances nécessaires
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application dans le répertoire de travail
COPY . .

# Définir les variables d'environnement
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

# Exposer le port sur lequel l'application va tourner
EXPOSE 5000

# Commande pour démarrer l'application Flask
CMD ["flask", "run"]
