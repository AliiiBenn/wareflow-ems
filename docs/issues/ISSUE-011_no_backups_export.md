# [CRITICAL] No Backup or Data Export Functionality

## Type
**Data Safety / Business Continuity**

## Severity
**CRITICAL** - Complete data loss risk with no recovery mechanism

## Affected Components
- **ENTIRE APPLICATION** - No backup functionality exists

## Description
The application has NO mechanism for:
- Creating backups of employee data
- Exporting data to standard formats (Excel, CSV, JSON)
- Restoring from backups
- Scheduled automatic backups
- Data portability (GDPR requirement)

This creates critical risks:
- **Hardware failure** = complete data loss
- **File corruption** = no recovery
- **Accidental deletion** = permanent loss
- **Migration to new system** = no data export
- **GDPR compliance** = cannot provide data to employees

## Real-World Scenarios

### Scenario 1: Hard Drive Failure
```
Day 1: Application running, 500 employees in database
Day 50: Hard drive fails completely
Result: ALL DATA PERMANENTLY LOST
Recovery: Must re-enter 500 employees from paper records
Time: 40+ hours of manual data entry
Business Impact: Operations paralyzed for days
```

### Scenario 2: Database Corruption
```python
# SQLite database can become corrupted from:
# - Power failure during write
# - Disk I/O errors
# - Concurrent access issues
# - Application crashes

# When corrupted:
peewee.DatabaseError: database disk image is malformed

# Current application has NO:
# - Automatic backups
# - Corruption detection
# - Recovery mechanism
# - Last known good backup
```

### Scenario 3: Employee Requests Data (GDPR)
```
Employee: "I want a copy of all my personal data"
HR: "We cannot export your data from the application"
Employee: Files GDPR complaint
Result: Legal issues, fines, reputational damage
```

### Scenario 4: Migration to New System
```
Company: "We're switching to a new HR system next month"
IT: "How do we export our employee data?"
Answer: "We can't. Must re-enter everything manually"
Cost: 80+ hours, data entry errors, lost historical data
```

### Scenario 5: Ransomware Attack
```
Attacker: Encrypts employee_manager.db
Attacker: "Pay $10,000 or lose your data"
Company: Has NO offline backups
Result: Must pay ransom or lose all data
```

## Current State Analysis

### No Backup Functionality
```python
# Searching for backup-related code:
# - find . -name "*.py" | xargs grep -l backup
# Result: NO FILES FOUND

# The application NEVER creates backups
```

### No Export Functionality
```python
# Only import exists, no export:
src/excel_import/excel_importer.py  # ← Import only

# No equivalent exporter exists
# - No src/export/
# - No export_employees()
# - No export_to_excel()
# - No export_to_csv()
```

### Database File Vulnerability
```python
# src/database/connection.py:8
database = SqliteDatabase(None, pragmas={'foreign_keys': 1})

# Database is single file: employee_manager.db
# Vulnerabilities:
# 1. No automatic versioning
# 2. No backup before schema changes
# 3. No transaction logging
# 4. No point-in-time recovery
```

## GDPR Compliance Issues

### Right to Data Portability (Article 20)
> "The data subject shall have the right to receive the personal data concerning him or her, which he or she has provided to a controller, in a structured, commonly used, machine-readable format."

**Current Application**: ❌ Cannot provide data to employees
**Required**: ✅ Export functionality for individual employee data

### Right of Access (Article 15)
> "The data subject shall have the right to obtain confirmation from the controller as to whether or not personal data concerning him or her are being processed, and access to the personal data."

**Current Application**: ❌ Cannot show all data in portable format
**Required**: ✅ Export all employee data on request

## Proposed Solution

### Part 1: Automated Backup System

