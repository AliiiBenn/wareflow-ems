# [CRITICAL] Hardcoded UI Strings Block Internationalization

## Type
**Architecture / Maintainability**

## Severity
**CRITICAL** - Completely blocks translation to other languages

## Affected Components
- **ENTIRE CODEBASE** - All UI strings are hardcoded in Python

## Description
Every single UI string is hardcoded in Python code throughout the application. This creates a complete blocker for:
1. **Translation to other languages** (German, Spanish, English, etc.)
2. **Localization of date/time formats**
3. **Maintenance of consistent terminology**
4. **Dynamic language switching**

Currently, the application is mixed French/English and cannot be translated without rewriting the entire codebase.

## Examples of Hardcoded Strings

### In Forms
```python
# src/ui_ctk/forms/employee_form.py:90
title = "Modifier un Employé" if self.is_edit_mode else "Nouvel Employé"
# ↑ Hardcoded French, cannot be translated
```

### In Views
```python
# src/ui_ctk/views/employee_detail.py:443
info_label = ctk.CTkLabel(
    item,
    text=f"{INFO_EMPLOYEE} : {self.employee.external_id or 'N/A'}",
    # ↑ Hardcoded text with interpolation
)

# src/ui_ctk/views/employee_list.py:62
title_label = ctk.Label(
    header,
    text="Liste des Employés",  # Hardcoded French
    font=("Arial", 14, "bold")
)
```

### In Constants
```python
# src/ui_ctk/constants.py
BTN_ADD = "Ajouter"  # Hardcoded
BTN_EDIT = "Modifier"  # Hardcoded
BTN_DELETE = "Supprimer"  # Hardcoded
```

## Problems Created

### 1. No Translation Possible
Every string would need to be:
1. Extracted to a translation file
2. Translated by linguists
3. Loaded at runtime
4. Re-inserted into UI components

### 2. Mixed Languages
Current code has:
- French UI labels: "Ajouter", "Modifier"
- English words in French UI: "Detail"
- Mixed error messages
- Inconsistent terminology

### 3. Maintenance Nightmare
To change a label, developer must:
1. Find where it's hardcoded (could be anywhere)
2. Modify Python code
3. Test application
4. Commit changes

### 4. No Runtime Language Switching
Users cannot:
- Switch between French and English
- Add new languages without code changes
- Customize terminology per installation

## Impact Assessment

### Current State
- **Languages**: Mixed French/English (accidental)
- **Translatable**: 0% (everything hardcoded)
- **Translations**: 0 (no i18n framework)
- **Maintenance**: High (changes require code modification)

### Target State
- **Languages**: French (primary), with English translation ready
- **Translatable**: 100% (all strings externalized)
- **Translations**: Easy to add new languages
- **Maintenance**: Low (update translation files, not code)

## Technical Debt

### String Count
Based on analysis of the codebase:
- **~500+ hardcoded UI strings** across all files
- **~15 different files** with hardcoded strings
- **~8 different languages/terms mixed** inconsistently

### Affected Modules
- `src/ui_ctk/forms/` - 5 forms with ~200 strings
- `src/ui_ctk/views/` - 4 views with ~250 strings
- `src/ui_ctk/constants.py` - ~50 strings
- `src/controllers/` - ~50 strings

## Proposed Solution

### Architecture: gettext + Python i18n

```python
# src/i18n/translations.py
import gettext
import locale
from pathlib import Path

# Setup translations
LOCALE_DIR = Path(__file__).parent.parent / 'locales'

def setup_i18n(language: str = 'fr'):
    """Setup internationalization for the application."""
    try:
        # Set locale
        locale.setlocale(locale.LC_ALL, f'{language}.UTF-8')

        # Bind gettext
        gettext.bindtextdomain('wareflow_ems', LOCALE_DIR / 'locale')
        gettext.textdomain('wareflow_ems')

        # Install translation in builtins
        gettext.install('wareflow_ems')

        # Store language for runtime
        import builtins
        builtins._ = gettext.gettext

    except Exception as e:
        print(f"[WARN] Failed to setup i18n: {e}")
        # Fallback to English
        builtins._ = lambda x: x
```

### Extract Strings to POT File

```bash
# Extract all strings from Python files
pybabel extract -o locales/wareflow_ems.pot \
    -k "lazy_gettext" \
    src/

# Creates locales/wareflow_ems.pot with all strings
```

### Example: Before and After

#### Before (Current)
```python
# src/ui_ctk/views/employee_list.py
title_label = ctk.CTkLabel(
    header,
    text="Liste des Employés",  # Hardcoded
    font=("Arial", 14, "bold")
)
```

#### After (With i18n)
```python
# src/ui_ctk/views/employee_list.py
from src.i18n.translations import _

title_label = ctk.CTkLabel(
    header,
    text=_("Liste des Employés"),  # Translatable!
    font=("Arial", 14, "bold")
)
```

### Translation Files

```python
# locales/fr/LC_MESSAGES/wareflow_ems.po
msgid "Liste des Employés"
msgstr "Employee List"

msgid "Ajouter"
msgstr "Add"

msgid "Modifier"
msgstr "Edit"

msgid "Supprimer"
msgstr "Delete"
```

