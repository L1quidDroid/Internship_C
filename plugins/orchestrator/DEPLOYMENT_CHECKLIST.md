# Orchestrator Plugin - Pre-Deployment Checklist

## Local Testing ✅

- [x] **Unit tests pass**
  ```bash
  cd /Users/tonyto/Documents/GitHub/Triskele\ Labs/Internship_C
  PYTHONPATH="." python3 plugins/orchestrator/test_event_handler.py
  ```
  Result: ✅ ALL TESTS PASSED

- [x] **No Python syntax errors**
  ```bash
  python3 -m py_compile plugins/orchestrator/app/orchestrator_svc.py
  ```
  Result: ✅ No errors

- [x] **Code changes documented**
  - [x] FIX_SUMMARY.md created
  - [x] TROUBLESHOOTING.md created
  - [x] deploy_and_verify.sh created
  - [x] test_event_handler.py created

## Files Ready for Commit

- [x] `plugins/orchestrator/app/orchestrator_svc.py` - **Main fix**
- [x] `plugins/orchestrator/test_event_handler.py` - Unit tests
- [x] `plugins/orchestrator/deploy_and_verify.sh` - Deployment script
- [x] `plugins/orchestrator/TROUBLESHOOTING.md` - Debug guide
- [x] `plugins/orchestrator/FIX_SUMMARY.md` - Implementation summary
- [x] `plugins/orchestrator/DEPLOYMENT_CHECKLIST.md` - This file

## Git Commit Checklist

```bash
cd "/Users/tonyto/Documents/GitHub/Triskele Labs/Internship_C"

# 1. Review changes
git status
git diff plugins/orchestrator/app/orchestrator_svc.py

# 2. Stage files
git add plugins/orchestrator/app/orchestrator_svc.py
git add plugins/orchestrator/test_event_handler.py
git add plugins/orchestrator/deploy_and_verify.sh
git add plugins/orchestrator/TROUBLESHOOTING.md
git add plugins/orchestrator/FIX_SUMMARY.md
git add plugins/orchestrator/DEPLOYMENT_CHECKLIST.md

# 3. Commit with detailed message
git commit -m "Fix orchestrator event handler signatures for ELK tagging

Problem:
- Orchestrator plugin was not tagging Elasticsearch documents
- Event handlers were never triggered properly
- Operations completed successfully but no purple.* fields appeared in ELK

Root Cause:
- Event handlers had incorrect function signatures
- Expected (op=None, **kwargs) but received (socket, path, services)
- Handlers need to read JSON from websocket, not receive pre-parsed data

Solution:
- Updated on_operation_completed and on_operation_state_changed signatures
- Added websocket message reading: await socket.recv()
- Added JSON parsing: json.loads(message_data)
- Changed data_svc access from self.data_svc to services.get('data_svc')

Testing:
- Unit tests verify handlers parse websocket messages correctly
- All tests pass locally (test_event_handler.py)

Files Modified:
- orchestrator_svc.py: Fixed event handler signatures and implementation
- test_event_handler.py: Comprehensive unit tests for event handlers
- deploy_and_verify.sh: Automated deployment and testing script
- TROUBLESHOOTING.md: Complete debugging guide for future issues
- FIX_SUMMARY.md: Detailed implementation documentation

Deployment Instructions:
See plugins/orchestrator/FIX_SUMMARY.md for complete deployment guide

Testing Checklist:
1. Plugin loads: curl http://localhost:8888/plugin/orchestrator/status
2. Manual tag test: curl -X POST http://localhost:8888/plugin/orchestrator/tag-test
3. Run Caldera operation with Discovery adversary
4. Check logs: tail -f caldera.log | grep orchestrator
5. Query ELK: curl http://20.28.49.97:9200/winlogbeat-*/_search
6. Verify purple.* fields and tags appear in Elasticsearch
7. Confirm tags visible in Kibana Discover

Related Issue: Orchestrator plugin tagging failure
Impact: High - Core purple team automation feature now functional
Risk: Low - Backwards compatible, only affects event handler internals"

# 4. Verify commit
git log -1 --stat

# 5. Push to remote (when ready)
# git push origin main
```

