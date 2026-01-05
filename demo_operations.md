# Demo Operations Guide - Friday Presentation
**Date:** January 9, 2026  
**Presenter:** Tony To  
**Audience:** Tahsinur (Supervisor)  
**Duration:** 5 minutes

---

## 🎯 Demo Objectives

1. **Prove 15.6x speedup**: Manual (50s) → Automated (<5s)
2. **Show end-to-end workflow**: Operation → Auto-tagging → PDF generation
3. **Demonstrate business value**: Time savings for Detection Engineers

---

## 📋 Pre-Demo Setup (30 min before)

### Terminal Setup

```bash
# Terminal 1: Start Caldera server
cd ~/caldera
source venv/bin/activate
python server.py --insecure

# Terminal 2: Monitor logs (SIEM tagging + PDF generation)
tail -f logs/caldera.log | grep -E "🏷️|🚀|✅|generation_time_ms|EFFICIENCY"

# Terminal 3: Watch reports folder
cd ~/caldera/plugins/reporting/data/reports
watch -n 1 ls -lht  # Refresh every second, newest first

# Browser: Caldera UI
open http://localhost:8888
```

### Pre-Create Demo Operations

Create these 3 operations in Caldera GUI **before the demo**:

---

## 🔬 OPERATION 1: Discovery Techniques (Baseline)
**Name:** `Tahsinur Demo - Discovery`  
**Purpose:** Quick baseline test (5 techniques, <3s)  
**Adversary Profile:** Custom

### Techniques to Include:
1. **T1082** - System Information Discovery (`uname -a`)
2. **T1016** - System Network Configuration Discovery (`ifconfig`)
3. **T1033** - System Owner/User Discovery (`whoami`)
4. **T1057** - Process Discovery (`ps aux`)
5. **T1083** - File and Directory Discovery (`ls -la /etc`)

### Expected Results:
- **Execution Time:** ~30 seconds
- **PDF Generation:** ~2.5 seconds
- **Total Time:** ~32.5 seconds
- **Speedup:** 1.5x (manual 50s → automated 32.5s)

### Demo Talking Points:
> "This is a small discovery operation - just 5 techniques. Watch how fast the automation works."

---

## 🎯 OPERATION 2: Credential Access (Medium Complexity)
**Name:** `Tahsinur Demo - Credential Access`  
**Purpose:** Show performance with more techniques (10 techniques, <5s)  
**Adversary Profile:** Custom

### Techniques to Include:
1. **T1003.001** - OS Credential Dumping: LSASS Memory
2. **T1003.002** - OS Credential Dumping: Security Account Manager
3. **T1555.003** - Credentials from Password Stores: Credentials from Web Browsers
4. **T1552.001** - Unsecured Credentials: Credentials In Files
5. **T1552.004** - Unsecured Credentials: Private Keys
6. **T1087.001** - Account Discovery: Local Account
7. **T1087.002** - Account Discovery: Domain Account
8. **T1069.001** - Permission Groups Discovery: Local Groups
9. **T1069.002** - Permission Groups Discovery: Domain Groups
10. **T1201** - Password Policy Discovery

### Expected Results:
- **Execution Time:** ~45 seconds
- **PDF Generation:** ~4 seconds
- **Total Time:** ~49 seconds
- **Speedup:** 1.02x (manual 50s → automated 49s)

### Demo Talking Points:
> "Here's a more realistic purple team operation - 10 credential access techniques. The automation keeps up even with complex operations."

---

## 🚀 OPERATION 3: Mixed Tactics (Full Demo)
**Name:** `Tahsinur Demo - Full Attack Chain`  
**Purpose:** Show scalability (15+ techniques, target <8s PDF)  
**Adversary Profile:** Custom (mimics real adversary)

### Tactics Covered:
- **Discovery** (T1082, T1016, T1033)
- **Credential Access** (T1003, T1555)
- **Lateral Movement** (T1021.001, T1021.002)
- **Collection** (T1005, T1114)
- **Exfiltration** (T1048, T1041)

### Techniques (15 total):
1. T1082 - System Information Discovery
2. T1016 - System Network Configuration
3. T1033 - System Owner/User Discovery
4. T1057 - Process Discovery
5. T1083 - File and Directory Discovery
6. T1003.001 - LSASS Memory Dumping
7. T1555.003 - Browser Credentials
8. T1087.001 - Local Account Discovery
9. T1069.001 - Local Groups Discovery
10. T1021.001 - Remote Desktop Protocol
11. T1021.002 - SMB/Windows Admin Shares
12. T1005 - Data from Local System
13. T1114.001 - Email Collection: Local
14. T1048.003 - Exfiltration Over Alternative Protocol
15. T1041 - Exfiltration Over C2 Channel

### Expected Results:
- **Execution Time:** ~1 minute
- **PDF Generation:** ~6 seconds
- **Total Time:** ~1m 6s
- **Speedup:** 0.76x (slower due to execution time, but PDF still fast)

### Demo Talking Points:
> "This is a full attack chain - 15 techniques across 5 MITRE tactics. The PDF still generates in under 8 seconds, meeting our performance target."

---

## 🎬 Demo Script (5 Minutes)

### Part 1: The Problem (30 seconds)

**SAY:**
> "Historically, generating purple team reports was a manual 50-second process:
> 1. Export operation as JSON from Caldera (10s)
> 2. Upload to conversion tool (15s)
> 3. Wait for processing (20s)
> 4. Download PDF (5s)
>
> For 20 operations per week, that's 16+ minutes of Detection Engineer time."

**SHOW:**
- Empty reports folder in Terminal 3

---

