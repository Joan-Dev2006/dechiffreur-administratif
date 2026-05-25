# ⚖️ Le Déchiffreur Administratif

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badge-gradient-gradient.svg)](https://streamlit.io)
[![Model](https://img.shields.io/badge/LLM-Llama%203.3%2070B%20(Groq)-orange)](https://groq.com)

Une application Web intuitive et grand public conçue pour traduire le jargon administratif complexe (lettres de relance, amendes, notifications de droits) en une feuille de route claire, actionnable et chronologique.

L'application adopte une **architecture hybride** : elle extrait le texte des images/photos localement pour garantir la gratuité et la flexibilité, puis s'appuie sur la puissance de l'API Groq pour l'analyse sémantique.

---

## ✨ Fonctionnalités clés

* **📸 Scanner Photo Grand Public :** Capture de documents en direct via smartphone ou webcam grâce à un moteur OCR local (`EasyOCR`).
* **📁 Multi-formats :** Prise en charge des fichiers PDF, Word (`.docx`), fichiers texte brut et images (`PNG`, `JPG`).
* **🧠 Analyse Haute Précision :** Découpage des résultats en 3 piliers (Sens global, Actions obligatoires, Délais & Échéances) via le modèle `llama-3.3-70b-versatile`.
* **🛡️ Sécurisé & Conforme RGPD :** Anonymisation automatique locale des données sensibles (numéros de téléphone, adresses e-mail) par Regex *avant* l'envoi au LLM.
* **🌍 Internationalisation native :** Détection automatique de la langue du document et réponse dans la même langue.

---

## 🛠️ Pile Technique (Stack)

| Technologie | Rôle |
| :--- | :--- |
| **Streamlit** | Interface utilisateur (UI) responsive et interactive |
| **EasyOCR / OpenCV** | Reconnaissance optique de caractères (OCR) locale |
| **Groq SDK** | Inférence ultra-rapide du modèle Llama 3.3 70B |
| **Pdfplumber / Python-docx** | Extraction textuelle des fichiers numériques |

---
## Installer les dépendances
Utilisez le gestionnaire de paquets pour installer les bibliothèques requises :

Bash
python -m pip install streamlit groq easyocr opencv-python-headless pillow numpy pdfplumber python-docx
(Note : Lors du premier lancement d'un scan photo, EasyOCR téléchargera automatiquement les modèles de langues fr/en/es, ce qui peut prendre quelques minutes).

---

## Configuration de la clé API
Créez un dossier .streamlit à la racine du projet, puis un fichier secrets.toml à l'intérieur :

Bash
mkdir .streamlit
touch .streamlit/secrets.toml
Ajoutez-y votre clé Groq de la manière suivante :

Ini, TOML
💻 Utilisation
Pour lancer l'application en local, exécutez la commande suivante à la racine du projet :

Bash
python -m streamlit run app.py
Ouvrez ensuite votre navigateur à l'adresse locale indiquée (généralement http://localhost:8501).

---

## 🔒 Sécurité et Confidentialité
Ce projet prend la vie privée au sérieux. Aucun document original n'est envoyé sur le cloud. Le script Python nettoie le texte de ses marqueurs d'identité (téléphones, e-mails) en mémoire locale. Seul le texte anonymisé et purifié est transmis aux serveurs de Groq pour l'analyse.


---

### 💡 Un petit conseil pour la suite
Une fois que tu auras poussé ce fichier sur ton dépôt GitHub avec un `git push`, l'interface de GitHub va automatiquement le mettre en page proprement sur la page d'accueil de ton projet.

Est-ce que tu as déjà créé ton dépôt de code sur GitHub pour y déposer ton projet, ou est-ce que tu veux qu'on regarde ensemble comment lier ton dossier local à GitHub en ligne ?
## 🚀 Installation et Configuration

### 1. Prérequis
Assurez-vous d'avoir **Python 3.11+** installé ainsi qu'une clé API valide auprès de [Groq Console](https://console.groq.com/).

### 2. Cloner le projet
```bash
git clone [https://github.com/VOTRE_NOM_UTILISATEUR/VOTRE_DEPOT.git](https://github.com/VOTRE_NOM_UTILISATEUR/VOTRE_DEPOT.git)
cd VOTRE_DEPOT
