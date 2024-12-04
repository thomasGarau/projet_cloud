# Projet de plateforme de stockage cloud

## Description
Ce projet a été réalisé dans le cadre d'un projet scolaire. L'objectif initial était d'implémenter l'algorithme de compression de Huffman.
Nous avons décidé de créer une plateforme de stockage avec un client et un serveur pour démontrer l'utilité d'un tel algorithme.
En effet, cet algorithme permet de réduire à la fois la bande passante et l'espace de stockage, ce qui est idéal pour une application de stockage en ligne.

Contrairement à une application classique de gestion de fichiers basée sur une base de données, ce projet utilise un simple fichier texte géré par l'ORM (SQLAlchemy) à l'aide de migrations. Cela permet de simuler une base de données tout en gardant le projet léger et facile à déployer.

## Technologies
- **Client** : React.js
- **Serveur** : Python Flask
- **Fichier de stockage** : Fichier texte (géré par ORM avec migrations)
- **Azure Storage** : compte nécessaire 

## Prérequis
**Avant de commencer, assurez-vous d'avoir installé** :
- [Node.js](https://nodejs.org) (pour le client React)
- [Python 3.x](https://www.python.org/downloads/) (pour le serveur Flask) :

## Installation
### **Client**
- Installer les dépendances : ```npm install```
- Lancer le client : ```npm start```
### **Serveur** 
- Créer un environnement virtuel (optionnel, mais recommandé) :
- python -m venv venv (à la racine du projet)
- Activer l'environnement virtuel : 
  - Sur Windows : ```venv\Scripts\activate```
  - Sur Linux/Mac : ```source venv/bin/activate```
- Installer les dépendances : ```pip install -r requirements.txt```
  Lancer le serveur : ```flask run```
- Instancier un fichier .env avec les attributs suivant : 
  - SECRET_KEY=
  - DATABASE_URI=
  - JWT_SECRET_KEY=

  - AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=
  - AZURE_STORAGE_CONTAINER_NAME=
  - AZURE_ACCOUNT_NAME=
  - AZURE_QUEUE_NAME=
  - AZURE_ACCOUNT_KEY=
### **Worker** 
  - dépendance partager avec le serveur
  - ajouté un .env contenant les attributs suivant : 
  - AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=
  - AZURE_STORAGE_CONTAINER_NAME=
  -  AZURE_QUEUE_NAME=
  -  Lancer le script : ```python main.py```
### **Stress_test** 
  - dépendance partager avec le reste du projet
  - Lancer le script : ``` python stress_test.py ```
  
## Utilisation
Le client tourne en localhost à l'adresse ```http://localhost:3000/```

Une fois le client et le serveur lancés, la plateforme vous permet d'uploader et de stocker des fichiers de tout types.
L'algorithme de compression de Huffman est utilisé pour compresser les fichiers avant de les enregistrer, ce qui permet de réduire l'espace utilisé sur le serveur et la bande passante lors des téléchargements.