## On-Site Deployment Checklist (Ubuntu VM)

### Pre-Deployment

- [ ] **SSH access confirmed**
  ```bash
  ssh user@20.28.49.97
  ```

- [ ] **Locate Caldera installation**
  ```bash
  find /opt /home /var -name "server.py" 2>/dev/null | grep caldera
  ```

- [ ] **Check current Caldera version**
  ```bash
  cd /path/to/caldera
  git log -1 --oneline
  ```

- [ ] **Verify Elasticsearch is running**
  ```bash
  curl http://localhost:9200/_cluster/health
  # or
  curl http://20.28.49.97:9200/_cluster/health
  ```

- [ ] **Check current ELK credentials**
  ```bash
  env | grep -i elk
  # or check conf/local.yml
  ```

### Deployment Steps

- [ ] **1. Pull latest code**
  ```bash
  cd /path/to/caldera
  git pull origin main
  ```

- [ ] **2. Verify files updated**
  ```bash
  git log -1 --stat
  ls -lh plugins/orchestrator/app/orchestrator_svc.py
  ```

- [ ] **3. Set ELK environment variables (if needed)**
  ```bash
  export ELK_URL="http://20.28.49.97:9200"
  export ELK_USER="elastic"
  export ELK_PASS="<password>"
  
  # Make persistent (optional)
  echo 'export ELK_URL="http://20.28.49.97:9200"' >> ~/.bashrc
  echo 'export ELK_USER="elastic"' >> ~/.bashrc
  echo 'export ELK_PASS="<password>"' >> ~/.bashrc
  ```

- [ ] **4. Stop Caldera**
  ```bash
  # Option A: Systemd service
  sudo systemctl stop caldera
  
  # Option B: Manual process
  pkill -f "python.*server.py"
  
  # Verify stopped
  ps aux | grep server.py
  ```

- [ ] **5. Start Caldera**
  ```bash
  # Option A: Systemd service
  sudo systemctl start caldera
  
  # Option B: Manual start
  cd /path/to/caldera
  nohup python3 server.py --insecure > caldera.log 2>&1 &
  
  # Capture PID
  echo $! > caldera.pid
  ```

- [ ] **6. Wait for startup (30-60 seconds)**
  ```bash
  sleep 30
  tail -f caldera.log
  # Look for: "All systems ready."
  ```

### Post-Deployment Verification

- [ ] **7. Check plugin status**
  ```bash
  curl http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool
  ```
  Expected: `"status": "running"`, `"elk.status": "connected"`

- [ ] **8. Test manual tagging**
  ```bash
  curl -X POST http://localhost:8888/plugin/orchestrator/tag-test | python3 -m json.tool
  ```
  Expected: `"status": "success"`

- [ ] **9. Verify Elasticsearch received tag**
  ```bash
  # Wait 2 seconds for indexing
  sleep 2
  
  curl -X GET "http://localhost:9200/purple-team-logs/_search?pretty" \
    -H 'Content-Type: application/json' \
    -d '{"query": {"term": {"tags": "purple_team"}}, "size": 1}'
  ```
  Expected: At least 1 hit

### End-to-End Test

- [ ] **10. Run Caldera operation**
  1. Open UI: `http://20.28.49.97:8888`
  2. Login with admin credentials
  3. Navigate to Operations
  4. Create new operation:
     - Name: `orchestrator-test-<timestamp>`
     - Adversary: `Discovery`
     - Agent: Select Windows Sandcat agent
     - Planner: `atomic`
  5. Click "Start"
  6. Wait for completion (2-5 minutes)

- [ ] **11. Monitor event handler logs**
  ```bash
  tail -f caldera.log | grep -i orchestrator
  ```
  Expected within 60s of operation completion:
  ```
  [orchestrator] State change: abc123... (running → finished)
  [orchestrator] Operation finished: abc123... (state: finished)
  ELK tagged operation: abc123... (doc ID: xyz789)
  ```