```python
# src/utils/backup_manager.py
import os
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages database backups with automatic scheduling."""

    def __init__(self,
                 database_path: Path,
                 backup_dir: Path = Path("backups"),
                 max_backups: int = 30):
        """
        Initialize backup manager.

        Args:
            database_path: Path to database file
            backup_dir: Directory to store backups
            max_backups: Maximum number of backups to keep
        """
        self.database_path = Path(database_path)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, description: str = "") -> Path:
        """
        Create a backup of the database.

        Args:
            description: Optional description for backup

        Returns:
            Path to created backup file
        """
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"employee_manager_{timestamp}.db"
        if description:
            backup_name = f"employee_manager_{timestamp}_{description}.db"

        backup_path = self.backup_dir / backup_name

        # Use SQLite backup API for safe backup
        try:
            source = sqlite3.connect(str(self.database_path))
            dest = sqlite3.connect(str(backup_path))

            # Backup with online backup API
            source.backup(dest)

            dest.close()
            source.close()

            logger.info(f"Backup created: {backup_path}")

            # Clean old backups
            self._cleanup_old_backups()

            return backup_path

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            if backup_path.exists():
                backup_path.unlink()
            raise

    def _cleanup_old_backups(self):
        """Remove old backups exceeding max_backups limit."""
        backups = sorted(
            self.backup_dir.glob("employee_manager_*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Remove excess backups
        for old_backup in backups[self.max_backups:]:
            old_backup.unlink()
            logger.info(f"Removed old backup: {old_backup}")

    def list_backups(self) -> List[dict]:
        """List all available backups with metadata."""
        backups = []

        for backup_path in self.backup_dir.glob("employee_manager_*.db"):
            stat = backup_path.stat()
            backups.append({
                'path': str(backup_path),
                'name': backup_path.name,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_mtime),
            })

        return sorted(backups, key=lambda b: b['created'], reverse=True)

    def restore_backup(self, backup_path: Path) -> bool:
        """
        Restore database from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            True if successful
        """
        backup_path = Path(backup_path)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        # Validate backup is SQLite database
        if not self._validate_sqlite_database(backup_path):
            raise ValueError(f"Invalid SQLite database: {backup_path}")

        # Close existing connections
        # (Application must handle this)

        # Restore backup
        try:
            # Create backup of current database before restore
            if self.database_path.exists():
                pre_restore_backup = self.database_path.with_suffix(
                    f".pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                )
                shutil.copy2(self.database_path, pre_restore_backup)

            # Copy backup to database location
            shutil.copy2(backup_path, self.database_path)

            logger.info(f"Restored from backup: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

    def _validate_sqlite_database(self, path: Path) -> bool:
        """Validate file is a valid SQLite database."""
        try:
            conn = sqlite3.connect(str(path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            conn.close()
            return True
        except Exception:
            return False

    def get_backup_size(self) -> int:
        """Get total size of all backups in MB."""
        total_bytes = sum(
            b.stat().st_size
            for b in self.backup_dir.glob("employee_manager_*.db")
        )
        return round(total_bytes / (1024 * 1024), 2)
```

### Part 2: Data Export Functionality

