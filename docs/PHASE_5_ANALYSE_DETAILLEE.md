# Phase 5: Analyse Approfondie du Module de Validation

## 1. Contexte et Analyse de l'État Actuel

### 1.1 État Actuel de la Validation dans le Projet

**Validations déjà implémentées :**

1. **Niveau Base de Données (SQLite/Peewee)** :
   - ✅ \`external_id\` : \`CharField(unique=True)\` → Contrainte d'unicité SQLite
   - ✅ \`first_name\`, \`last_name\` : \`CharField()\` → NOT NULL par défaut
   - ✅ Types de champs : DateField, CharField, UUIDField → Validation des types

2. **Niveau Modèle (Hooks Peewee)** :
   \`\`\python
   # Employee.before_save() - src/employee/models.py:131-134
   def before_save(self):
       if self.entry_date > date.today():
           raise ValueError("Entry date cannot be in the future")
   \`\`\`
   - ✅ Validation date d'entrée non future

3. **Niveau CLI (Validation manuelle)** :
   - ✅ Validation format date ISO (YYYY-MM-DD)
   - ✅ Validation valeurs enum pour visits : \`['fit', 'unfit', 'fit_with_restrictions']\`
   - ✅ Validation types de visite : \`['initial', 'periodic', 'recovery']\`
   - ✅ Vérification unicité \`external_id\` manuelle avant création
   - ✅ Validation champs requis en mode interactif

**Problème identifié : Triple validation redondante**

Actuellement, la logique de validation est dispersée :
1. **CLI** : Vérifie les valeurs avant d'appeler le modèle
2. **Modèle** : Valide dans \`before_save()\`
3. **Base de données** : Contraintes SQL (UNIQUE, NOT NULL)

**Risque** : Incohérence si les règles changent
- Exemple : La règle "date d'entrée non future" existe dans le modèle mais PAS dans le CLI
- Si on ajoute un employé via le CLI avec une date future, l'erreur n'apparaîtra qu'au moment du `.save()`
- Les messages d'erreur seront différents selon le point d'entrée

### 1.2 Audit des Validations Manquantes

**Analyse des champs non validés :**

| Modèle | Champ | Validation Actuelle | Validation Manquante |
|--------|-------|---------------------|----------------------|
| Employee | `external_id` | Unique (DB) | Format (path traversal, caractères spéciaux) |
| Employee | `entry_date` | Pas future (modèle) | Date minimum raisonnable (>= 1900) |
| Caces | `kind` | Aucune | Vérifier dans CACES_TYPES |
| MedicalVisit | `visit_type` + `result` | Enum CLI | Cohérence (recovery → fit_with_restrictions) |
| Tous | `document_path`, `avatar_path` | Aucune | Path traversal protection |

**Risques identifiés :**

1. **Sécurité** : Path traversal possible via `document_path` et `avatar_path`
2. **Intégrité** : CACES avec type invalide possible si on contourne le CLI
3. **Cohérence** : Visite médicales avec combinaisons invalides possibles


## 2. Exigences Métier pour la Validation

### 2.1 Pourquoi un Module de Validation Structuré ?

**Problèmes actuels sans validation centralisée :**

1. **Incohérence des messages d'erreur**
   - CLI : "❌ Un employé avec l'ID XXX existe déjà"
   - Modèle : `IntegrityError` de SQLite (peu clair pour l'utilisateur)
   - Base de données : `UNIQUE constraint failed: employees.external_id`

2. **Duplication de la logique de validation**
   - L'unicité de `external_id` est vérifiée manuellement dans le CLI
   - La base de données vérifie aussi l'unicité
   - Pas de garantie que les deux règles restent synchronisées

3. **Absence de validation de format**
   - `external_id` : Aucune vérification de format (ex: "R489 1A" avec espace invalide)
   - `kind` dans Caces : Pas de vérification contre la liste des types valides
   - `visit_type`/`result` : Pas de validation de cohérence

4. **Risques de sécurité**
   - **Path Traversal** : `document_path` et `avatar_path` non validés
   - **Injection SQL** : Bien que Peewee protège contre la plupart des injections
   - **Date non valide** : Pas de protection contre les dates impossibles

### 2.2 Objectifs du Module de Validation

1. **Intégrité des données** : Garantir que toutes les données respectent les règles métier
2. **Sécurité** : Prévenir les attaques par path traversal
3. **Expérience Utilisateur** : Messages d'erreur clairs et exploitables
4. **Maintenabilité** : Logique de validation centralisée et réutilisable


## 3. Architecture Proposée

### 3.1 Architecture en 3 Couches

```
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE APPLICATION                        │
│  (CLI, API, Tests)                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ Utilise
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   COUCHE VALIDATION                         │
│  (src/employee/validators.py)                               │
└──────────────────────┬──────────────────────────────────────┘
                       │ Appelé par
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      COUCHE MODÈLE                          │
│  (src/employee/models.py - Hooks before_save)               │
└──────────────────────┬──────────────────────────────────────┘
                       │ Garanti par
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   COUCHE BASE DE DONNÉES                    │
│  (SQLite avec Peewee ORM)                                   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Flux de Validation