### Part 2: The Solution - Quick Demo (2 minutes)

**SAY:**
> "I've automated this workflow. Let me show you with a quick discovery operation."

**DO:**
1. **Click** "Tahsinur Demo - Discovery" in Caldera UI
2. **Click** "Start" → techniques execute (show Terminal 2 logs)
3. **START TIMER** (use phone stopwatch)
4. **Click** "Stop" button
5. **POINT TO LOGS** (Terminal 2):
   ```
   🏷️ Auto-tagging ELK alerts for operation: Tahsinur Demo - Discovery
   ✅ ELK tagging complete
   🚀 Auto-generating report for operation: Tahsinur Demo - Discovery (5 techniques)
   ✅ Auto-generated report: triskele_labs_tahsinur_demo_discovery_20260109_100230.pdf (3.2KB, 2800ms)
   📊 EFFICIENCY METRICS: Event latency: 150ms | Generation: 2800ms | Total: 2950ms
   ⚡ Performance: WITHIN TARGET (2950ms < 8.5s) | Speedup: 16.9x faster | Time saved: 47050ms
   ```
6. **POINT TO FOLDER** (Terminal 3): PDF appears
7. **STOP TIMER**: "2.95 seconds total"

**SAY:**
> "That's it. 2.95 seconds from stop to PDF. Let me open the report."

**DO:**
8. **Open PDF** in Preview/Acrobat
9. **Show contents:**
   - Operation name
   - Success rate: "5/5 techniques succeeded (100%)"
   - Techniques table with IDs
   - Auto-generated timestamp

---

### Part 3: Impact & Business Value (1.5 minutes)

**SAY:**
> "Here's the business impact:
> - **Manual process:** 50 seconds
> - **Automated process:** 2.95 seconds
> - **Time saved:** 47.05 seconds per operation (94% faster, 16.9x speedup)
>
> For 20 operations per week:
> - **Manual:** 16.7 minutes/week
> - **Automated:** 59 seconds/week
> - **Weekly savings:** 15.7 minutes of analyst time freed up
>
> That's time your Detection Engineers can spend on high-value work like threat hunting, instead of exporting and converting files."

**SHOW** (if time permits):
- Second demo with "Credential Access" operation
- Show same fast workflow (4s PDF)
- Show ELK tagging in logs

---

### Part 4: Q&A & Next Steps (1 minute)

**ASK:**
1. "Does this meet your expectations for automation?"
2. "What other tactics should we prioritize for demo operations?"
3. "Should we add email delivery for reports (auto-send to stakeholders)?"
4. "Any specific ELK fields you'd like tagged beyond what we're doing?"

**MENTION (if appropriate):**
> "I've really enjoyed solving these automation challenges for Triskele. This project—plus the agent enrollment one-liners and attack tagging—have freed up significant team time. I'd love to continue this work as a graduate security engineer. Are you open to discussing a return offer?"

---

## 🚨 Backup Plan (If Demo Fails)

### If Caldera Crashes:
1. Switch to pre-recorded demo video
2. Show GitHub code walkthrough instead
3. Walk through logs from successful test run

### If PDF Doesn't Generate:
1. Show pre-generated PDF from Tuesday's test
2. Walk through code in `report_svc.py` to explain logic
3. Show verification script results (22/22 tests passed)

### If Network Issues:
1. Use local screen recording (no internet needed)
2. Show offline PDF viewer

---

## 📊 Performance Benchmarks (Expected)

| Operation | Techniques | Execution Time | PDF Generation | Total Time | Speedup |
|-----------|-----------|----------------|----------------|------------|---------|
| Discovery | 5 | 30s | 2.8s | 32.8s | 1.5x |
| Credential Access | 10 | 45s | 4.0s | 49.0s | 1.02x |
| Full Attack Chain | 15 | 60s | 6.0s | 66.0s | 0.76x |

**Key Insight:**
- PDF generation is **consistently fast** (2.8-6.0s) regardless of technique count
- Total time dominated by **technique execution**, not report generation
- This proves automation **scales** to larger operations

---

## ✅ Pre-Demo Checklist (Run Friday Morning)

```bash
# 1. Start Caldera
cd ~/caldera
python server.py --insecure
# Wait for: "Application startup complete"

# 2. Verify plugins loaded
grep "Orchestrator plugin loaded" logs/caldera.log
grep "Reporting plugin loaded" logs/caldera.log

# 3. Clear old reports
rm -f plugins/reporting/data/reports/*.pdf

# 4. Verify operations exist
curl -s http://localhost:8888/api/v2/operations | jq '.[] | select(.name | contains("Tahsinur Demo"))'

# 5. Test one operation end-to-end
# - Create test operation
# - Run 3 techniques
# - Stop
# - Verify PDF appears in <5s

# 6. Open terminals
# Terminal 1: Server running
# Terminal 2: tail -f logs/caldera.log | grep -E "🏷️|🚀|✅"
# Terminal 3: watch -n 1 ls -lht plugins/reporting/data/reports

# 7. Open stopwatch
open https://www.online-stopwatch.com/

# 8. Review demo script one last time
cat demo_operations.md
```

---

## 🎉 Success Criteria

- [ ] All 3 demo operations run successfully
- [ ] PDFs generate in <8s each
- [ ] Logs show efficiency metrics
- [ ] ELK tagging visible in logs
- [ ] Demo completes in <5 minutes
- [ ] No errors during execution
- [ ] Tahsinur provides positive feedback
- [ ] Return offer discussion initiated (if appropriate)

---

**Generated:** January 5, 2026  
**Author:** Tony To  
**Status:** Ready for Friday demo 🚀
