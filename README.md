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

## 🚀 Installation et Configuration

### 1. Prérequis
Assurez-vous d'avoir **Python 3.11+** installé ainsi qu'une clé API valide auprès de [Groq Console](https://console.groq.com/).

### 2. Cloner le projet
```bash
git clone [https://github.com/VOTRE_NOM_UTILISATEUR/VOTRE_DEPOT.git](https://github.com/VOTRE_NOM_UTILISATEUR/VOTRE_DEPOT.git)
cd VOTRE_DEPOT
