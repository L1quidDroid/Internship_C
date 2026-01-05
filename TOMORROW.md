# Tomorrow's TL VM Deployment Checklist

## 🚀 Startup Verification (5 minutes)

### Step 1: Pull & Prepare
```bash
cd /path/to/caldera
git pull origin develop
pip install -r requirements.txt
```

### Step 2: Run Sanity Check
```bash
./verify_sanity.sh
```
**Expected**: All 4 checks pass (compile, imports, files, dependencies)

### Step 3: Start Server & Monitor
```bash
python3 server.py --insecure
```

**Watch for these 7 plugin load messages:**
```
✅ Orchestrator plugin enabled successfully
✅ Reporting plugin: REST API registered
✅ Branding plugin enabled
✅ Sandcat plugin enabled
✅ Stockpile plugin enabled
✅ Atomic plugin enabled
✅ Magma plugin enabled
```

---

## 🎯 Golden Operation Test (10 minutes)

### Operation: "Purple Team Discovery Test"

**Purpose**: Validates full orchestrator → reporting → branding pipeline

**Setup:**
1. Navigate to: http://localhost:8888
2. Login: `red` / `ADMIN123`
3. Create Agent:
   - Agents tab → Deploy → Copy sandcat one-liner
   - Run in terminal (local test) or RDP into client VM
   - Wait for agent to appear

**Run Operation:**
1. Operations tab → Create new operation:
   - **Name**: `Purple Team Discovery Test`
   - **Group**: Select your agent
   - **Adversary**: `Hunter` (from stockpile)
   - **Planner**: `atomic`
   - **Jitter**: `2/8`
   - **Auto-close**: Enabled

2. Click **Start**

3. Wait for operation to complete (~2 minutes)

**Verify 3 Things:**

| Check | What to Look For | Location |
|-------|------------------|----------|
| 1️⃣ **Orchestrator Logs** | `[orchestrator] Operation finished: ...`<br>`[orchestrator] Triggering report generation...` | Terminal logs |
| 2️⃣ **PDF Report** | File exists: `plugins/reporting/data/reports/Purple_Team_Discovery_Test_<timestamp>.pdf`<br>Opens without errors | File system |
| 3️⃣ **Branding** | PDF shows Triskele logo (top)<br>Uses colors: Blue #0f3460, Teal #16a085<br>Company name: "Triskele Labs" | Open PDF |

---

## 🐛 Troubleshooting

### If plugins don't load:
```bash
# Check for import errors
python3 -c "from plugins.orchestrator.app.orchestrator_svc import OrchestratorService"
python3 -c "from plugins.reporting.app.report_svc import ReportService"
```

### If ELK tagging fails:
```bash
# Check .env file exists with:
ELK_URL=http://localhost:9200
ELK_INDEX=purple-team-logs
ELK_API_KEY=<your-key>
```

### If PDF not generated:
```bash
# Check reporting service loaded
grep "report_svc" logs/caldera.log

# Check orchestrator called reporting
grep "Triggering report generation" logs/caldera.log

# Check disk space
df -h /
```

### If branding broken:
```bash
# Verify static files accessible
curl http://localhost:8888/branding/static/css/triskele.css
curl http://localhost:8888/branding/static/img/triskele_logo.svg
```

---

## 📊 Success Criteria

✅ **Production-ready if:**
- All 7 plugins load without errors
- Golden operation completes successfully
- PDF generated automatically within 10 seconds
- PDF contains Triskele branding
- No stack traces in logs (warnings OK)

❌ **Block deployment if:**
- Any plugin fails to load
- PDF not generated or malformed
- Branding missing from PDF
- Operation hangs or crashes server

---

## 🔧 Quick Fixes

### Missing python-dotenv:
```bash
pip install python-dotenv
```

### Missing Elasticsearch:
```bash
pip install elasticsearch
```

### Permissions error on report directory:
```bash
chmod 777 plugins/reporting/data/reports/
```

---

## 📝 Demo Day Talking Points

When showing to Tahsinur (supervisor):

1. **"We automated the entire purple team workflow"**
   - Show agent enrollment (no RDP needed)
   - Run operation with 1 click
   - PDF appears automatically

2. **"Attack metadata flows to SIEM automatically"**
   - Show orchestrator logs tagging events
   - (If ELK available) Show purple_team_exercise tags in Kibana

3. **"Reports are client-ready out of the box"**
   - Open PDF
   - Point out Triskele branding
   - Show executive summary, tactic coverage, technique details

4. **"Built for MSP scale"**
   - Mention 6x throughput improvement (5 manual → 30+ automated)
   - RAM-optimized (7.7GB VM runs fine)
   - All documentation stripped for production deployment

---

## 🎓 For Next Intern

If you're taking over this project:

1. Read the audit report in git history (commit `<hash>`)
2. Run `./verify_sanity.sh` to ensure baseline works
3. Golden operation is your smoke test - run it first
4. All custom code is in 3 plugins: orchestrator, reporting, branding
5. Everything else is stock MITRE Caldera (don't modify)

**Key files:**
- [plugins/orchestrator/app/orchestrator_svc.py](plugins/orchestrator/app/orchestrator_svc.py) - Event handlers
- [plugins/reporting/app/pdf_generator.py](plugins/reporting/app/pdf_generator.py) - PDF rendering
- [plugins/branding/static/css/triskele.css](plugins/branding/static/css/triskele.css) - UI styling

Good luck! 🚀
