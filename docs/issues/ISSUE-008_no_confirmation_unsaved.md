# [CRITICAL] No Confirmation for Unsaved Changes

## Type
**User Experience / Data Safety**

## Severity
**CRITICAL** - High risk of accidental data loss

## Affected Components
- **Navigation** - Switching views without saving
- **Closing window** - Exiting app with unsaved changes
- **Form editing** - Leaving form without saving

## Description
The application provides NO warnings or confirmation when users navigate away from unsaved changes. This creates multiple scenarios where users can accidentally lose work:

## Problem Scenarios

### Scenario 1: Editing Employee, Then Clicking Navigation
1. User opens employee detail
2. User clicks "Modifier" (Edit)
3. User changes employee name from "Dupont" to "Dupont-Modified"
4. User realizes wrong employee, clicks "Retour" (Back)
5. **Form closes without warning**
6. **Changes lost**

### Scenario 2: Adding CACES, Then Switching Tabs
1. User clicks "+ Ajouter" for CACES
2. Fills in form (Type: R489-1A, Date: 15/01/2024)
3. User realizes needs to check medical visits first
4. User clicks "Visites Médicales" tab
5. **Form closes without warning**
6. **All entered data lost**

### Scenario 3: Accidental Window Close
1. User is filling employee form
2. Has entered 8 out of 10 required fields
3. User accidentally closes window (Alt+F4 or click X)
4. **All progress lost, no warning**
5. **Must start over from beginning**

### Scenario 4: Import in Progress
1. User starts Excel import
2. Import is running (50% complete)
3. User accidentally clicks different view
4. **No warning, import abandoned**
5. **May have partial/corrupted data**

## Current Code Analysis

### Form Dialogs - No Unsaved Changes Detection
```python
# src/ui_ctk/forms/base_form.py:56-70
def on_save(self):
    """Handle save button click."""
    is_valid, error = self.validate()

    if not is_valid:
        self.show_error(error)
        return

    try:
        self.save()
        self.result = True
        self.destroy()  # ← Just closes, no warning if unsaved changes in other forms
```

### Navigation - No Check for Unsaved Changes
```python
# src/ui_ctk/main_window.py:120-138
def switch_view(self, view_class, *args, **kwargs):
    """
    Switch to a new view.
    """
    # Remove current view
    self.clear_view()

    # Create new view
    self.current_view = view_class(self.view_container, *args, **kwargs)
    # ↑ NO CHECK: Does the current view have unsaved changes?

    self.current_view.pack(fill="both", expand=True)
```

### Window Close - No Check for Unsaved Changes
```python
# src/ui_ctk/app.py:127-139
def on_closing():
    """Handle application closing."""
    print("\n[INFO] Shutting down application...")

    # Close database connection
    if not database.is_closed():
        database.close()
        print("[OK] Database connection closed")

    # app.destroy()
    # ↑ NO CHECK: Does any view have unsaved changes?
```

## Impact Assessment

### User Frustration
- **Lost work**: Users must re-enter data
- **Uncertainty**: Users don't know if changes were saved
- **Fear**: Users afraid to navigate freely
- **Inefficiency**: Extra caution slows down workflow

### Data Loss Risks
- **Accidental**: Click navigation by mistake
- **Confusion**: Don't know if "Sauvegarder" (Save) was clicked
- **Forgetfulness**: Don't remember if they saved before closing
- **Distractions**: Phone calls, interruptions

### Affected Operations
- Employee creation/editing (10+ fields)
- CACES addition (3 fields + document)
- Medical visit addition (4 fields + document)
- Training addition (multiple fields)
- Excel import (critical - lots of data)

## Proposed Solution

### Part 1: Track Form State

```python
# src/ui_ctk/forms/base_form.py
class BaseFormDialog(ctk.CTkToplevel):
    """Enhanced form dialog with change tracking."""

    def __init__(self, parent, title: str, width: int = 500, height: int = 600):
        super().__init__(parent)

        self.title = f"{APP_TITLE} - {title}"
        self.geometry(f"{width}x{height}")

        self.result = None

        # Track form state
        self.initial_state = {}  # State when form opened
        self.current_state = {}   # State after last change
        self.has_unsaved_changes = False

        # Create form content
        self.create_form()

        # Capture initial state
        self._capture_initial_state()

    def _capture_initial_state(self):
        """Capture initial form state."""
        # Get all StringVars
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, ctk.StringVar):
                self.initial_state[attr_name] = attr.get()

    def _check_for_changes(self) -> bool:
        """Check if form has unsaved changes."""
        self.current_state = {}

        # Get current state
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, ctk.StringVar):
                self.current_state[attr_name] = attr.get()

        return self.current_state != self.initial_state

    def _mark_changed(self):
        """Mark form as having unsaved changes."""
        self.has_unsaved_changes = True

    def _mark_saved(self):
        """Mark form as saved (update state)."""
        self.has_unsaved_changes = False
        self.initial_state = self.current_state.copy()
```

### Part 2: Enhanced Navigation with Change Detection

```python
# src/ui_ctk/main_window.py
def switch_view(self, view_class, *args, **kwargs):
    """
    Switch to a new view with unsaved changes detection.
    """
    # Check if current view has unsaved changes
    if self.current_view and hasattr(self.current_view, 'has_unsaved_changes'):
        if self.current_view.has_unsaved_changes:
            # Show confirmation dialog
            response = messagebox.askyesnocancel(
                "Changements non sauvegardés",
                "Vous avez des changements non sauvegardés dans cette vue.\n\n"
                "Voulez-vous les sauvegarder maintenant ?",
                icon='warning'
            )

            if response == 'yes':
                # Try to save
                if hasattr(self.current_view, 'save'):
                    try:
                        self.current_view.save()
                    except Exception as e:
                        if not messagebox.askyesno(
                            "Erreur de sauvegarde",
                            f"Erreur lors de la sauvegarde: {e}\n\n"
                            "Quitter sans sauvegarder ?"
                        ):
                            return  # Cancel navigation
            elif response == 'cancel':
                return  # Cancel navigation
            else:  # 'no'
                pass  # Continue without saving

    # Proceed with view switch
    # ... (existing code)
```

