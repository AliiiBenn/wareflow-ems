"""UI constants for CustomTkinter application."""

# Application Metadata
APP_NAME = "Wareflow EMS"
APP_TITLE = "Gestion des Salariés"
APP_VERSION = "1.0.0"

# Window Configuration
DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 800
MIN_WIDTH = 800
MIN_HEIGHT = 600

# Theme Configuration
DEFAULT_THEME = "blue"  # blue, green, dark-blue
DEFAULT_MODE = "System"  # System, Dark, Light

# Colors (for custom coloring)
COLOR_CRITICAL = "#DC3545"  # Red
COLOR_WARNING = "#FFC107"   # Yellow
COLOR_SUCCESS = "#28A745"   # Green
COLOR_INFO = "#17A2B8"     # Blue
COLOR_INACTIVE = "#6C757D"  # Gray

# Status Text (French)
STATUS_ACTIVE = "Actif"
STATUS_INACTIVE = "Inactif"
STATUS_VALID = "Valide"
STATUS_EXPIRED = "Expiré"
STATUS_CRITICAL = "Critique"
STATUS_WARNING = "Avertissement"

# Contract Types (French)
CONTRACT_TYPES = {
    "CDI": "CDI",
    "CDD": "CDD",
    "Interim": "Intérim",
    "Alternance": "Alternance",
}

CONTRACT_TYPE_CHOICES = ["CDI", "CDD", "Interim", "Alternance"]

# CACES Types (French)
CACES_TYPES = [
    "R489-1A",
    "R489-1B",
    "R489-3",
    "R489-4",
    "R489-5",
]

# Medical Visit Types (French)
VISIT_TYPES = {
    "initial": "Visite d'embauche",
    "periodic": "Visite périodique",
    "recovery": "Visite de reprise",
}

VISIT_TYPE_CHOICES = ["initial", "periodic", "recovery"]

# Medical Visit Results (French)
VISIT_RESULTS = {
    "fit": "Apte",
    "unfit": "Inapte",
    "fit_with_restrictions": "Apte avec restrictions",
}

VISIT_RESULT_CHOICES = ["fit", "unfit", "fit_with_restrictions"]

# Date Format (French)
DATE_FORMAT = "%d/%m/%Y"
DATE_PLACEHOLDER = "JJ/MM/AAAA"

# Navigation
NAV_EMPLOYEES = "Employés"
NAV_ALERTS = "Alertes"
NAV_IMPORT = "Import Excel"

# Button Labels
BTN_ADD = "Ajouter"
BTN_EDIT = "Modifier"
BTN_DELETE = "Supprimer"
BTN_SAVE = "Sauvegarder"
BTN_CANCEL = "Annuler"
BTN_REFRESH = "Rafraîchir"
BTN_BACK = "Retour"
BTN_VIEW = "Detail"

# Form Labels
FORM_FIRST_NAME = "Prénom"
FORM_LAST_NAME = "Nom"
FORM_EMAIL = "Email"
FORM_PHONE = "Téléphone"
FORM_STATUS = "Statut"
FORM_WORKSPACE = "Espace de travail"
FORM_ROLE = "Rôle"
FORM_CONTRACT = "Type de contrat"
FORM_ENTRY_DATE = "Date d'entrée"

# Form Placeholders
PLACEHOLDER_SEARCH = "Rechercher par nom..."

# Filter Options
FILTER_ALL = "Tous"
FILTER_ACTIVE = "Actifs"
FILTER_INACTIVE = "Inactifs"

# Messages
MSG_CONFIRM_DELETE = "Êtes-vous sûr de vouloir supprimer cet employé ?"
MSG_SAVE_SUCCESS = "Employé sauvegardé avec succès !"
MSG_DELETE_SUCCESS = "Employé supprimé avec succès !"
MSG_ERROR_REQUIRED = "Ce champ est requis"
MSG_ERROR_INVALID = "Valeur invalide"

# Table Headers
TABLE_NAME = "Nom"
TABLE_EMAIL = "Email"
TABLE_PHONE = "Téléphone"
TABLE_STATUS = "Statut"
TABLE_ACTIONS = "Actions"
TABLE_WORKSPACE = "Espace"
TABLE_ROLE = "Rôle"
TABLE_CONTRACT = "Contrat"

# Alert Types
ALERT_TYPE_ALL = "Tous"
ALERT_TYPE_CACES = "CACES"
ALERT_TYPE_MEDICAL = "Visites médicales"
ALERT_TYPE_TRAINING = "Formations"

ALERT_TYPE_CHOICES = [ALERT_TYPE_ALL, ALERT_TYPE_CACES, ALERT_TYPE_MEDICAL, ALERT_TYPE_TRAINING]

# Alert Day Filters
ALERT_DAYS_30 = "30 jours"
ALERT_DAYS_60 = "60 jours"
ALERT_DAYS_90 = "90 jours"
ALERT_DAYS_ALL = "Toutes"

ALERT_DAYS_CHOICES = [ALERT_DAYS_30, ALERT_DAYS_60, ALERT_DAYS_90, ALERT_DAYS_ALL]
ALERT_DAYS_VALUES = {"30 jours": 30, "60 jours": 60, "90 jours": 90, "Toutes": 999}

# Status Badges
STATUS_BADGE_VALID = "Valide"
STATUS_BADGE_WARNING = "Avertissement"
STATUS_BADGE_CRITICAL = "Critique"
STATUS_BADGE_EXPIRED = "Expiré"

# CACES Form Labels
FORM_CACES_TYPE = "Type de CACES"
FORM_CACES_COMPLETION_DATE = "Date d'obtention"
FORM_CACES_EXPIRATION_DATE = "Date d'expiration"
FORM_CACES_DOCUMENT = "Certificat (PDF)"

