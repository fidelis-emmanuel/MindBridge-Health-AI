#!/usr/bin/env python3
"""
Test connection to Railway PostgreSQL using DATABASE_PUBLIC_URL.
This is the EASIER method - just copy one value!
"""
import psycopg2
from datetime import datetime

# Copy your DATABASE_PUBLIC_URL from Railway
# Click the eye icon next to DATABASE_PUBLIC_URL and paste the ENTIRE string here
DATABASE_PUBLIC_URL = "postgresql://postgres:HwxNFHyakpIoPXoMefNdsOTLwIwMJlfP@switchback.proxy.rlwy.net:56330/railway"

# Example of what it looks like (yours will be different):
# postgresql://postgres:AbCd1234XyZ@monorail.proxy.rlwy.net:12345/railway

def test_railway_connection():
    """Test connection to Railway PostgreSQL."""
    print("=" * 70)
    print("☁️  Testing Railway PostgreSQL Connection")
    print("=" * 70)
    
    # Validate URL was provided
    if DATABASE_PUBLIC_URL == "":
        print("\n❌ ERROR: You need to replace the placeholder!")
        print("\nSteps:")
        print("1. Go to Railway → Variables tab")
        print("2. Find DATABASE_PUBLIC_URL")
        print("3. Click the eye icon (👁️) to reveal it")
        print("4. Copy the ENTIRE string")
        print("5. Paste it in this file replacing ''")
        print("\nIt should start with: postgresql://postgres:...")
        return False
    
    try:
        # Connect using the full URL
        print("\n🔌 Attempting connection...")
        conn = psycopg2.connect(DATABASE_PUBLIC_URL)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Extract connection info from URL for display
        # Format: postgresql://user:password@host:port/database
        parts = DATABASE_PUBLIC_URL.replace("postgresql://", "").split("@")
        host_port_db = parts[1] if len(parts) > 1 else "unknown"
        host = host_port_db.split(":")[0] if ":" in host_port_db else "unknown"
        
        print(f"\n✅ CONNECTION SUCCESSFUL!")
        print(f"📊 PostgreSQL version: {version[:60]}...")
        print(f"🌐 Host: {host}")
        print(f"☁️  Location: Railway Cloud (Production)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ RAILWAY DATABASE IS LIVE AND ACCESSIBLE!")
        print("=" * 70)
        print("\n🎯 Interview-Ready Statement:")
        print("'I deployed PostgreSQL to Railway and connected from my")
        print(" local development environment to the production database.'")
        print("\n💼 Salary Impact: +$15K-$20K in negotiations")
        print("=" * 70 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"Error: {e}\n")
        print("Troubleshooting:")
        print("1. Make sure you copied the ENTIRE DATABASE_PUBLIC_URL")
        print("2. It should start with: postgresql://postgres:")
        print("3. It should contain .proxy.rlwy.net in the middle")
        print("4. Check Railway shows 'Online' status")
        print("5. Verify psycopg2 is installed:")
        print("   pip install psycopg2-binary --break-system-packages")
        return False

if __name__ == "__main__":
    test_railway_connection()