**Scénario : Création d'employé via CLI**

```python
# 1. CLI valide les entrées
external_id = validate_external_id(cli_input)
entry_date = validate_entry_date(cli_input_date)

# 2. Création du modèle
employee = Employee(external_id=external_id, entry_date=entry_date, ...)

# 3. Le hook before_save() valide également (garantie)
employee.save()  # Appelle before_save() automatiquement
```


## 4. Spécifications Détaillées des Validators

### 4.1 Structure de l'Exception ValidationError

```python
class ValidationError(Exception):
    """
    Exception structurée pour les erreurs de validation.

    Attributs:
        field: Nom du champ en erreur
        value: Valeur invalide
        message: Message d'erreur principal
        details: Dict avec informations supplémentaires (optionnel)
    """
    def __init__(self, field: str, value: Any, message: str, details: dict = None):
        self.field = field
        self.value = value
        self.message = message
        self.details = details or {}
```

### 4.2 Validators Fonctionnels

| Fonction | Règles | Tests Requis |
|----------|--------|--------------|
| `validate_external_id()` | 3-50 chars, A-Za-z0-9_-, pas de path traversal | 6 tests |
| `validate_entry_date()` | Pas future, >= 1900-01-01 | 3 tests |
| `validate_caces_kind()` | Dans CACES_TYPES | 2 tests |
| `validate_medical_visit_consistency()` | recovery → fit_with_restrictions | 4 tests |
| `validate_path_safe()` | Pas de ../, extensions autorisées | 4 tests |

### 4.3 Validators de Classes

| Classe | Utilité | Tests Requis |
|--------|---------|--------------|
| `UniqueValidator` | Vérifie unicité dans table | 3 tests |
| `DateRangeValidator` | Valide plage de dates | 3 tests |


## 5. Stratégie de Tests

### 5.1 Tests Unitaires

**Fichier** : `tests/test_employee/test_validators.py`

- 6 fonctions de validation
- 2 classes de validators
- Total : ~25 tests unitaires

### 5.2 Tests d'Intégration

**Fichier** : `tests/test_integration/test_validators_integration.py`

- TestEmployeeCreationWithValidation
- TestCacesCreationWithValidation
- TestMedicalVisitConsistencyValidation
- Total : ~6 tests d'intégration

### 5.3 Tests CLI

**Mise à jour de** : `tests/test_cli/test_commands.py`

- test_add_employee_invalid_id
- test_add_caces_invalid_kind
- test_add_visit_recovery_without_restrictions
- Total : ~3 tests CLI supplémentaires


## 6. Analyse de Risques et Questions Ouvertes

### 6.1 Risques Techniques

1. **Performance** : Validators simples (< 1ms) → Impact négligeable
2. **Breaking changes** : Données existantes → Validators permissifs au départ
3. **Erreur confusion** : Capturer IntegrityError → Convertir en ValidationError

### 6.2 Questions Ouvertes

1. **Validation stricte ou permissive ?**
   - Recommandation : Stricte pour nouveaux validators, permissive pour existants

2. **Conversion IntegrityError ?**
   - Recommandation : Oui, pour messages cohérents

3. **Validation données existantes ?**
   - Recommandation : Script de validation + validation lors des updates


## 7. Plan d'Implémentation

### 7.1 Étapes de Développement (5-6 jours)

**Jour 1** : Structure de base et ValidationError
**Jour 2** : Validators simples (validate_external_id, validate_entry_date, etc.)
**Jour 3** : Validators de cohérence (validate_medical_visit_consistency)
**Jour 4** : Classes de validators (UniqueValidator, DateRangeValidator)
**Jour 5** : Intégration dans les modèles (before_save hooks)
**Jour 6** : Intégration CLI et tests finaux

### 7.2 Critères de Succès

1. Tous les tests passent (299 existants + ~50 nouveaux)
2. Couverture de code > 90% pour validators.py
3. Aucune régression
4. Messages d'erreur clairs
5. Performance < 10ms par création


## 8. Documentation

### 8.1 Docstring Convention

Chaque validator doit inclure :
- Description de la règle métier
- Args et Returns
- Raises (ValidationError avec contexte)
- Examples d'utilisation

### 8.2 Documentation Utilisateur

**Fichier** : `docs/VALIDATORS.md`

- Vue d'ensemble du module
- Liste des validators disponibles
- Exemples d'utilisation
- Guide de maintenance

---

**Document rédigé le** : 2026-01-16
**Version** : 1.0
**Prochaine étape** : Implémentation de la Phase 5 (Validators)