```python
# src/export/data_exporter.py
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from peewee import prefetch

from employee.models import (
    Employee, Caces, MedicalVisit, OnlineTraining,
    EmployeeDocument
)

class DataExporter:
    """Export employee data to various formats."""

    def export_employee_to_json(self, employee: Employee, output_path: Path) -> bool:
        """
        Export single employee data to JSON (GDPR data portability).

        Args:
            employee: Employee to export
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            # Load all related data
            employee_data = {
                'employee': {
                    'external_id': employee.external_id,
                    'first_name': employee.first_name,
                    'last_name': employee.last_name,
                    'email': employee.email,
                    'phone': employee.phone,
                    'entry_date': employee.entry_date.isoformat(),
                    'current_status': employee.current_status,
                    'workspace': employee.workspace,
                    'role': employee.role,
                    'contract_type': employee.contract_type,
                    'comment': employee.comment,
                },
                'caces': [
                    {
                        'type': c.type,
                        'number': c.number,
                        'issue_date': c.issue_date.isoformat() if c.issue_date else None,
                        'expiration_date': c.expiration_date.isoformat() if c.expiration_date else None,
                        'document_path': c.document_path,
                    }
                    for c in employee.caces
                ],
                'medical_visits': [
                    {
                        'visit_type': v.visit_type,
                        'visit_date': v.visit_date.isoformat() if v.visit_date else None,
                        'expiration_date': v.expiration_date.isoformat() if v.expiration_date else None,
                        'document_path': v.document_path,
                    }
                    for v in employee.medical_visits
                ],
                'online_trainings': [
                    {
                        'name': t.name,
                        'completion_date': t.completion_date.isoformat() if t.completion_date else None,
                        'expiration_date': t.expiration_date.isoformat() if t.expiration_date else None,
                        'document_path': t.document_path,
                    }
                    for t in employee.online_trainings
                ],
                'export_metadata': {
                    'export_date': datetime.now().isoformat(),
                    'export_version': '1.0',
                }
            }

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(employee_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"[ERROR] Export to JSON failed: {e}")
            return False

    def export_all_to_excel(self, output_path: Path) -> bool:
        """
        Export all employees to Excel with multiple sheets.

        Args:
            output_path: Output Excel file path

        Returns:
            True if successful
        """
        try:
            wb = openpyxl.Workbook()

            # Remove default sheet
            wb.remove(wb.active)

            # Employees sheet
            self._create_employees_sheet(wb)

            # CACES sheet
            self._create_caces_sheet(wb)

            # Medical visits sheet
            self._create_medical_visits_sheet(wb)

            # Training sheet
            self._create_training_sheet(wb)

            # Save workbook
            wb.save(output_path)
            return True

        except Exception as e:
            print(f"[ERROR] Export to Excel failed: {e}")
            return False

    def _create_employees_sheet(self, workbook):
        """Create employees summary sheet."""
        ws = workbook.create_sheet("Employés")

        # Headers
        headers = [
            "ID Externe", "Nom", "Prénom", "Email", "Téléphone",
            "Date Entrée", "Statut", "Zone", "Poste", "Type Contrat",
            "CACES Actifs", "Visites Actives", "Formations Actives"
        ]

        ws.append(headers)

        # Style headers
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')

        # Data rows with prefetch for performance
        employees = list(Employee.select().order_by(Employee.last_name))

        for emp in employees:
            ws.append([
                emp.external_id,
                emp.last_name,
                emp.first_name,
                emp.email or "",
                emp.phone or "",
                emp.entry_date.isoformat() if emp.entry_date else "",
                emp.current_status,
                emp.workspace or "",
                emp.role or "",
                emp.contract_type or "",
                emp.caces.count(),
                emp.medical_visits.count(),
                emp.online_trainings.count(),
            ])

        # Auto-width columns
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

    def _create_caces_sheet(self, workbook):
        """Create CACES detail sheet."""
        ws = workbook.create_sheet("CACES")

        headers = ["Employé", "Type", "Numéro", "Date Émission", "Date Expiration", "Statut"]
        ws.append(headers)

        # Style headers
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

        # Load all CACES with employee info
        caces_list = list(Caces.select().join(Employee))

        for c in caces_list:
            status = "Expiré" if c.is_expired else "Valide"
            ws.append([
                c.employee.full_name,
                c.type,
                c.number or "",
                c.issue_date.isoformat() if c.issue_date else "",
                c.expiration_date.isoformat() if c.expiration_date else "",
                status,
            ])

    def _create_medical_visits_sheet(self, workbook):
        """Create medical visits sheet."""
        ws = workbook.create_sheet("Visites Médicales")

        headers = ["Employé", "Type Visite", "Date Visite", "Date Expiration", "Statut"]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

        visits = list(MedicalVisit.select().join(Employee))

        for v in visits:
            status = "Expiré" if v.is_expired else "Valide"
            ws.append([
                v.employee.full_name,
                v.visit_type,
                v.visit_date.isoformat() if v.visit_date else "",
                v.expiration_date.isoformat() if v.expiration_date else "",
                status,
            ])

    def _create_training_sheet(self, workbook):
        """Create training sheet."""
        ws = workbook.create_sheet("Formations")

        headers = ["Employé", "Formation", "Date Complétion", "Date Expiration", "Statut"]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

        trainings = list(OnlineTraining.select().join(Employee))

        for t in trainings:
            status = "Expiré" if t.is_expired else "Valide"
            ws.append([
                t.employee.full_name,
                t.name,
                t.completion_date.isoformat() if t.completion_date else "",
                t.expiration_date.isoformat() if t.expiration_date else "",
                status,
            ])

    def export_to_csv(self, output_path: Path, employees: Optional[List[Employee]] = None) -> bool:
        """
        Export employee data to CSV.

        Args:
            output_path: Output CSV file path
            employees: List of employees to export (all if None)

        Returns:
            True if successful
        """
        try:
            if employees is None:
                employees = list(Employee.select().order_by(Employee.last_name))

            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')

                # Headers
                headers = [
                    "ID Externe", "Nom", "Prénom", "Email", "Téléphone",
                    "Date Entrée", "Statut", "Zone", "Poste", "Type Contrat"
                ]
                writer.writerow(headers)

                # Data rows
                for emp in employees:
                    writer.writerow([
                        emp.external_id,
                        emp.last_name,
                        emp.first_name,
                        emp.email or "",
                        emp.phone or "",
                        emp.entry_date.isoformat() if emp.entry_date else "",
                        emp.current_status,
                        emp.workspace or "",
                        emp.role or "",
                        emp.contract_type or "",
                    ])

            return True

        except Exception as e:
            print(f"[ERROR] Export to CSV failed: {e}")
            return False
```

