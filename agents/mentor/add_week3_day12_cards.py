import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "mentor.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the cards table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        card_type TEXT NOT NULL,
        repetitions INTEGER DEFAULT 0,
        ease_factor REAL DEFAULT 2.5,
        interval INTEGER DEFAULT 1
    )
""")
conn.commit()

cards = [
    (
        "What is ECONNREFUSED and what causes it?",
        "ECONNREFUSED means the connection was actively refused by the target server. Common causes: wrong host/port, firewall blocking the connection, or using an internal URL (like postgres.railway.internal) from outside the network. Fix: verify the host, port, and that you're using the public URL when connecting from outside.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is the difference between Railway's internal and public database URL?",
        "Internal URL (postgres.railway.internal:5432) only works inside Railway's private network — Railway service to Railway service. Public URL (switchback.proxy.rlwy.net:56330) works from anywhere — your laptop, Vercel, external services. Rule: use internal URL in production (faster, free), public URL for local development and external connections.",
        "CON", 0, 2.5, 1
    ),
    (
        "Why does localhost:3000 not work in production on Vercel?",
        "localhost always refers to the current machine. On Vercel, localhost:3000 points to Vercel's server, not your Railway database or local dev server. Fix: Never hardcode localhost in fetch calls. Use relative URLs (/api/patients) or query the database directly in Server Components. Environment variables handle the difference between dev and production.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is a Next.js API route and when should you use one?",
        "An API route is a file at app/api/*/route.ts that creates a backend endpoint inside your Next.js app. Use it when: external services need to call your backend, you need to hide credentials from the browser, or you want a REST API. Don't use it when a Server Component can query the database directly — that's simpler and faster.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is the correct way to store secrets in Next.js?",
        "Use .env.local for local development — Next.js reads it automatically on startup. Never commit .env.local to git (add .env* to .gitignore). For production, add environment variables in Vercel's Settings → Environment Variables panel. Access them in code with process.env.VARIABLE_NAME. Never hardcode secrets directly in source code.",
        "CON", 0, 2.5, 1
    ),
    (
        "Why must you restart the Next.js dev server after changing .env.local?",
        "Next.js reads environment variables only at startup, not dynamically. If you change .env.local while the server is running, the process still has the old values in memory. Fix: always Ctrl+C to stop, then npm run dev to restart. This is a common debugging trap — connection errors after changing credentials are often just a missing restart.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is GitGuardian and why did it detect our Railway credentials?",
        "GitGuardian is a security service that scans public GitHub repos for exposed secrets like API keys, passwords, and connection strings. It detected our Railway PostgreSQL URL because we hardcoded it directly in Python scripts that were committed to a public repo. Fix: use os.environ.get() for all credentials, add .env* to .gitignore, rotate exposed passwords immediately.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is the incident response process for exposed credentials?",
        "1. Rotate the credential immediately — invalidates the exposed secret. 2. Remove from code — replace with environment variables. 3. Clean git history — use git-filter-repo to remove from all commits. 4. Force push — git push origin main --force. 5. Verify — confirm old credential no longer works. Speed matters: rotate first, clean second.",
        "SIM", 0, 2.5, 1
    ),
    (
        "How does a Next.js Server Component query a database directly?",
        "Server Components run on the server, never in the browser, so they can safely use database credentials. Import Pool from pg, create a connection using process.env.DATABASE_URL, run your query, close the pool with pool.end(), and return the data. No API route needed. This is faster than fetch → API route → database because it eliminates one network hop.",
        "CON", 0, 2.5, 1
    ),
    (
        "INTERVIEW: Walk me through a security incident you handled.",
        "GitGuardian detected exposed Railway PostgreSQL credentials in my public GitHub repo. I immediately rotated the database password in Railway's Config panel — invalidating the exposed credentials within minutes. Then I replaced all hardcoded URLs with os.environ.get() calls, committed the fix, cleaned git history with git-filter-repo, and force pushed. Total resolution: under 30 minutes. I also added the incident to my simulation lab as a learning scenario.",
        "INT", 0, 2.5, 1
    ),
    (
        "What does ssl: rejectUnauthorized: false mean in PostgreSQL connections?",
        "This tells the pg client to accept self-signed SSL certificates without verifying them against a certificate authority. Railway uses SSL for all connections but with certificates that aren't signed by a public CA. In production with a real CA-signed cert, set rejectUnauthorized: true for better security. For Railway and most cloud databases, false is the standard setting.",
        "CON", 0, 2.5, 1
    ),
    (
        "How do you add environment variables to Vercel for production deployment?",
        "Go to Vercel → Project → Settings → Environment Variables. Add the key-value pair and select All Environments. After saving, you must redeploy — Vercel bakes environment variables into the build at deploy time, not runtime. The variable is then available via process.env.VARIABLE_NAME in your Next.js code. Never use .env.local for production — that's local development only.",
        "CON", 0, 2.5, 1
    ),
]

inserted = 0
skipped = 0

for card in cards:
    try:
        cursor.execute("""
            INSERT INTO cards (question, answer, card_type, repetitions, ease_factor, interval)
            VALUES (?, ?, ?, ?, ?, ?)
        """, card)
        inserted += 1
    except sqlite3.IntegrityError:
        skipped += 1

conn.commit()
conn.close()

print(f"✅ Day 12 cards loaded: {inserted} inserted, {skipped} skipped")
print(f"🔒 Topics: credentials security, ECONNREFUSED, API routes, env vars, Vercel deployment")
print(f"🎯 Run: python quiz.py")