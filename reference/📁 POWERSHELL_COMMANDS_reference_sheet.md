📁 POWERSHELL COMMANDS - COPY AND RUN
powershell# Navigate to your project root
cd "E:\Mindbridge health care"

# Create Week 1 structure
New-Item -ItemType Directory -Path ".\.claude\week1\conversations" -Force
New-Item -ItemType Directory -Path ".\.claude\week1\summaries" -Force
New-Item -ItemType Directory -Path ".\.claude\week1\resources" -Force

# Create Week 2 structure
New-Item -ItemType Directory -Path ".\.claude\week2\conversations" -Force
New-Item -ItemType Directory -Path ".\.claude\week2\summaries" -Force
New-Item -ItemType Directory -Path ".\.claude\week2\resources" -Force

# Create Week 3 structure
New-Item -ItemType Directory -Path ".\.claude\week3\conversations" -Force
New-Item -ItemType Directory -Path ".\.claude\week3\summaries" -Force
New-Item -ItemType Directory -Path ".\.claude\week3\frontend-resources" -Force
New-Item -ItemType Directory -Path ".\.claude\week3\nextjs-learning\component-examples" -Force

# Create placeholder files for Week 2
New-Item -ItemType File -Path ".\.claude\week2\conversations\day9-railway-deployment.txt" -Force
New-Item -ItemType File -Path ".\.claude\week2\summaries\WEEK_2_COMPLETE_SUMMARY.md" -Force
New-Item -ItemType File -Path ".\.claude\week2\resources\simulation_lab_expansion.md" -Force

# Create placeholder file for Week 3
New-Item -ItemType File -Path ".\.claude\week3\frontend-resources\nextjs-basics.md" -Force

Write-Host "✅ Claude folder structure created!" -ForegroundColor Green
Write-Host "📁 Location: E:\Mindbridge health care\.claude" -ForegroundColor Cyan
```

---

## **🎯 WHAT THIS DOES**

**Creates folders:**
```
.claude\
├── week1\
│   ├── conversations\
│   ├── summaries\
│   └── resources\
├── week2\
│   ├── conversations\
│   ├── summaries\
│   └── resources\
└── week3\
    ├── conversations\
    ├── summaries\
    ├── frontend-resources\
    └── nextjs-learning\
        └── component-examples\
Creates placeholder files:

.claude\week2\conversations\day9-railway-deployment.txt
.claude\week2\summaries\WEEK_2_COMPLETE_SUMMARY.md
.claude\week2\resources\simulation_lab_expansion.md
.claude\week3\frontend-resources\nextjs-basics.md

KEEPS everything else:

✅ All your existing folders (agents, backend, docs, etc.)
✅ All your existing files
✅ Nothing is deleted or moved

The -Force flag means:

If folder exists, it won't fail
If folder doesn't exist, it creates it
Safe to run multiple times


✅ VERIFICATION
After running, check with:
powershell# See the new structure
tree ".\.claude" /F

# Or just navigate and look
explorer ".\.claude"
```

---

## **📋 YOUR COMPLETE STRUCTURE AFTER THIS**
```
E:\Mindbridge health care\
├── .claude\              ← NEW organized learning structure
│   ├── week1\
│   ├── week2\
│   └── week3\
├── .git\                 ← KEPT (version control)
├── agents\               ← KEPT (mentor system)
├── backend\              ← KEPT (FastAPI app)
├── data\                 ← KEPT
├── database\             ← KEPT (migrations)
├── docs\                 ← KEPT (all documentation)
├── files\                ← KEPT
├── frontend\             ← KEPT (demos, simulation lab)
├── infrastructure\       ← KEPT
├── logs\                 ← KEPT (application logs)
├── Mentor files\         ← KEPT
├── portfolio\            ← KEPT (interview materials)
├── reference\            ← KEPT (learning resources)
├── reports\              ← KEPT (generated reports)
├── scripts\              ← KEPT (all automation scripts)
├── .dockerignore         ← KEPT
├── .env.example          ← KEPT
├── .gitignore            ← KEPT
├── docker-compose.yml    ← KEPT
└── README.md             ← KEPT
Perfect separation:

Project files: Root directory (production code)
Learning files: .claude/ directory (organized by week)