### Part 3: Automatic Backup on Application Start

```python
# src/ui_ctk/app.py
from src.utils.backup_manager import BackupManager
from src.config import Config

def setup_database():
    """Initialize database with automatic backup."""
    db_path = Config.get_database_path()

    # Create backup manager
    backup_manager = BackupManager(
        database_path=db_path,
        backup_dir=Path("backups"),
        max_backups=30
    )

    # Create backup if database exists
    if db_path.exists():
        try:
            backup_path = backup_manager.create_backup(description="startup")
            print(f"[OK] Database backup created: {backup_path.name}")
        except Exception as e:
            print(f"[WARN] Backup creation failed: {e}")

    # Initialize database
    init_database(db_path)
```

### Part 4: Backup/Export UI

```python
# src/ui_ctk/views/backup_view.py (NEW)
import customtkinter as ctk
from pathlib import Path
from src.utils.backup_manager import BackupManager
from src.export.data_exporter import DataExporter
from tkinter import filedialog, messagebox

class BackupView(ctk.CTkFrame):
    """Backup and export management view."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.backup_manager = BackupManager(
            database_path=Config.get_database_path(),
            backup_dir=Path("backups"),
            max_backups=30
        )

        self.exporter = DataExporter()

        self.create_ui()
        self.refresh_backup_list()

    def create_ui(self):
        """Create backup management UI."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Gestion des Sauvegardes",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        # Backup buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10, fill="x", padx=20)

        # Create backup button
        create_backup_btn = ctk.CTkButton(
            button_frame,
            text="Créer une Sauvegarde",
            command=self.create_backup,
            width=200
        )
        create_backup_btn.pack(side="left", padx=5)

        # Restore backup button
        restore_backup_btn = ctk.CTkButton(
            button_frame,
            text="Restaurer",
            command=self.restore_backup,
            width=200
        )
        restore_backup_btn.pack(side="left", padx=5)

        # Export buttons
        export_frame = ctk.CTkFrame(self)
        export_frame.pack(pady=10, fill="x", padx=20)

        # Export all to Excel
        export_excel_btn = ctk.CTkButton(
            export_frame,
            text="Exporter tout vers Excel",
            command=self.export_excel,
            width=200
        )
        export_excel_btn.pack(side="left", padx=5)

        # Export to CSV
        export_csv_btn = ctk.CTkButton(
            export_frame,
            text="Exporter vers CSV",
            command=self.export_csv,
            width=200
        )
        export_csv_btn.pack(side="left", padx=5)

        # Backup list
        self.backup_listbox = ctk.CTkTextbox(self, height=400)
        self.backup_listbox.pack(pady=20, fill="both", expand=True, padx=20)

    def create_backup(self):
        """Create a new backup."""
        try:
            backup_path = self.backup_manager.create_backup(description="manual")
            messagebox.showinfo(
                "Succès",
                f"Sauvegarde créée:\n{backup_path.name}"
            )
            self.refresh_backup_list()
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la sauvegarde:\n{e}")

    def refresh_backup_list(self):
        """Refresh the backup list display."""
        backups = self.backup_manager.list_backups()

        text = ""
        for backup in backups:
            text += f"📦 {backup['name']}\n"
            text += f"   Taille: {backup['size_mb']} MB\n"
            text += f"   Créé: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        self.backup_listbox.delete("1.0", "end")
        self.backup_listbox.insert("1.0", text)

    def restore_backup(self):
        """Restore selected backup."""
        # Show file dialog to select backup
        backup_path = filedialog.askopenfilename(
            title="Sélectionner une sauvegarde",
            initialdir=str(self.backup_manager.backup_dir),
            filetypes=[("SQLite Database", "*.db")]
        )

        if backup_path:
            confirm = messagebox.askyesno(
                "Confirmer la restauration",
                "Voulez-vous vraiment restaurer cette sauvegarde ?\n\n"
                "La base de données actuelle sera remplacée."
            )

            if confirm:
                try:
                    self.backup_manager.restore_backup(Path(backup_path))
                    messagebox.showinfo("Succès", "Base de données restaurée")
                    # Restart application
                except Exception as e:
                    messagebox.showerror("Erreur", f"Restauration échouée:\n{e}")

    def export_excel(self):
        """Export all data to Excel."""
        save_path = filedialog.asksaveasfilename(
            title="Exporter vers Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )

        if save_path:
            try:
                self.exporter.export_all_to_excel(Path(save_path))
                messagebox.showinfo("Succès", f"Exporté vers:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Export échoué:\n{e}")

    def export_csv(self):
        """Export to CSV."""
        save_path = filedialog.asksaveasfilename(
            title="Exporter vers CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )

        if save_path:
            try:
                self.exporter.export_to_csv(Path(save_path))
                messagebox.showinfo("Succès", f"Exporté vers:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Export échoué:\n{e}")
```

