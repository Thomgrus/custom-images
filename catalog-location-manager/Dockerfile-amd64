FROM python:3-slim

WORKDIR /app

# Mettre à jour la liste des paquets et installer git
RUN apt-get update && \
    apt-get install -y git && \
    # Nettoyage du cache pour réduire la taille de l'image
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py /usr/local/bin/catalog-location-manager
RUN chmod +x /usr/local/bin/catalog-location-manager

# Définir l'ENTRYPOINT avec une commande shell
ENTRYPOINT ["/bin/bash"]