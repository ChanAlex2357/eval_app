# Eval_App TODO List

## Import de donnee

- [ ] rajouter tables dans reinitialisation des donnees
  - [ ] employee
  - [ ] salary slip
  - [ ] salary structure
  - [ ] salary strucutre assignement
  - [ ] company sauf si company = "Itu Eval"
- [ ] doctype conforme au fichier 1
  - [ ] fonction import data
  - [ ] traitement des donnees
    - [ ] recuperation company
      - [ ] cree si inexistant
      - [ ] Assigner holiday list par defaut "HL"
    - [ ] verification du nom et prenom non vide
    - [ ] genre existant ()
    - [ ] Date d'embauche - format de date
    - [ ] date de naissance - format de date
    - [ ] cree instance d'un employee et inserer
  - [ ] tester import sur erpnext
  - [ ] api upload fichier et activation de l'import a distance
- [ ] doctype conforme au fichier 2
  - [ ] fonction import data
  - [ ] traitement des donnees
    - [ ] salary - verifier si structure existante sinon cree
    - [ ] company - verifier si companie existante
    - [ ] type - verifier si type valide
    - [ ] valeur - verifier si formule coherente
    - [ ] verifier si name non vide
    - [ ] verifier si abbr non vide
    - [ ] cree instance d'un component asigner a une structure et inserer
  - [ ] validation de toutes les structures
  - [ ] tester import sur erpnext
  - [ ] api upload fichier et activation de l'import a distance

- [ ] doctype conforme au fichier 3
  - [ ] fonction import data
  - [ ] traitement des donnees
    - [ ] mois
      - [ ] format de date
      - [ ] debut du mois
    - [ ] recuperer employee selon ref
    - [ ] validation numerique du salaire
    - [ ] recuperer Salaire Structure
      - [ ] verifier si structure existante
      - [ ] verifier si component Salaire Base existant
    - [ ] cree un salary slip avec component Salaire Base amount = salaire
    - [ ] validation du salary slip
  - [ ] tester import sur erpnext
  - [ ] api upload fichier et activation de l'import a distance

- [ ] grouper les 3 doctype dans un seul import
  - [ ] doctype pour import de 3 fichiers
  - [ ] fonction import stack data
  - [ ] api upload fichier et activation de l'import a distance
- [ ] ajouter un bouton pour reinitialiser les donnees