# Medical Visit Form Labels
FORM_MEDICAL_TYPE = "Type de visite"
FORM_MEDICAL_DATE = "Date de visite"
FORM_MEDICAL_RESULT = "Résultat"
FORM_MEDICAL_EXPIRATION_DATE = "Date de fin de validité"
FORM_MEDICAL_DOCUMENT = "Certificat (PDF)"

# Import Labels
IMPORT_TITLE = "Import Excel"
IMPORT_DESCRIPTION = "Importez un fichier Excel contenant la liste des employés."
IMPORT_BUTTON_CHOOSE = "Choisir un fichier Excel..."
IMPORT_BUTTON_TEMPLATE = "Télécharger le modèle"
IMPORT_BUTTON_IMPORT = "Importer"
IMPORT_PROGRESS = "Progression"
IMPORT_COMPLETE = "Import terminé"

# Import Errors
IMPORT_ERROR_NO_FILE = "Aucun fichier sélectionné"
IMPORT_ERROR_INVALID_FORMAT = "Format de fichier invalide (attendu: .xlsx)"
IMPORT_ERROR_MISSING_COLUMNS = "Colonnes requises manquantes"
IMPORT_ERROR_INVALID_DATA = "Données invalides"

# Validation Messages
VALIDATION_FIRST_NAME_REQUIRED = "Le prénom est requis"
VALIDATION_LAST_NAME_REQUIRED = "Le nom est requis"
VALIDATION_EMAIL_INVALID = "Format d'email invalide"
VALIDATION_PHONE_INVALID = "Format de téléphone invalide"
VALIDATION_DATE_REQUIRED = "La date est requise"
VALIDATION_DATE_INVALID = "Format de date invalide (attendu: JJ/MM/AAAA)"
VALIDATION_DATE_FUTURE = "La date ne peut pas être dans le futur"
VALIDATION_DATE_TOO_OLD = "La date semble incorrecte (avant 2000)"
VALIDATION_STATUS_REQUIRED = "Le statut est requis"
VALIDATION_WORKSPACE_REQUIRED = "L'espace de travail est requis"
VALIDATION_ROLE_REQUIRED = "Le rôle est requis"
VALIDATION_CONTRACT_REQUIRED = "Le type de contrat est requis"
VALIDATION_REQUIRED_FIELD = "Ce champ est obligatoire"

# Workspaces
WORKSPACE_ZONES = ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E"]

# Roles
ROLE_CARISTE = "Cariste"
ROLE_PREPARATEUR = "Préparateur de commandes"
ROLE_MAGASINIER = "Magasinier"
ROLE_RECEVEUR = "Réceptionnaire"
ROLE_EXPEDITEUR = "Expéditeur"

ROLE_CHOICES = [
    ROLE_CARISTE,
    ROLE_PREPARATEUR,
    ROLE_MAGASINIER,
    ROLE_RECEVEUR,
    ROLE_EXPEDITEUR,
]

# Section Titles
SECTION_INFO = "Informations"
SECTION_CACES = "CACES"
SECTION_MEDICAL = "Visites Médicales"
SECTION_TRAININGS = "Formations en Ligne"

# Empty States
EMPTY_NO_EMPLOYEES = "Aucun employé trouvé"
EMPTY_NO_CACES = "Aucun CACES enregistré"
EMPTY_NO_VISITS = "Aucune visite médicale enregistrée"
EMPTY_NO_TRAININGS = "Aucune formation en ligne enregistrée"

# Confirmation Messages
CONFIRM_DELETE_EMPLOYEE = "Voulez-vous vraiment supprimer cet employé ?"
CONFIRM_DELETE_WARNING = "Cette action est irréversible."
CONFIRM_DELETE_CACES = "Voulez-vous vraiment supprimer ce CACES ?"
CONFIRM_DELETE_VISIT = "Voulez-vous vraiment supprimer cette visite médicale ?"

# Success Messages
SUCCESS_EMPLOYEE_CREATED = "Employé créé avec succès"
SUCCESS_EMPLOYEE_UPDATED = "Employé mis à jour avec succès"
SUCCESS_EMPLOYEE_DELETED = "Employé supprimé avec succès"
SUCCESS_CACES_CREATED = "CACES ajouté avec succès"
SUCCESS_CACES_UPDATED = "CACES mis à jour avec succès"
SUCCESS_CACES_DELETED = "CACES supprimé avec succès"
SUCCESS_VISIT_CREATED = "Visite médicale ajoutée avec succès"
SUCCESS_VISIT_UPDATED = "Visite médicale mise à jour avec succès"
SUCCESS_VISIT_DELETED = "Visite médicale supprimée avec succès"

# Error Messages
ERROR_LOAD_EMPLOYEES = "Erreur lors du chargement des employés"
ERROR_LOAD_EMPLOYEE = "Erreur lors du chargement de l'employé"
ERROR_SAVE_EMPLOYEE = "Erreur lors de l'enregistrement de l'employé"
ERROR_DELETE_EMPLOYEE = "Erreur lors de la suppression de l'employé"
ERROR_SAVE_CACES = "Erreur lors de l'enregistrement du CACES"
ERROR_DELETE_CACES = "Erreur lors de la suppression du CACES"
ERROR_SAVE_VISIT = "Erreur lors de l'enregistrement de la visite"
ERROR_DELETE_VISIT = "Erreur lors de la suppression de la visite"

# Expiration Status
EXPIRATION_STATUS_VALID = "Valide"
EXPIRATION_STATUS_SOON = "Bientôt"
EXPIRATION_STATUS_URGENT = "Urgent"
EXPIRATION_STATUS_EXPIRED = "Expiré"