### Part 3: Window Close Warning

```python
# src/ui_ctk/app.py
def on_closing():
    """Handle application closing with unsaved changes check."""
    # Check for unsaved changes in all views
    has_unsaved = False

    if self.main_window.current_view:
        if hasattr(self.main_window.current_view, 'has_unsaved_changes'):
            if self.main_window.current_view.has_unsaved_changes:
                has_unsaved = True

    # Check for active imports
    if hasattr(self, '_active_import'):
        has_unsaved = True

    if has_unsaved:
        response = messagebox.askyesnocancel(
            "Quitter l'application ?",
            "Vous avez des changements non sauvegardés.\n\n"
            "Voulez-vous vraiment quitter ?",
            icon='warning'
        )

        if response == 'cancel':
            return  # Cancel the close

    # Proceed with cleanup
    print("\n[INFO] Shutting down application...")

    # Close database connection
    if not database.is_closed():
        database.close()
        print("[OK] Database connection closed")

    # Destroy window
    self.quit()  # Use quit() instead of destroy()
```

### Part 4: Unsaved Changes Indicator in Forms

```python
# src/ui_ctk/forms/base_form.py
class BaseFormDialog(ctk.CTkToplevel):
    """Form dialog with unsaved changes indicator."""

    def create_form(self):
        """Create form content."""
        # ... existing form creation ...

        # Add unsaved changes indicator
        self.unsaved_indicator = ctk.CTkLabel(
            self,
            text="● Non sauvegardé",
            text_color="gray",
            font=("Arial", 9)
        )
        # Position at top-right of form
        self.unsaved_indicator.place(relx=1.0, x=-10, y=10)
        self.unsaved_indicator.place_forget()  # Initially hidden

    def _mark_changed(self):
        """Mark form as changed and show indicator."""
        if not self.has_unsaved_changes:
            self.has_unsaved_changes = True
            self.unsaved_indicator.place()

    def _mark_saved(self):
        """Mark form as saved and hide indicator."""
        if self.has_unsaved_changes:
            self.has_unsaved_changes = False
            self.unsaved_indicator.place_forget()

    def on_save(self):
        """Handle save button click."""
        is_valid, error = self.validate()

        if not is_valid:
            self.show_error(error)
            return

        try:
            self.save()
            self.result = True
            self._mark_saved()  # Hide unsaved indicator
            self.destroy()

        except Exception as e:
            self.show_error(f"Erreur lors de la sauvegarde: {str(e)}")
```

### Part 5: Tab Change Warning for Employee Detail

```python
# src/ui_ctk/views/employee_detail.py
class EmployeeDetailView(BaseView):
    """Employee detail with tab change detection."""

    def __init__(self, master, employee: Employee, title: str = ""):
        # ... existing init ...

        # Track unsaved changes in forms
        self.active_tab_form = None
        self.tab_unsaved_changes = {}

        # Bind tab change events
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changing)

    def _on_tab_changing(self, event):
        """Handle tab change - check for unsaved forms."""
        current_tab = event.widget.index(event.widget.select())

        # Check if form in active tab has unsaved changes
        if self.active_tab_form and hasattr(self.active_tab_form, 'has_unsaved_changes'):
            if self.active_tab_form.has_unsaved_changes:
                # Show warning
                response = messagebox.askyesnocancel(
                    "Changements non sauvegardés",
                    "Vous avez des changements non sauvegardés dans cet onglet.\n\n"
                    "Voulez-vous les sauvegarder maintenant ?",
                    icon='warning'
                )

                if response == 'yes':
                    # Try to save
                    try:
                        self.active_tab_form.save()
                    except Exception as e:
                        if not messagebox.askyesno(
                            "Erreur de sauvegarde",
                            f"Erreur lors de la sauvegarde: {e}\n\n"
                            "Quitter sans sauvegarder ?"
                        ):
                            return  # Cancel tab change
                elif response == 'cancel':
                    return  # Cancel tab change
                # else: 'no' - Continue without saving
```

## Files to Create
- `src/utils/state_tracker.py`
- `tests/test_unsaved_changes.py`

## Files to Modify
- `src/ui_ctk/forms/base_form.py` - Add change tracking
- `src/ui_ctk/main_window.py` - Add navigation checks
- `src/ui_ctk/app.py` - Add close warning
- `src/ui_ctk/views/employee_detail.py` - Add tab change warnings
- All forms: Add `has_unsaved_changes` tracking

## Testing Requirements
- Test editing employee, then navigating away without saving
- Test adding CACES, then switching tab
- Test filling form, then closing window
- Test unsaved indicator appears/disappears correctly
- Test "Yes" saves changes
- Test "No" continues without saving
- Test "Cancel" aborts operation
- Test keyboard shortcuts (Alt+F4, Ctrl+W, Ctrl+Tab)
- Test window close with unsaved changes
- Test concurrent operations (import while editing)

## Related Issues
- #007: No undo/redo (partially solves this issue)
- #018: No audit trail (no tracking of changes)

## Priority
**CRITICAL** - High risk of accidental data loss

## Estimated Effort
4-5 hours (implementation + tests)

## Mitigation
While waiting for fix:
1. Add manual save reminder in documentation
2. Educate users about importance of save button
3. Add frequent auto-save prompts
4. Train users on proper workflow
