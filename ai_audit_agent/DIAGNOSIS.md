# 🔍 Diagnosis: "Bad Request" Error

## ✅ What's Working

1. **API is running** ✅
   - You can reach `http://10.246.184.25:8000`
   
2. **Endpoint exists** ✅
   - GET shows "Method Not Allowed" (expected - endpoint only accepts POST)

3. **Data is valid** ✅
   - All required fields filled
   - Email format correct
   - All 9 departments present

4. **Apps Script is working** ✅
   - Can connect to API
   - Validation passes
   - Sending POST request

## ❓ What's the Issue?

The "Bad request" error is **not showing the actual error details**. We need to see what the API is actually rejecting.

---

## 🧪 Diagnostic Steps

### Step 1: Check API Logs

**If using Docker:**
```bash
docker-compose logs -f
```

**If running directly:**
```bash
# Logs appear in terminal where you ran python main.py
```

**Look for:**
- Did the API receive the POST request?
- What error is it returning?
- Is there a validation error?

---

### Step 2: Test from Your Machine

Run this on the **same machine** where your API is running:

```bash
cd ai_audit_agent
python test_api_directly.py
```

This will:
1. Test health endpoint
2. Send your **exact** Google Sheets data
3. Show the **actual** error response
4. Display full details

**Expected output if working:**
```
✅ SUCCESS! Webhook accepted the data
Request ID: audit_20241105_012500
📧 Check email in ~60 seconds!
```

**If there's an error, it will show the details!**

---

### Step 3: Update Apps Script for Better Logging

Replace your Apps Script with the updated version I just modified:

1. Copy from: `docs/gs_script_fixed.txt` (just updated)
2. This version will show **detailed error responses**

---

## 🎯 Common Causes

### Cause 1: API Not Actually Running on Port 8000

**Check:**
```bash
# On the API server machine
curl http://localhost:8000/health

# Or
netstat -an | grep 8000
```

**Fix:**
```bash
# Start the API
python main.py

# OR
docker-compose up -d
```

---

### Cause 2: Firewall Blocking Port 8000

**Check:**
```bash
# On API server
sudo ufw status

# Or test from another machine on same network
curl http://10.246.184.25:8000/health
```

**Fix:**
```bash
# Allow port 8000
sudo ufw allow 8000/tcp
```

---

### Cause 3: API Validation Rejecting Data

Possible issues:
- Field name mismatch
- Data type issue
- Required field empty (though validation passed)

**Diagnose:**
- Run `test_api_directly.py` to see actual validation error
- Check API logs

---

### Cause 4: IP Address Changed

**Check:**
```bash
# On API server, find current IP
ip addr show

# Or
ifconfig

# Or
hostname -I
```

**Update:**
- Update WEBHOOK_URL in Apps Script if IP changed

---

## 🔧 Quick Fix Attempts

### Fix 1: Test Locally First

On the API server machine:

```bash
cd ai_audit_agent

# Test with your exact data
python test_api_directly.py
```

If this **works**, the issue is:
- Network/firewall between Google Sheets and your server
- IP address incorrect
- Port not accessible from outside

If this **fails**, the issue is:
- API validation
- API configuration
- Dependencies

---

### Fix 2: Check .env Configuration

```bash
cd ai_audit_agent
cat .env
```

Verify:
- `HF_API_KEY` is set
- `SENDER_EMAIL` is set
- `SMTP_PASSWORD` is set

**Missing credentials won't stop webhook acceptance**, but check anyway.

---

### Fix 3: Try from Browser Developer Tools

1. Open browser
2. Press F12 (Developer Tools)
3. Go to Console tab
4. Paste this:

```javascript
fetch('http://10.246.184.25:8000/webhook/sheet-row', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    "company_name": "ABP",
    "recipient_name": "Srujan",
    "recipient_email": "katukams@vcu.edu",
    "industry": "Food & Bevarage",
    "company_size": "Small (11-50 emplyees)",
    "annual_revenue_inr": "Less than 10 lakhs",
    "departments": {
      "Leadership & Management": {
        "track_business_metrics": "Excel spreadsheets",
        "competitor_analysis_frequency": "Monthly"
      },
      "Customer Engagement": {
        "inquiry_handling": "Basic analysis",
        "avg_response_time": "4-12 hours"
      },
      "Human Resources": {
        "recruitment_screening": "Basic filtering",
        "attendance_tracking": "Biometric/manual entry"
      },
      "Sales & Marketing": {
        "lead_management": "Manual/notebook",
        "sales_forecasting": "Manual estimates",
        "proposal_generation": "Semi-automated"
      },
      "Operations": {
        "repetitive_tasks": "Fully automated",
        "process_documentation": "Basic documentation"
      },
      "Inventory & Supply Chain": {
        "inventory_tracking": "Basic software",
        "vendor_communication": "Email chains"
      },
      "Quality Control": {
        "quality_checks": "Manual inspection",
        "defect_tracking": "Basic tracking"
      },
      "Finance & Accounting": {
        "invoice_management": "Semi-automated",
        "expense_tracking": "Smart automated"
      },
      "IT & Technology": {
        "website": "Basic static website",
        "backup_security": "Scheduled backup"
      }
    }
  })
})
.then(r => r.json())
.then(d => console.log(d))
.catch(e => console.error(e));
```

This will show the actual response!

---

## 📊 Expected vs Actual

### Expected (Working):

**Apps Script logs:**
```
✅ Validation passed
Response code: 200
Response body: {"status":"accepted","request_id":"audit_..."}
✅ Success!
```

**API logs:**
```
INFO: Started
INFO: Received audit request for ABP
INFO: Background task processing...
```

### Actual (Your Case):

**Apps Script logs:**
```
✅ Validation passed
❌ Error sending to webhook: Exception: Bad request
```

**This means:** Apps Script can't show the actual error. We need to see API logs or test directly.

---

## 🎯 Action Plan

Do these **in order**:

### 1. Check API Logs
```bash
docker-compose logs -f
# OR check terminal where python main.py is running
```

Look for errors when you run `testWebhook()`

### 2. Run Direct Test
```bash
python test_api_directly.py
```

This will show the **real** error!

### 3. Based on Results:

**If test_api_directly.py works:**
- Issue is network/firewall
- Check if port 8000 is accessible from outside
- Try from another machine: `curl http://10.246.184.25:8000/health`

**If test_api_directly.py fails:**
- Shows validation error → Fix the data
- Shows connection error → API not running
- Shows other error → Check API logs

---

## 💡 Most Likely Causes

Based on your symptoms:

1. **Network/CORS Issue** (60% likely)
   - API running but not accessible from Google Apps Script
   - Firewall blocking
   - CORS policy

2. **Data Format Issue** (30% likely)
   - Something in the data API doesn't like
   - Field name typo
   - Encoding issue

3. **API Configuration** (10% likely)
   - API not fully started
   - Missing dependency
   - Port conflict

---

## 🚀 Next Steps

**Right now, run this:**

```bash
# On API server machine
cd ai_audit_agent
python test_api_directly.py
```

**Then tell me:**
1. What does it output?
2. What do the API logs show?
3. Does it work or fail?

This will tell us **exactly** what the problem is!

---

## 📞 Additional Debug Info

### Check API is Listening on Correct IP

```bash
# On API server
netstat -tulpn | grep 8000

# Should show:
# tcp 0 0 0.0.0.0:8000 ... python
```

If it shows `127.0.0.1:8000` instead of `0.0.0.0:8000`, the API is only listening on localhost!

**Fix:** Make sure you're running with `--host 0.0.0.0`:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

### Test from Another Machine on Same Network

```bash
# From any computer on same network as 10.246.184.25
curl http://10.246.184.25:8000/health
```

Should return:
```json
{"status":"ok","timestamp":"...","service":"AI Audit Agent"}
```

---

**Bottom line: Run `test_api_directly.py` and share the output!**

---

*Last Updated: 2024-11-05*
