import streamlit as st
import pdfplumber
from docx import Document
from groq import Groq  # Importation du moteur Cloud ultra-rapide

# Configuration de la page en mode Large pour un rendu professionnel
st.set_page_config(page_title="Déchiffreur Administratif Global", page_icon="📝", layout="wide")

st.title("📝 Le Déchiffreur Administratif - Version Cloud")
st.write("Analyse à l'échelle industrielle de vos documents réglementaires et juridiques.")
st.markdown("---")

# Barre latérale sécurisée pour la configuration de la clé API
st.sidebar.header("🔑 Configuration Cloud")
api_key = st.sidebar.text_input("Entrez votre clé API Groq (gsk_...)", type="password")
st.sidebar.markdown("""
---
*Note technique : En production, cette clé est stockée dans les variables d'environnement du serveur (AWS/Scaleway) pour que les utilisateurs finaux n'aient rien à configurer.*
""")

st.subheader("1. Importez votre document")
fichier_implique = st.file_uploader("Choisissez un fichier (Format PDF, DOCX ou TXT)", type=["pdf", "docx", "txt"])

def extraire_texte(fichier):
    extension = fichier.name.split(".")[-1].lower()
    texte = ""
    if extension == "pdf":
        with pdfplumber.open(fichier) as pdf:
            for page in pdf.pages:
                texte += page.extract_text() + "\n"
    elif extension == "docx":
        doc = Document(fichier)
        for para in doc.paragraphs:
            texte += para.text + "\n"
    elif extension == "txt":
        texte = fichier.read().decode("utf-8")
    return texte

st.markdown("---")

if fichier_implique is not None:
    with st.spinner("Extraction du texte intégral..."):
        texte_complet = extraire_texte(fichier_implique)
    
    if not texte_complet.strip():
        st.error("Impossible de lire le texte du document.")
    else:
        st.success(f"✓ Document '{fichier_implique.name}' chargé avec succès ({len(texte_complet)} caractères).")
        
        with st.expander("🔍 Inspecter le texte extrait envoyé à l'IA Cloud"):
            st.text(texte_complet)

        if st.button("⚡ Déchiffrer à l'échelle industrielle", type="primary"):
            if not api_key:
                st.error("⚠️ Action requise : Veuillez coller votre clé API Groq dans la barre latérale gauche.")
            else:
                st.subheader("📌 Feuille de Route Simplifiée (Générée par IA 70B)")
                
                # Initialisation du client Cloud Groq
                client = Groq(api_key=api_key)
                
                # Déploiement des 3 colonnes Streamlit
                col1, col2, col3 = st.columns(3)
                
                # --- APPEL 1 : EXPLICATION DU SENS ---
                with col1:
                    st.write("🤔 **Ce que ça veut dire :**")
                    zone_1 = st.empty()
                    with st.spinner("Analyse sémantique..."):
                        prompt_1 = f"Tu es un conseiller juridique expert. Analyse ce document et explique en français très simple, vulgarisé et en deux phrases maximum quel est le but de ce document pour l'utilisateur. Sois rigoureux. Document :\n\n{texte_complet}"
                        flux_1 = client.chat.completions.create(
                            model="llama-3.3-70b-versatile", # Le nouveau modèle mis à jour !
                            messages=[{"role": "user", "content": prompt_1}],
                            stream=True
                        )
                        txt1 = ""
                        for morceau in flux_1:
                            if morceau.choices[0].delta.content:
                                txt1 += morceau.choices[0].delta.content
                                zone_1.info(txt1)

                # --- APPEL 2 : LES ACTIONS OBLIGATOIRES ---
                with col2:
                    st.write("🛠️ **Ce que vous devez faire :**")
                    zone_2 = st.empty()
                    with st.spinner("Extraction des obligations..."):
                        prompt_2 = f"Tu es un conseiller juridique expert. Extrais de ce document TOUTES les actions concrètes et obligatoires que l'utilisateur doit accomplir. Liste-les sous forme de puces tirets (-) en français simple. Inclus impérativement les montants précis (ex: 1700€) s'ils existent. Document :\n\n{texte_complet}"
                        flux_2 = client.chat.completions.create(
                            model="llama-3.3-70b-versatile", # Le nouveau modèle mis à jour !
                            messages=[{"role": "user", "content": prompt_2}],
                            stream=True
                        )
                        txt2 = ""
                        for morceau in flux_2:
                            if morceau.choices[0].delta.content:
                                txt2 += morceau.choices[0].delta.content
                                zone_2.warning(txt2)

                # --- APPEL 3 : LES DÉLAIS ET DATES ---
                with col3:
                    st.write("📅 **Date limite :**")
                    zone_3 = st.empty()
                    with st.spinner("Recherche des échéances..."):
                        prompt_3 = f"Tu es un conseiller juridique expert. Analyse ce document et cherche s'il y a des dates limites, des délais maximums ou des durées (ex: 60 jours, 14 jours, 6 mois). Extrais-les de façon très précise et synthétique sous forme de puces en français. Si aucun délai n'existe, écris 'Non spécifiée'. Document :\n\n{texte_complet}"
                        flux_3 = client.chat.completions.create(
                            model="llama-3.3-70b-versatile", # Le nouveau modèle mis à jour !
                            messages=[{"role": "user", "content": prompt_3}],
                            stream=True
                        )
                        txt3 = ""
                        for morceau in flux_3:
                            if morceau.choices[0].delta.content:
                                txt3 += morceau.choices[0].delta.content
                                zone_3.error(txt3)
else:
    st.info("💡 En attente d'un document pour lancer l'analyse cloud.")