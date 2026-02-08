# SmartGestion

Application de gestion de stock et de point de vente (POS) développée avec KivyMD.

## Fonctionnalités

- **Tableau de Bord** : Vue d'ensemble des ventes et du stock.
- **Gestion des Utilisateurs** : Administration des comptes et rôles.
- **Inventaire** : Gestion des produits, ajout, modification et suppression.
- **Point de Vente (POS)** : Interface de vente rapide avec calcul automatique.
- **Historique des Ventes** : Consultation des transactions passées.
- **Profil** : Gestion du profil utilisateur.

## Installation

1. Assurez-vous d'avoir Python installé.
2. Créez un environnement virtuel :
   ```bash
   python -m venv venv
   ```
3. Activez l'environnement virtuel :
   - Windows : `venv\Scripts\activate`
   - Linux/Mac : `source venv/bin/activate`
4. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

Pour lancer l'application :

```bash
python main.py
```

## Structure du Projet

- `main.py` : Point d'entrée de l'application.
- `ui/` : Interfaces utilisateur (fichiers KV et classes écrans).
- `data/` : Gestion de la base de données et modèles.
- `assets/` : Ressources graphiques.
