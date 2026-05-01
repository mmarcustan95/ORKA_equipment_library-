from main.models import ValidationEntry
from datetime import date
from typing import List

# In-memory storage with dummy data for testing
db: List[ValidationEntry] = [
    ValidationEntry(
        project_name="Project Alpha - BioPharma",
        equipment_system="Centrifuge C-102",
        consultant="ORKA Consultant",
        validation_phase="OQ (Operational Qualification)",
        intended_outcome="Stable rotation at 15,000 RPM for 30 mins",
        obstacle="Excessive vibration at high speeds causing safety cutoff",
        resolution="Installed secondary vibration damping mounts and recalibrated the balance sensors.",
        date_logged=date(2023, 11, 15),
        keywords=["vibration", "centrifuge", "OQ", "safety"]
    ),
    ValidationEntry(
        project_name="Project Gamma - Labs",
        equipment_system="Agilent HPLC 1260",
        consultant="ORKA Consultant",
        validation_phase="PQ (Performance Qualification)",
        intended_outcome="Consistent retention times across 5 injection cycles",
        obstacle="Retention time drift observed after the 3rd injection",
        resolution="Identified air bubbles in the degasser; performed manual purge and replaced inlet filters.",
        date_logged=date(2024, 1, 10),
        keywords=["HPLC", "chromatography", "drift", "maintenance"]
    ),
    ValidationEntry(
        project_name="Orka Internal Training",
        equipment_system="DeltaV Control System",
        consultant="ORKA Consultant",
        validation_phase="FAT (Factory Acceptance Test)",
        intended_outcome="Successful automated emergency shutdown (ESD) sequence",
        obstacle="IO mapping error caused the valve to stay open during ESD",
        resolution="Corrected the logic in the control module and re-verified the IO mapping table.",
        date_logged=date(2024, 2, 22),
        keywords=["DeltaV", "automation", "ESD", "logic error"]
    )
]