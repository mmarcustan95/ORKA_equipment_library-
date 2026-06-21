"""
seed_test_data.py
-----------------
Inserts 50 realistic C&Q test entries into Supabase with embeddings.
All entries are tagged 'testing' for easy cleanup afterwards.

Run from the project root:
    python -m main.seed_test_data

To delete test entries afterwards, run in Supabase SQL Editor:
    DELETE FROM entries WHERE keywords::text LIKE '%testing%';
"""

import os
import json
from pathlib import Path
from datetime import date
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

import psycopg2
from .models import ValidationEntry
from .vector_embed import VectorEmbedder

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("Set DATABASE_URL in main/.env to point at your Supabase instance.")

TEST_ENTRIES = [
    # WFI Loop
    ("WFI Loop", None, "IQ", "Verify WFI loop pipework installation matches P&ID drawings", "Slope on return leg measured at 1:80, below required 1:100 gradient for self-draining", "Re-surveyed pipework with laser level. Adjusted pipe hanger at support S-14. Confirmed 1:105 slope achieved across full return leg.", ["WFI", "pipework", "slope", "IQ", "testing"]),
    ("WFI Loop", "WFIS-3000", "OQ", "Demonstrate WFI loop maintains ≥80°C during continuous circulation", "Temperature drop to 76°C observed at use point UP-07 during peak demand cycle", "Insulation gap identified at elbow joint near UP-07. Added 50mm Armaflex insulation. Temperature confirmed ≥81°C at all use points across three consecutive cycles.", ["WFI", "temperature", "OQ", "insulation", "testing"]),
    ("WFI Loop", "WFIS-3000", "PQ", "Confirm WFI meets Ph. Eur. specification over 4-week monitoring period", "TOC spike of 620 ppb detected on Day 11, exceeding 500 ppb limit", "Traced to degraded gasket on sample valve SV-03. Replaced with EPDM gasket. System flushed 3x. TOC returned to <200 ppb. Restarted 4-week clock per protocol.", ["WFI", "TOC", "PQ", "gasket", "testing"]),
    ("WFI Loop", None, "OQ", "Validate heat sanitisation cycle at 121°C for minimum 30 minutes", "Cycle aborted at 18 minutes due to pressure sensor fault on PS-102", "PS-102 found to have water ingress from previous hydrostatic test. Replaced sensor, recalibrated against reference. Three consecutive successful cycles completed.", ["WFI", "sanitisation", "pressure sensor", "OQ", "testing"]),

    # HVAC / Clean Room
    ("HVAC System", "AHU-2200X", "IQ", "Confirm AHU installation matches design specification and drawings", "HEPA filter bank installed in incorrect orientation — arrow indicating airflow direction pointing upstream", "Filters repositioned to correct orientation. Re-taped seals. Leak test repeated per EN 1822. No leakage detected above 0.01%.", ["HVAC", "HEPA", "IQ", "filter", "testing"]),
    ("HVAC System", "AHU-2200X", "OQ", "Verify ISO 7 classification achieved in Grade C cleanroom", "Particle count at 0.5µm exceeded 352,000/m³ limit at sample point SP-04 near door seal", "Door seal found to be misaligned creating a 3mm gap. Replaced magnetic door seal. Particle counts confirmed compliant at all 9 sample points.", ["HVAC", "particle count", "ISO 7", "OQ", "testing"]),
    ("HVAC System", None, "OQ", "Validate room pressure differentials per design — +15Pa Grade B vs Grade C", "Pressure differential reading only +8Pa between Grade B filling room and Grade C corridor", "Balancing damper BD-11 found partially closed from commissioning. Adjusted to design position. Differential confirmed at +16Pa and stable over 4-hour monitoring.", ["HVAC", "pressure differential", "OQ", "damper", "testing"]),
    ("HVAC System", "AHU-2200X", "PQ", "Demonstrate Grade B environment maintained during aseptic filling simulation", "Air changes per hour dropped to 18 ACH during filling simulation, below minimum 20 ACH", "Filter loading analysis showed HEPA pre-filter at 85% capacity. Pre-filter replaced. ACH confirmed at 23 ACH. Smoke visualisation repeated — unidirectional flow confirmed.", ["HVAC", "ACH", "PQ", "HEPA", "testing"]),

    # Autoclave
    ("Autoclave", "LJAX-500", "IQ", "Verify autoclave chamber volume and utility connections per URS", "Condensate drain line connected to drain without air break, creating potential back-contamination route", "Drain line rerouted with 50mm air break above floor drain. Updated as-built drawing. Confirmed compliant with EN 285.", ["autoclave", "drain", "IQ", "testing"]),
    ("Autoclave", "LJAX-500", "OQ", "Demonstrate F0 ≥12 min achieved at all load positions using thermocouple mapping", "Cold spot identified at load position LP-3 (geometric centre of load) with F0 of 9.8 min", "Load configuration modified — spacing between items increased from 10mm to 25mm to improve steam penetration. F0 at LP-3 confirmed at 14.2 min across three runs.", ["autoclave", "F0", "thermocouple", "OQ", "sterilisation", "testing"]),
    ("Autoclave", "LJAX-500", "OQ", "Validate Bowie-Dick test performance for steam penetration", "Bowie-Dick test sheet showed uneven colour change with pale centre indicating air entrapment", "Investigated vacuum pump performance — found check valve worn. Replaced check valve. Vacuum leak rate test passed. Bowie-Dick test passed on three consecutive cycles.", ["autoclave", "Bowie-Dick", "vacuum", "OQ", "testing"]),
    ("Autoclave", "LJAX-500", "PQ", "Confirm sterilisation efficacy using biological indicators (G. stearothermophilus)", "One BI vial at position LP-7 showed growth after 48h incubation — positive result", "Investigated — BI vial found to have been placed too close to chamber wall blocking steam access. Load configuration updated. Three consecutive cycles with all BIs negative achieved.", ["autoclave", "biological indicator", "PQ", "sterilisation", "testing"]),

    # Bioreactor
    ("Bioreactor Skid", "BIOSTAT-200L", "IQ", "Verify vessel material certificates and surface finish specifications", "Ra surface finish measured at 0.92 µm on vessel interior — exceeds 0.8 µm specification", "Polishing carried out by vendor on-site. Ra re-measured at 0.61 µm at 5 representative points. Updated certification provided.", ["bioreactor", "surface finish", "Ra", "IQ", "testing"]),
    ("Bioreactor Skid", "BIOSTAT-200L", "OQ", "Validate dissolved oxygen (DO) probe calibration and response time", "DO probe response time of 68 seconds measured — exceeds 60-second specification", "Probe membrane found to have minor fouling from storage. Membrane replaced, probe re-polarised for 6 hours. Response time confirmed at 42 seconds.", ["bioreactor", "dissolved oxygen", "DO probe", "OQ", "testing"]),
    ("Bioreactor Skid", "BIOSTAT-200L", "OQ", "Demonstrate pH control within ±0.05 pH units of setpoint during simulated run", "pH oscillation of ±0.12 pH units observed during acid/base pump control test", "PID parameters found to be factory default — not tuned for vessel volume. Retuned proportional gain from 1.2 to 0.4. pH control confirmed within ±0.03 pH units.", ["bioreactor", "pH", "PID", "OQ", "testing"]),
    ("Bioreactor Skid", "BIOSTAT-200L", "PQ", "Confirm CIP cycle achieves <10 CFU/cm² bioburden on vessel surfaces", "Rinse water conductivity at end of CIP cycle reading 180 µS/cm — above 10 µS/cm acceptance criterion", "CIP programme missing final WFI rinse step due to programming error during import. Step added and validated. Conductivity confirmed <5 µS/cm. Swab results: <1 CFU/cm².", ["bioreactor", "CIP", "conductivity", "PQ", "bioburden", "testing"]),

    # Freeze Dryer
    ("Freeze Dryer", "LYOMAX-10", "IQ", "Confirm shelf temperature uniformity specification ±2°C across all shelves", "Temperature variation of ±4.1°C measured between shelf 1 (top) and shelf 5 (bottom)", "Heat transfer fluid flow rate through shelf manifold unbalanced. Flow balancing valves adjusted. Temperature variation confirmed at ±1.6°C across all shelves.", ["freeze dryer", "lyophiliser", "shelf temperature", "IQ", "testing"]),
    ("Freeze Dryer", "LYOMAX-10", "OQ", "Validate condenser temperature achieves -55°C within 60 minutes of startup", "Condenser reached only -48°C after 90 minutes — refrigeration capacity insufficient", "Refrigerant charge found low due to slow leak at compressor shaft seal. Seal replaced, system recharged. Condenser achieved -57°C within 45 minutes.", ["freeze dryer", "condenser", "refrigerant", "OQ", "testing"]),
    ("Freeze Dryer", "LYOMAX-10", "OQ", "Demonstrate chamber leak rate <0.04 mbar/min per ASTM F2638", "Leak rate measured at 0.11 mbar/min — exceeds acceptance criterion", "Leak located at viewport O-ring seal using helium leak detector. O-ring replaced with Viton grade. Leak rate confirmed at 0.02 mbar/min.", ["freeze dryer", "leak rate", "O-ring", "OQ", "vacuum", "testing"]),

    # CIP System
    ("CIP System", "CIP-150", "IQ", "Verify spray ball coverage across all vessels in CIP circuit", "Spray ball SB-04 on tank T-302 providing only 180° coverage — full 360° required", "Spray ball found to have 2 of 8 nozzles blocked with installation debris. Cleaned and flushed. 360° coverage confirmed with riboflavin spray ball test.", ["CIP", "spray ball", "coverage", "IQ", "testing"]),
    ("CIP System", "CIP-150", "OQ", "Demonstrate NaOH caustic wash at 2% concentration at ≥70°C for minimum 20 minutes", "Caustic concentration at end of wash cycle measured at 1.6% — below 2% minimum", "Dosing pump DP-02 found to have worn check valves causing backflow. Check valves replaced. Caustic concentration confirmed at 2.1% ± 0.1% across three cycles.", ["CIP", "caustic", "NaOH", "OQ", "concentration", "testing"]),
    ("CIP System", "CIP-150", "PQ", "Confirm TOC in final rinse water <10 ppm across full CIP circuit", "TOC of 34 ppm measured in final rinse from vessel V-201 — trace of caustic carryover", "Dead leg identified on return line from V-201 — 6D rule violated. Pipework modified to eliminate dead leg. TOC confirmed <5 ppm across all vessels.", ["CIP", "TOC", "dead leg", "PQ", "testing"]),

    # Purified Water
    ("Purified Water System", "PWS-2000", "IQ", "Confirm RO membrane installation and pre-treatment sequence", "Activated carbon filter installed downstream of softener rather than upstream — incorrect sequence", "Carbon filter relocated to correct position upstream of softener per P&ID. Flow direction arrows confirmed. As-built drawing updated.", ["purified water", "RO", "carbon filter", "IQ", "testing"]),
    ("Purified Water System", "PWS-2000", "OQ", "Validate conductivity meets Ph. Eur. specification ≤4.3 µS/cm at 20°C", "Conductivity reading 6.8 µS/cm at sample point SP-03 on distribution loop", "EDI unit found in bypass mode following maintenance — isolation valve not reopened. EDI returned to service. Conductivity confirmed 1.2 µS/cm at all sample points.", ["purified water", "conductivity", "EDI", "OQ", "testing"]),
    ("Purified Water System", "PWS-2000", "PQ", "Demonstrate bioburden <100 CFU/mL over 12-week monitoring period", "Bioburden count of 380 CFU/mL at use point UP-11 at Week 8", "Sanitisation frequency increased from weekly to twice-weekly. Dead leg at UP-11 eliminated. Bioburden returned to <10 CFU/mL. 12-week clock restarted.", ["purified water", "bioburden", "sanitisation", "PQ", "testing"]),

    # Clean Steam Generator
    ("Clean Steam Generator", "CSG-500", "IQ", "Verify feedwater quality and generator vessel material certification", "Feedwater conductivity supply to CSG measured at 12 µS/cm — exceeds 5 µS/cm limit", "CSG was incorrectly connected to plant steam condensate return rather than purified water supply. Repiped to PW system. Feedwater conductivity confirmed 1.8 µS/cm.", ["clean steam", "CSG", "feedwater", "IQ", "testing"]),
    ("Clean Steam Generator", "CSG-500", "OQ", "Confirm clean steam dryness fraction ≥0.95 per EN 285", "Dryness fraction measured at 0.88 using throttling calorimeter method", "Steam trap ST-01 found to be passing — allowing water carry-over. Steam trap replaced. Dryness fraction confirmed at 0.97.", ["clean steam", "dryness fraction", "steam trap", "OQ", "testing"]),

    # Environmental Monitoring
    ("Environmental Monitoring System", None, "OQ", "Validate active air sampling at Grade A filling zone during aseptic fill simulation", "Particle counter alarming intermittently at 0.5µm channel showing counts of 3520/m³", "Isokinetic probe orientation found to be 45° off-axis to unidirectional airflow. Probe repositioned perpendicular to airflow. Counts confirmed <10 particles/m³ at 0.5µm.", ["environmental monitoring", "active air", "Grade A", "OQ", "particle", "testing"]),
    ("Environmental Monitoring System", None, "PQ", "Demonstrate Grade B settle plate results <5 CFU per 4-hour exposure", "Settle plate at position SB-07 showing 8 CFU after 4 hours — exceeds Grade B limit", "Personnel flow analysis identified route crossing causing turbulence near SB-07. Gowning procedure updated. Personnel movement protocol revised. Subsequent 6 sessions all <2 CFU.", ["environmental monitoring", "settle plate", "Grade B", "PQ", "testing"]),

    # SCADA / PLC
    ("SCADA System", "Siemens S7-1500", "OQ", "Validate alarm management — all critical alarms must annunciate within 5 seconds", "High-temperature alarm for reactor jacket HTA-201 taking 23 seconds to annunciate on SCADA", "Polling interval on Siemens S7-1500 PLC found set to 20 seconds. Reduced to 1 second for critical alarm tags. Annunciation confirmed within 2 seconds.", ["SCADA", "PLC", "Siemens", "alarm", "OQ", "testing"]),
    ("SCADA System", "Siemens S7-1500", "OQ", "Demonstrate 21 CFR Part 11 compliant audit trail for all parameter changes", "Audit trail entries showing generic 'admin' user for all changes rather than individual user IDs", "Shared admin account in use by multiple operators. Individual user accounts created for all 8 operators. Password policy enforced. Audit trail tested with individual logins — all entries correctly attributed.", ["SCADA", "21 CFR Part 11", "audit trail", "OQ", "testing"]),
    ("SCADA System", "Siemens S7-1500", "IQ", "Confirm PLC programme version matches approved documentation", "PLC programme version 2.1.3 installed — qualification documents reference version 2.1.1", "Vendor had applied patch during installation without change control. Change assessment completed. Patch reviewed by QA — no impact on validated functionality. IQ re-executed with version 2.1.3 referenced.", ["SCADA", "PLC", "version control", "IQ", "change control", "testing"]),

    # Centrifuge
    ("Centrifuge", "SIGMA-8K", "OQ", "Validate maximum RCF of 8,000 × g is achievable and speed control is accurate", "Actual RCF measured at 7,340 × g at set point of 8,000 × g using tachometer", "Belt drive tensioner found loose, causing slippage at high speed. Belt tensioned to manufacturer specification. RCF confirmed at 8,020 × g using calibrated tachometer.", ["centrifuge", "RCF", "speed", "OQ", "testing"]),
    ("Centrifuge", "SIGMA-8K", "IQ", "Verify rotor serial numbers and maximum load certification match URS", "Rotor serial number R-4492 on IQ documentation — physical rotor shows serial R-4429", "Documentation transcription error confirmed. Physical rotor R-4429 certification retrieved from vendor. Certificate matches URS specification. IQ document corrected via amendment.", ["centrifuge", "rotor", "serial number", "IQ", "documentation", "testing"]),

    # Incubator
    ("Incubator", "MIR-554", "OQ", "Validate temperature uniformity ±1°C throughout chamber at 37°C setpoint", "Temperature variation of ±2.3°C measured between top shelf and base of chamber", "Fan motor found running at 60% speed due to firmware error. Motor speed corrected to 100%. Temperature mapping repeated — uniformity confirmed ±0.6°C at all 9 sensor positions.", ["incubator", "temperature uniformity", "OQ", "testing"]),
    ("Incubator", "MIR-554", "OQ", "Demonstrate temperature recovery to setpoint within 15 minutes after door opening", "Temperature recovery taking 28 minutes after 30-second door open event", "Door gasket worn on right side allowing warm air infiltration during recovery. Gasket replaced. Recovery confirmed at 11 minutes after door open.", ["incubator", "temperature recovery", "door gasket", "OQ", "testing"]),

    # Laminar Flow Cabinet
    ("Laminar Flow Cabinet", "MSC-Advantage", "OQ", "Validate HEPA filter integrity per ISO 14644-3 using photometer scan", "Leak detected at filter-to-frame seal on right side — penetration reading 0.03% above 0.01% limit", "Adhesive sealant between filter frame and housing had not fully cured at time of test. 48-hour cure time allowed. Re-scan confirmed 0.001% penetration — pass.", ["laminar flow", "HEPA", "filter integrity", "photometer", "OQ", "testing"]),
    ("Laminar Flow Cabinet", "MSC-Advantage", "OQ", "Confirm unidirectional airflow velocity of 0.45 m/s ±20% at working height", "Airflow velocity at right edge of work surface measuring 0.28 m/s — below lower limit of 0.36 m/s", "Airflow profiling showed channelling due to equipment placed inside cabinet. Cabinet cleared. Velocity remeasured — 0.47 m/s ± 0.04 m/s across work surface.", ["laminar flow", "airflow velocity", "OQ", "unidirectional", "testing"]),

    # Balance / Weighing
    ("Analytical Balance", "Mettler XS205", "IQ", "Confirm balance installation location meets vibration and levelling requirements", "Balance levelling bubble found off-centre after installation on benchtop near HVAC diffuser", "Anti-vibration table installed. Balance relevelled. Vibration check using repeatability test: 10 × 200mg weight — RSD 0.0008%, within acceptance criterion of 0.01%.", ["balance", "weighing", "vibration", "IQ", "testing"]),
    ("Analytical Balance", "Mettler XS205", "OQ", "Validate linearity across full weighing range 0.1mg to 205g", "Linearity deviation of 0.08mg observed at mid-range (100g) — exceeds 0.05mg acceptance criterion", "Balance internal calibration weight found out of tolerance. Factory service performed. External calibration with OIML E2 weights completed. Linearity confirmed ±0.02mg across full range.", ["balance", "linearity", "calibration", "OQ", "testing"]),

    # Temperature Mapping
    ("Cold Room", "CR-01", "OQ", "Validate cold room temperature distribution 2°C to 8°C at full load", "Temperature at top-rear corner (sensor T-09) reading 1.1°C — below lower limit of 2°C", "Air circulation analysis showed dead zone at top-rear. Additional circulation fan installed. Temperature mapping repeated with fan — all 15 sensor positions within 2.1°C to 7.8°C.", ["cold room", "temperature mapping", "OQ", "storage", "testing"]),
    ("Cold Room", "CR-01", "PQ", "Demonstrate temperature recovery after door open event within 30 minutes", "Temperature at sensor T-12 reached 9.8°C during power interruption simulation — above 8°C limit", "Power interruption recovery procedure in SOP did not specify minimum door-closed time. SOP updated to mandate door closed during recovery. Thermal mass study performed — full recovery confirmed within 22 minutes.", ["cold room", "temperature recovery", "PQ", "power interruption", "testing"]),

    # Nitrogen System
    ("Nitrogen Blanketing System", None, "OQ", "Validate nitrogen purity ≥99.998% at all use points", "Nitrogen purity at use point NUP-04 measuring 99.91% — below 99.998% specification", "Atmospheric air ingress identified at compression fitting CF-22 downstream of pressure regulator. Fitting replaced with orbital-welded connection. Purity confirmed 99.999% at all use points.", ["nitrogen", "blanketing", "purity", "OQ", "testing"]),

    # Compressed Air
    ("Compressed Air System", None, "OQ", "Confirm compressed air meets ISO 8573-1 Class 1 for oil content ≤0.01 mg/m³", "Oil vapour content measured at 0.08 mg/m³ at sample point CA-07 — exceeds Class 1 limit", "Activated carbon filter downstream of compressor found saturated. Filter cartridge replaced. Oil vapour confirmed <0.005 mg/m³ at all 12 sample points.", ["compressed air", "oil content", "ISO 8573", "OQ", "testing"]),

    # Data Logger / Calibration
    ("Data Logger", "Testo 176T4", "IQ", "Verify data logger calibration certificate is current and traceable to national standards", "Calibration certificate dated 14 months ago — exceeds 12-month recalibration interval", "Data logger removed from service. Returned to UKAS-accredited lab for recalibration. Certificate issued with current date and UKAS reference. IQ re-executed with valid certificate.", ["data logger", "calibration", "IQ", "UKAS", "testing"]),

    # Vessel / Pressure Equipment
    ("Buffer Preparation Vessel", "V-201", "IQ", "Confirm pressure vessel inspection and pressure test records per PED 2014/68/EU", "Pressure test certificate references design pressure of 3 bar — URS specifies 4 bar design pressure", "Discrepancy traced to early revision URS used by vessel fabricator. URS updated at project change to 4 bar but vendor not notified. Vessel replaced with correct 4 bar rated unit. New certificate obtained.", ["vessel", "pressure", "PED", "IQ", "testing"]),
    ("Buffer Preparation Vessel", "V-201", "OQ", "Validate mixing homogeneity — conductivity variation ≤2% across vessel at end of mix", "Conductivity variation of 6.8% measured between top and bottom sample points at end of 15-minute mix", "Impeller found to have one of three blades broken during installation. Impeller replaced. Mix time extended to 20 minutes per revised protocol. Homogeneity confirmed ±0.9%.", ["vessel", "mixing", "homogeneity", "OQ", "impeller", "testing"]),

    # UPS / Utilities
    ("UPS System", "Eaton 9PX", "IQ", "Verify UPS capacity matches critical load calculation in URS", "UPS nameplate rating 10 kVA — critical load calculation in URS shows 14.2 kVA required", "UPS unit ordered against early-stage load estimate. Final load schedule revised but UPS not upsized. Additional 10 kVA UPS installed in parallel. Combined capacity 20 kVA confirmed sufficient.", ["UPS", "utilities", "capacity", "IQ", "testing"]),
    ("UPS System", "Eaton 9PX", "OQ", "Demonstrate UPS provides minimum 15-minute runtime at full critical load", "UPS runtime measured at 9 minutes at full load — below 15-minute requirement", "Battery bank found to have 3 of 12 cells at end of service life. Full battery replacement performed. Runtime confirmed at 19 minutes at full critical load.", ["UPS", "battery", "runtime", "OQ", "testing"]),

    # Sterilising Filter
    ("Sterilising Filter", "Millipak-200", "OQ", "Validate bacterial retention using Brevundimonas diminuta challenge at 107 CFU/cm²", "Filter challenge test failed — breakthrough detected in effluent sample at 103 CFU/mL", "Filter integrity test (bubble point) re-run prior to challenge — passed. Investigation revealed challenge organism concentration below 107 CFU/cm² due to pipetting error. Test repeated correctly. Retention confirmed — 0 CFU/mL effluent.", ["sterilising filter", "bacterial retention", "OQ", "integrity", "testing"]),
    ("Sterilising Filter", "Millipak-200", "OQ", "Confirm post-use integrity test (diffusion flow) passes after simulated batch processing", "Post-use diffusion flow value of 8.2 mL/min measured — above pass limit of 6.0 mL/min", "Filter housing drain valve found not fully closed during test, introducing false airflow. Drain valve closed and retested. Diffusion flow confirmed 4.1 mL/min — pass.", ["sterilising filter", "integrity test", "diffusion flow", "OQ", "testing"]),
]