## Implementation Plan

### Phase 1: Backup System (3 hours)
1. Create `src/utils/backup_manager.py`
2. Implement BackupManager class
3. Add automatic backup on app startup
4. Add backup before schema changes
5. Write tests

### Phase 2: Export Functionality (3 hours)
1. Create `src/export/data_exporter.py`
2. Implement JSON export (GDPR)
3. Implement Excel export
4. Implement CSV export
5. Write tests

### Phase 3: Backup/Export UI (2 hours)
1. Create `src/ui_ctk/views/backup_view.py`
2. Add to main navigation
3. Implement file dialogs
4. Test export functionality

### Phase 4: Integration (1 hour)
1. Add backup scheduling (optional)
2. Add backup encryption (optional)
3. Document backup procedures
4. Create user guide

## Files to Create
- `src/utils/backup_manager.py`
- `src/export/__init__.py`
- `src/export/data_exporter.py`
- `src/ui_ctk/views/backup_view.py`
- `tests/test_backup_manager.py`
- `tests/test_data_exporter.py`
- `backups/.gitignore` (add: `*.db`)

## Files to Modify
- `src/ui_ctk/app.py` - Add automatic backup
- `src/ui_ctk/main_window.py` - Add backup view navigation
- `.gitignore` - Ignore backup files

## Database Backup Strategy

### Backup Schedule
- **Automatic**: On application startup
- **Manual**: Via UI button
- **Scheduled**: Optional cron job for production

### Backup Retention
- Keep last 30 backups
- Approx 30 days if running daily
- Total storage: ~60-100 MB (30 × ~2-3 MB)

### Backup Types
1. **Full backup**: Entire database
2. **Incremental**: Changes only (future enhancement)
3. **Exported**: Excel/JSON for portability

## GDPR Compliance Features

### Data Portability
```python
# Employee can request their data
exporter = DataExporter()
exporter.export_employee_to_json(employee, Path("employee_data.json"))
# → Complete data in structured, machine-readable format
```

### Right to Access
```python
# HR can provide employee's data on request
employee = Employee.get_by_id(employee_id)
exporter.export_employee_to_json(employee, output_path)
# → Email or provide file to employee
```

## Related Issues
- #007: No undo/redo (backups enable recovery)
- #018: No audit trail (backups preserve history)
- #040: No configuration file support (backup paths should be configurable)

## References
- GDPR Article 15 (Right of Access): https://gdpr-info.eu/art-15-gdpr/
- GDPR Article 20 (Data Portability): https://gdpr-info.eu/art-20-gdpr/
- SQLite Backup API: https://www.sqlite.org/backup.html
- Database Backup Best Practices: https://www.mongodb.com/basics/backups

## Priority
**CRITICAL** - Complete data loss risk without backups

## Estimated Effort
9-10 hours (backup + export + UI + tests)

## Mitigation
While waiting for full implementation:
1. **MANUAL BACKUP**: Copy employee_manager.db regularly
   ```bash
   # Weekly manual backup
   cp employee_manager.db backups/employee_manager_$(date +%Y%m%d).db
   ```

2. **SQLite command-line backup**:
   ```bash
   sqlite3 employee_manager.db ".backup backups/backup_$(date +%Y%m%d).db"
   ```

3. **Document backup procedure** for users:
   - Stop application before backup
   - Copy employee_manager.db to safe location
   - Store backups on separate drive/cloud
   - Test restore procedure regularly

4. **Enable file versioning** (if on Windows/Mac):
   - Windows: File History
   - macOS: Time Machine
   - Linux: rsync to backup server

5. **Use cloud storage** for database directory:
   - Google Drive
   - Dropbox
   - OneDrive
   - Ensure automatic sync is enabled