```python
# locales/en/LC_MESSAGES/wareflow_ems.po
msgid "Liste des Employés"
msgstr "Employee List"

msgid "Ajouter"
msgstr "Add"

msgid "Modifier"
msgstr "Edit"

msgid "Supprimer"
msgstr "Delete"
```

### Language Switcher

```python
# src/ui_ctk/main_window.py
def create_language_switcher(self):
    """Add language selector to navigation bar."""
    lang_frame = ctk.CTkFrame(self.nav_bar, fg_color="transparent")
    lang_frame.pack(side="right", padx=10)

    lang_options = ["Français", "English"]
    self.lang_var = ctk.StringVar(value=lang_options[0])

    lang_menu = ctk.CTkOptionMenu(
        lang_frame,
        values=lang_options,
        variable=self.lang_var,
        command=self.on_language_changed,
        width=100
    )
    lang_menu.pack(side="left", padx=5)

def on_language_changed(self, language):
    """Handle language change."""
    lang_code = 'fr' if language == "Français" else 'en'

    # Reload i18n
    from src.i18n.translations import setup_i18n
    setup_i18n(lang_code)

    # Refresh current view
    if hasattr(self, 'current_view') and self.current_view:
        self.current_view.refresh()
```

## Implementation Plan

### Phase 1: Setup i18n Framework (4-6 hours)
1. Install dependencies (`babel`, `gettext`)
2. Create `src/i18n/translations.py`
3. Extract strings to POT file
4. Create initial French translation file
5. Create English translation file
6. Add language switcher to main window
7. Write tests

### Phase 2: Replace Hardcoded Strings (8-12 hours)
1. Update forms (~200 strings)
   - `employee_form.py`
   - `caces_form.py`
   - `medical_form.py`
   - Other forms

2. Update views (~250 strings)
   - `employee_list.py`
   - `employee_detail.py`
   - `alerts_view.py`
   - `import_view.py`

3. Update constants (~50 strings)
   - `constants.py`

4. Update controllers (~50 strings)

### Phase 3: Add More Languages (Ongoing)
1. German translation (German users)
2. Spanish translation
3. Italian translation
4. Dutch translation (warehouse context)

## Files to Create
- `src/i18n/__init__.py`
- `src/i18n/translations.py`
- `locales/wareflow_ems.pot` (template)
- `locales/fr/LC_MESSAGES/wareflow_ems.po`
- `locales/en/LC_MESSAGES/wareflow_ems.po`
- `pyproject.toml` (add babel config)

## Files to Modify
- **ALL files with hardcoded strings** (~50 files)
- Major ones:
  - `src/ui_ctk/forms/*.py` (5 files)
  - `src/ui_ctk/views/*.py` (4 files)
  - `src/ui_ctk/constants.py`
  - `src/controllers/*.py`

## Dependencies to Add
```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "babel>=2.13.0",  # i18n framework
]

[tool.babel.compile]
directory = "locales"
domains = ["wareflow_ems"]
```

## Code Example: Migration Steps

### Step 1: Import i18n
```python
# At top of file
from src.i18n.translations import _
```

### Step 2: Replace hardcoded strings
```python
# Before
text="Liste des Employés"

# After
text=_("Liste des Employés")
```

### Step 3: Extract strings
```bash
# Extract all strings to POT file
pybabel extract -o locales/wareflow_ems.pot src/
```

### Step 4: Create translations
```bash
# Create French translation (init)
msginit --input=locales/wareflow_ems.pot \
         --output-file=locales/fr/LC_MESSAGES/wareflow_ems.po

# Create English translation
msginit --input=locales/wareflow_ems.pot \
         --output-file=en/LC_MESSAGES/wareflow_ems.po \
         --locale=en
```

### Step 5: Compile translations
```bash
# Compile French
pybabel compile -d locales/fr -D wareflow_ems

# Compile English
pybabel compile -d locales/en -D wareflow_ems
```

## Testing Requirements
- Test language switching works
- Test all UI labels are translated
- Test string interpolation (variables in strings)
- Test plural forms
- Test date/time formatting
- Test error messages in both languages
- Test hot-switching languages (no restart)

## Benefits

### For Developers
- Easy to add new languages
- Consistent terminology
- No code changes needed for translations
- Professional translation workflow

### For Users
- Native language support
- Easy language switching
- Better accessibility
- Consistent terminology

### For Business
- Easier international expansion
- Professional appearance
- Compliance with language laws
- Reduced maintenance cost

## Related Issues
- #009: Mixed languages in UI (symptom of this issue)
- #007: No language switcher (part of solution)

## References
- Python gettext: https://docs.python.org/3/library/gettext.html
- Babel Documentation: https://babel.pocoo.org/
- GNU gettext: https://www.gnu.org/software/gettext/
- Python i18n Cookbook: https://python-i18n.readthedocs.io/

## Priority
**CRITICAL** - Blocks international expansion

## Estimated Effort
12-20 hours (extract all strings + translate + test)

## Mitigation
While waiting for full i18n implementation:
- Document all UI strings in spreadsheet
- Keep terminology consistent
- Choose one language (French or English) and stick to it
- Add TODO comments for translatable strings
- Consider using a translation service if deployed internationally
