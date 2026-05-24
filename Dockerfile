# 1. On part d'une image Linux allégée contenant Python 3.11
FROM python:3.11-slim

# 2. On définit le dossier de travail dans le conteneur
WORKDIR /app

# 3. On copie d'abord le fichier des dépendances
COPY requirements.txt .

# 4. On installe les bibliothèques Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. On copie tout ton code (app.py) dans le conteneur
COPY . .

# 6. On expose le port standard de Streamlit
EXPOSE 8501

# 7. Commande de démarrage officielle
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]