def seed():
    conn = psycopg2.connect(DB_URL)
    total = len(TEST_ENTRIES)
    print(f"Seeding {total} test entries into Supabase...")

    for i, (equipment, model, phase, outcome, obstacle, resolution, keywords) in enumerate(TEST_ENTRIES, 1):
        entry = ValidationEntry(
            id=uuid4(),
            project_name="ORKA Test Dataset",
            equipment_system=equipment,
            model_number=model,
            validation_phase=phase,
            consultant="Marcus",
            intended_outcome=outcome,
            obstacle=obstacle,
            resolution=resolution,
            date_logged=date(2026, 6, 20),
            keywords=keywords,
        )

        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO entries (id, project_name, equipment_system, model_number, validation_phase,
                                    consultant, intended_outcome, obstacle, resolution, date_logged,
                                    attachments, keywords)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                str(entry.id), entry.project_name, entry.equipment_system, entry.model_number,
                entry.validation_phase, entry.consultant, entry.intended_outcome, entry.obstacle,
                entry.resolution, entry.date_logged.isoformat(), "",
                json.dumps(entry.keywords),
            ))
            conn.commit()

            embedding = VectorEmbedder(entry).embed()
            cur2 = conn.cursor()
            cur2.execute("UPDATE entries SET embedding = %s WHERE id = %s", (embedding, str(entry.id)))
            conn.commit()
            print(f"[{i}/{total}] ✓ {equipment} | {phase}")

        except Exception as e:
            conn.rollback()
            print(f"[{i}/{total}] ✗ {equipment} | {phase} — {e}")

    conn.close()
    print("\nDone. To remove test data run in Supabase SQL Editor:")
    print("  DELETE FROM entries WHERE keywords::text LIKE '%testing%';")


if __name__ == "__main__":
    seed()
