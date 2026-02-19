#!/usr/bin/env python3
"""
Set up MindBridge schema on Railway PostgreSQL.
Creates patients table and inserts sample behavioral health data.
"""
import psycopg2
from datetime import datetime

# Your Railway DATABASE_PUBLIC_URL
# (Same one you used in test_railway_simple.py)
DATABASE_PUBLIC_URL = "postgresql://postgres:HwxNFHyakpIoPXoMefNdsOTLwIwMJlfP@switchback.proxy.rlwy.net:56330/railway"

def setup_mindbridge_database():
    """Create MindBridge schema and insert sample patients."""
    print("=" * 70)
    print("🏗️  Setting Up MindBridge Schema on Railway")
    print("=" * 70)
    
    if DATABASE_PUBLIC_URL == "YOUR_DATABASE_PUBLIC_URL_HERE":
        print("\n❌ ERROR: Replace the placeholder with your DATABASE_PUBLIC_URL!")
        return False
    
    try:
        print("\n🔌 Connecting to Railway...")
        conn = psycopg2.connect(DATABASE_PUBLIC_URL)
        cursor = conn.cursor()
        
        # Create patients table
        print("📋 Creating patients table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id SERIAL PRIMARY KEY,
                patient_name VARCHAR(100) NOT NULL,
                risk_level VARCHAR(20) NOT NULL,
                medication_adherence FLOAT CHECK (medication_adherence BETWEEN 0.0 AND 1.0),
                appointments_missed INT CHECK (appointments_missed >= 0),
                crisis_calls_30days INT DEFAULT 0 CHECK (crisis_calls_30days >= 0),
                diagnosis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index for performance
        print("⚡ Creating performance indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patients_risk_level 
            ON patients(risk_level);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patients_created_at 
            ON patients(created_at DESC);
        """)
        
        # Insert sample behavioral health patients
        print("👥 Inserting sample behavioral health patients...")
        sample_patients = [
            ('Marcus Johnson', 'HIGH', 0.3, 4, 2, 'Major Depressive Disorder, recurrent'),
            ('Sarah Williams', 'MEDIUM', 0.7, 1, 0, 'Generalized Anxiety Disorder'),
            ('James Brown', 'LOW', 0.9, 0, 0, 'Adjustment Disorder with anxiety'),
            ('Emily Davis', 'HIGH', 0.4, 3, 1, 'Bipolar I Disorder, current episode depressed'),
            ('Michael Chen', 'MEDIUM', 0.6, 2, 0, 'Post-Traumatic Stress Disorder'),
            ('Jessica Martinez', 'LOW', 0.85, 1, 0, 'Major Depressive Disorder, single episode'),
            ('David Wilson', 'HIGH', 0.25, 5, 3, 'Schizoaffective Disorder, bipolar type'),
            ('Ashley Taylor', 'MEDIUM', 0.75, 1, 0, 'Persistent Depressive Disorder'),
            ('Christopher Lee', 'LOW', 0.95, 0, 0, 'Social Anxiety Disorder'),
            ('Amanda Garcia', 'HIGH', 0.35, 4, 2, 'Borderline Personality Disorder'),
        ]
        
        cursor.executemany("""
            INSERT INTO patients 
            (patient_name, risk_level, medication_adherence, 
             appointments_missed, crisis_calls_30days, diagnosis)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, sample_patients)
        
        conn.commit()
        
        # Verify and display summary
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patients WHERE risk_level = 'HIGH'")
        high_risk = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patients WHERE risk_level = 'MEDIUM'")
        medium_risk = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patients WHERE risk_level = 'LOW'")
        low_risk = cursor.fetchone()[0]
        
        print(f"\n✅ MindBridge schema created successfully!")
        print(f"📊 Sample patients inserted: {total_count}")
        print(f"☁️  Database: Railway PostgreSQL (Production)")
        
        print("\n" + "=" * 70)
        print("PATIENT RISK DISTRIBUTION")
        print("=" * 70)
        print(f"🔴 HIGH RISK:   {high_risk} patients (require immediate review)")
        print(f"🟡 MEDIUM RISK: {medium_risk} patients (monitor closely)")
        print(f"🟢 LOW RISK:    {low_risk} patients (routine care)")
        print(f"📊 TOTAL:       {total_count} patients in Railway database")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ MINDBRIDGE SCHEMA DEPLOYED TO PRODUCTION!")
        print("=" * 70)
        print("\n🎯 Next Step: Generate risk assessment reports from Railway")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed!")
        print(f"Error: {e}\n")
        print("Troubleshooting:")
        print("1. Verify DATABASE_PUBLIC_URL is correct")
        print("2. Check Railway shows 'Online' status")
        print("3. Make sure connection test worked previously")
        return False

if __name__ == "__main__":
    setup_mindbridge_database()
