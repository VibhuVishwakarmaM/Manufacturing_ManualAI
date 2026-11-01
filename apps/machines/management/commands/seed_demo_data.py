import os
import fitz  # PyMuPDF
from django.core.management.base import BaseCommand
from django.core.files import File
from django.contrib.auth.models import User
from apps.machines.models import Machine
from apps.manuals.models import Manual
from apps.document_processing.processor import process_manual

class Command(BaseCommand):
    help = 'Seed demo machines and create verifiable synthetic PDF equipment manuals.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding demo equipment and technical manuals..."))

        admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(username='admin').first()

        # 1. Create Demo Machines
        machine_a, _ = Machine.objects.get_or_create(
            model_number='VF2SS-2024',
            defaults={
                'name': 'CNC Vertical Machining Center VF-2SS',
                'manufacturer': 'Precision CNC Dynamics Inc.',
                'description': 'High-performance 5-axis vertical machining center for aerospace alloys.',
                'status': 'ACTIVE'
            }
        )

        machine_b, _ = Machine.objects.get_or_create(
            model_number='HP500-2023',
            defaults={
                'name': 'Heavy Hydraulic Stamping Press HP-500',
                'manufacturer': 'HydroForce Industrial Machinery',
                'description': '500-Ton hydraulic press unit for sheet metal stamping and deep drawing.',
                'status': 'ACTIVE'
            }
        )

        self.stdout.write(self.style.SUCCESS(f"Registered demo machines: {machine_a.name} & {machine_b.name}"))

        # Temp directory for synthetic PDFs
        os.makedirs('media/demo_manuals', exist_ok=True)

        # 2. Build PDF for Machine A (CNC Milling Center)
        pdf_a_path = 'media/demo_manuals/VF2SS_Maintenance_Manual.pdf'
        doc_a = fitz.open()

        # Page 1: Title & Overview
        p1 = doc_a.new_page()
        p1.insert_text(fitz.Point(50, 72), "CNC VERTICAL MACHINING CENTER VF-2SS\nOPERATOR & PREVENTIVE MAINTENANCE MANUAL\nRevision: 2024.1", fontsize=16)
        p1.insert_text(fitz.Point(50, 150), 
            "CHAPTER 1: GENERAL SPECIFICATIONS AND SAFETY PROTOCOLS\n\n"
            "The VF-2SS vertical machining center operates at spindle speeds up to 12,000 RPM.\n"
            "Before performing any maintenance or inspection, operators must lock out and tag out the main electrical isolator.\n"
            "Daily inspection must verify air line pressure is maintained between 85 PSI and 100 PSI (5.9 - 6.9 bar).\n"
            "Ensure the chip auger and enclosure doors are free from metal chips and debris before machine power-on.",
            fontsize=11
        )

        # Page 2: Lubrication Schedule
        p2 = doc_a.new_page()
        p2.insert_text(fitz.Point(50, 72), "CHAPTER 2: SPINDLE AND AXIS LUBRICATION PROCEDURES\nPage 2", fontsize=14)
        p2.insert_text(fitz.Point(50, 140),
            "SPINDLE BEARING LUBRICATION PROCEDURE:\n"
            "1. The high-speed spindle bearings require Mobil SHC 625 synthetic synthetic oil.\n"
            "2. Lubrication frequency: Check oil reservoir level weekly; purge and replace spindle oil every 2,000 operating hours.\n"
            "3. Spindle oil delivery pressure must read between 25 PSI and 30 PSI on the manifold gauge.\n"
            "4. CAUTION: Using automotive engine oil or unapproved hydraulic fluids will void the spindle warranty and cause bearing seizure.\n\n"
            "BALL SCREW AND LINEAR GUIDE LUBRICATION:\n"
            "Apply Mobilith SHC 007 grease to the grease nipples on X, Y, and Z axes every 500 operating hours.\n"
            "Ensure the auto-lube metering valves produce an audible click during the priming cycle.",
            fontsize=11
        )

        doc_a.save(pdf_a_path)
        doc_a.close()

        # 3. Build PDF for Machine B (Hydraulic Press)
        pdf_b_path = 'media/demo_manuals/HP500_Hydraulic_Manual.pdf'
        doc_b = fitz.open()

        # Page 1: Hydraulic Press Specs
        p1_b = doc_b.new_page()
        p1_b.insert_text(fitz.Point(50, 72), "HEAVY HYDRAULIC STAMPING PRESS HP-500\nTECHNICAL SERVICE AND HYDRAULIC MANUAL\nRevision: Rev B", fontsize=16)
        p1_b.insert_text(fitz.Point(50, 150),
            "SECTION 1: HYDRAULIC CIRCUIT SPECIFICATIONS\n\n"
            "The HP-500 operates at a maximum system pressure of 350 bar (5,075 PSI).\n"
            "Main hydraulic fluid specification: ISO VG 46 anti-wear hydraulic oil.\n"
            "The primary safety relief valve is factory set to crack at 365 bar.\n"
            "Hydraulic oil temperature must be maintained between 40 deg C and 55 deg C.\n"
            "If oil temperature exceeds 65 deg C, the safety interlock will halt the press cycle automatically.",
            fontsize=11
        )

        doc_b.save(pdf_b_path)
        doc_b.close()

        # Ingest Manual A if not present
        if not Manual.objects.filter(machine=machine_a, title='VF-2SS Maintenance & Lubrication Manual').exists():
            with open(pdf_a_path, 'rb') as f:
                manual_a = Manual.objects.create(
                    machine=machine_a,
                    title='VF-2SS Maintenance & Lubrication Manual',
                    original_filename='VF2SS_Maintenance_Manual.pdf',
                    revision='2024.1',
                    uploaded_by=admin_user,
                    file=File(f, name='VF2SS_Maintenance_Manual.pdf')
                )
                self.stdout.write(f"Processing manual: {manual_a.title}...")
                process_manual(manual_a.id)

        # Ingest Manual B if not present
        if not Manual.objects.filter(machine=machine_b, title='HP-500 Hydraulic System Service Guide').exists():
            with open(pdf_b_path, 'rb') as f:
                manual_b = Manual.objects.create(
                    machine=machine_b,
                    title='HP-500 Hydraulic System Service Guide',
                    original_filename='HP500_Hydraulic_Manual.pdf',
                    revision='Rev B',
                    uploaded_by=admin_user,
                    file=File(f, name='HP500_Hydraulic_Manual.pdf')
                )
                self.stdout.write(f"Processing manual: {manual_b.title}...")
                process_manual(manual_b.id)

        self.stdout.write(self.style.SUCCESS("Demo seeding completed successfully!"))