- [ ] **12. Get operation UUID**
  - From Caldera UI (Operation details)
  - Or from logs: grep the operation ID from handler messages

- [ ] **13. Query Elasticsearch for tags**
  ```bash
  OP_ID="<paste-operation-uuid-here>"
  
  curl -X GET "http://20.28.49.97:9200/winlogbeat-*/_search?pretty" \
    -H 'Content-Type: application/json' \
    -d "{
      \"query\": {
        \"term\": {
          \"purple.operation_id\": \"$OP_ID\"
        }
      },
      \"size\": 5
    }"
  ```
  Expected: Multiple hits with `purple.*` fields

- [ ] **14. Verify purple.* metadata**
  Check response contains:
  ```json
  {
    "_source": {
      "purple": {
        "operation_id": "<uuid>",
        "technique": "T1033",
        "techniques": ["T1033", "T1087.001", "T1135", ...],
        "tactic": "discovery",
        "operation_name": "orchestrator-test-..."
      },
      "tags": ["purple_team", "caldera", "purple_T1033", ...]
    }
  }
  ```

- [ ] **15. Verify in Kibana**
  1. Open: `http://20.28.49.97:5601`
  2. Go to: Discover
  3. Index pattern: `winlogbeat-*`
  4. Filter: `tags: purple_team`
  5. Time range: Last 1 hour
  6. Expected: Sysmon events with purple team metadata visible

### Troubleshooting (If Issues Occur)

- [ ] **Review logs**
  ```bash
  tail -100 caldera.log | grep -i "error\|exception\|traceback"
  ```

- [ ] **Check fallback logs**
  ```bash
  ls -lh plugins/orchestrator/data/fallback_logs/
  cat plugins/orchestrator/data/fallback_logs/*.json
  ```
  If fallback logs exist → ELK connectivity issue

- [ ] **Run diagnostic script**
  ```bash
  bash plugins/orchestrator/deploy_and_verify.sh > diagnostic.log 2>&1
  cat diagnostic.log
  ```

- [ ] **Consult troubleshooting guide**
  ```bash
  less plugins/orchestrator/TROUBLESHOOTING.md
  ```

## Success Criteria

All of the following must be true:

- [x] Local unit tests pass
- [ ] Plugin loads without errors on VM
- [ ] Plugin status shows ELK connected
- [ ] Manual tagging API returns success
- [ ] Elasticsearch receives manual test tag
- [ ] Operation completion triggers event handlers
- [ ] Event handler logs appear in caldera.log
- [ ] Elasticsearch contains purple.* fields for operation
- [ ] Kibana can filter and display purple_team tags
- [ ] Detection engineer can filter SIEM logs by technique ID

## Documentation Delivered

- [x] Implementation summary (FIX_SUMMARY.md)
- [x] Troubleshooting guide (TROUBLESHOOTING.md)
- [x] Deployment script (deploy_and_verify.sh)
- [x] Unit test suite (test_event_handler.py)
- [x] This deployment checklist (DEPLOYMENT_CHECKLIST.md)

## Sign-Off

**Developer:** Tony To  
**Date Implemented:** January 10, 2026  
**Local Testing:** ✅ Complete  
**On-Site Deployment:** ⏳ Pending (awaiting lab access)  
**Production Verification:** ⏳ Pending (after deployment)

---

## Notes

- Bug was caused by incorrect event handler signature (websocket vs parsed args)
- Fix is backwards compatible - only changes internal implementation
- No database migrations or schema changes required
- Safe to deploy without downtime risk
- Can rollback by reverting commit if issues occur

## Next Steps After Deployment

1. Monitor first 3 operations closely
2. Collect sample tagged documents for demo
3. Create user training materials for detection engineers
4. Document expected ELK query patterns for purple team analysis
5. Set up Kibana dashboard templates for purple team exercises
