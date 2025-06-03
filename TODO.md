# Eval_App TODO List

## Import de donnee

- [ ] rajouter tables dans reinitialisation des donnees
  - [x] employee
  - [x] salary slip
  - [x] salary structure
  - [x] salary strucutre assignement
  - [ ] company sauf si company = "Itu Eval"
- [ ] doctype conforme au fichier 1
  - [x] model
  - [x] fonction import data
  - [x] traitement des donnees
    - [x] recuperation company
      - [x] cree si inexistant
      - [x] Assigner holiday list par defaut "HL"
    - [x] verification du nom et prenom non vide
    - [x] genre existant ()
    - [x] Date d'embauche - format de date
    - [x] date de naissance - format de date
    - [x] cree instance d'un employee et inserer
  - [x] tester import sur erpnext
  - [ ] api upload fichier et activation de l'import a distance
- [ ] doctype conforme au fichier 2
  - [x] fonction import data
  - [ ] traitement des donnees
    - [x] company - verifier si companie existante
    - [x] salary - verifier si structure existante sinon cree
    - [ ] type - verifier si type valide
    - [x] valeur - verifier si formule coherente
    - [x] verifier si name non vide
    - [x] verifier si abbr non vide
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
