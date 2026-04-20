# Troubleshooting Google Sheets Integration

Quick solutions for common Google Sheets + Apps Script issues.

---

## 🔴 Your Current Error

```
Error sending to webhook: Exception: Bad request: https://10.246.184.25:8000/webhook/sheet-row
```

### Root Causes:

1. **Empty Required Fields** ✗
   - Your row 4 has empty: Company Name, Contact Person Name, Email Address
   
2. **HTTPS on Local IP** ✗
   - Using `https://10.246.184.25:8000` without SSL certificate
   - Should be `http://10.246.184.25:8000`

---

## ✅ Quick Fix

### Step 1: Update Webhook URL

In your Apps Script, change this line:

**❌ Wrong:**
```javascript
const WEBHOOK_URL = "https://10.246.184.25:8000/webhook/sheet-row";
```

**✅ Correct:**
```javascript
const WEBHOOK_URL = "http://10.246.184.25:8000/webhook/sheet-row";
```

**Note:** Use `http://` (not `https://`) for local IP addresses without SSL.

---

### Step 2: Fill Required Fields

Row 4 in your sheet must have these fields filled:

| Required Field | Status in Row 4 | Fix |
|----------------|----------------|-----|
| Company Name | ❌ Empty | Must fill |
| Contact Person Name | ❌ Empty | Must fill |
| Email Address | ❌ Empty | Must fill with valid email |
| Industry | ✅ "Food & beverage" | OK |
| Company Size | ✅ "Small (11-50)" | OK |
| Annual Revenue | ✅ "Less than 10 lakhs" | OK |

---

### Step 3: Use Fixed Script

Replace your current Apps Script with the improved version:

1. Open: `docs/gs_script_fixed.txt`
2. Copy ALL the code
3. Go to your Apps Script editor
4. Delete existing code
5. Paste new code
6. Update WEBHOOK_URL to: `http://10.246.184.25:8000/webhook/sheet-row`
7. Save

---

## 🧪 Test the Fix

### Test 1: Check API Health

In Apps Script editor:
1. Select function: `testHealth`
2. Click Run
3. Check logs (Ctrl+Enter or View → Logs)

**Expected:**
```
Testing health endpoint: http://10.246.184.25:8000/health
Status: 200
✅ API is healthy and reachable!
```

---

### Test 2: Find Incomplete Rows

In Apps Script editor:
1. Select function: `findIncompleteRows`
2. Click Run
3. Check logs

This will show which rows have missing required fields.

---

### Test 3: Fill Required Fields and Test

1. Fill row 4 with sample data:
   - Company Name: `Test Food Company`
   - Contact Person Name: `Your Name`
   - Email Address: `your-email@gmail.com`

2. Run `testWebhook` function

**Expected:**
```
✅ Validation passed
✅ Test completed successfully!
📧 Check email in ~60 seconds for the report
```

---

## 📋 Common Errors & Solutions

### Error 1: "Bad request"

**Symptoms:**
```
Error: Bad request: https://...
```

**Causes:**
- Empty required fields
- Invalid email format
- Wrong protocol (HTTPS instead of HTTP)

**Solutions:**
1. ✅ Fill all required fields
2. ✅ Use valid email address
3. ✅ Change `https://` to `http://` for local IP

---

### Error 2: "DNS error" or "Cannot connect"

**Symptoms:**
```
Error: DNS error
Error: Address unavailable
```

**Causes:**
- API server not running
- Wrong IP address
- Network issue

**Solutions:**
1. ✅ Start API: `python main.py` or `docker-compose up -d`
2. ✅ Verify IP address is correct
3. ✅ Test from browser: `http://10.246.184.25:8000/health`
4. ✅ Check firewall allows port 8000

---

### Error 3: "SSL error" or "Certificate error"

**Symptoms:**
```
Error: SSL certificate problem
Error: Failed to verify certificate
```

**Cause:**
- Using HTTPS with local IP that has no SSL certificate

**Solution:**
✅ Use HTTP instead:
```javascript
// Wrong
const WEBHOOK_URL = "https://10.246.184.25:8000/webhook/sheet-row";

// Correct
const WEBHOOK_URL = "http://10.246.184.25:8000/webhook/sheet-row";
```

---

### Error 4: "Validation failed (422)"

**Symptoms:**
```
HTTP 422: Validation failed
Missing required field
Invalid email address
```

**Causes:**
- Required fields empty
- Email format invalid
- Data type mismatch

**Solutions:**
1. ✅ Check all required fields are filled
2. ✅ Verify email format: `name@domain.com`
3. ✅ Run `findIncompleteRows()` to find issues

---

### Error 5: "Timeout"

**Symptoms:**
```
Error: Request timeout
Error: Operation timed out
```

**Causes:**
- API server slow or not responding
- Network latency
- LLM processing taking too long

**Solutions:**
1. ✅ Check API is running: `curl http://10.246.184.25:8000/health`
2. ✅ Increase timeout in script
3. ✅ Check API logs for errors

---

## 🔧 Debugging Commands

### In Apps Script Editor:

**Show Configuration:**
```javascript
// Function: showConfig
// Shows webhook URL, sheet info, column headers
```

**Test API Health:**
```javascript
// Function: testHealth
// Tests if API is reachable
```

**Find Incomplete Rows:**
```javascript
// Function: findIncompleteRows
// Lists rows with missing required fields
```

**Test Full Workflow:**
```javascript
// Function: testWebhook
// Tests complete workflow with validation
```

---

## 📊 Required Fields Checklist

Every row must have these fields (non-empty):

- [x] **Company Name** - Any text
- [x] **Contact Person Name** - Any text
- [x] **Email Address** - Valid email format
- [x] **Industry** - Any text
- [x] **Company Size** - Any text
- [x] **Annual Revenue** - Any text

Department questions can be empty (will show as "No information provided" in report).

---

## 🌐 Network Configuration

### Local Development (Your Current Setup):

**API URL:**
```
http://10.246.184.25:8000
```

**Webhook URL:**
```
http://10.246.184.25:8000/webhook/sheet-row
```

**Health Check:**
```
http://10.246.184.25:8000/health
```

**Important:** Use `http://` not `https://` for local IP!

---

### Production (With Domain):

**API URL:**
```
https://yourdomain.com
```

**Webhook URL:**
```
https://yourdomain.com/webhook/sheet-row
```

**With SSL:** You can use `https://` when you have a proper domain and SSL certificate.

---

## 🧪 Step-by-Step Testing

### 1. Test API is Running

From terminal:
```bash
curl http://10.246.184.25:8000/health
```

Expected:
```json
{"status":"ok","timestamp":"...","service":"AI Audit Agent"}
```

---

### 2. Test from Browser

Open in browser:
```
http://10.246.184.25:8000/health
```

Should show:
```json
{"status": "ok", ...}
```

---

### 3. Test Apps Script Connection

In Apps Script:
1. Select: `testHealth`
2. Click Run
3. Check logs

Expected: "✅ API is healthy and reachable!"

---

### 4. Check Row Completeness

In Apps Script:
1. Select: `findIncompleteRows`
2. Click Run
3. Check logs

Fix any rows that show as incomplete.

---

### 5. Test Full Workflow

In Apps Script:
1. Select: `testWebhook`
2. Click Run
3. Check logs

Expected: "✅ Test completed successfully!"

---

### 6. Check Email

Wait ~60 seconds, check:
- Inbox
- Spam folder
- Promotions tab (Gmail)

---

## 💡 Best Practices

### DO:
✅ Fill all required fields before testing
✅ Use HTTP for local IP addresses
✅ Use valid email addresses
✅ Test with `testHealth` first
✅ Run `findIncompleteRows` regularly
✅ Check API logs if errors occur

### DON'T:
❌ Use HTTPS with local IP without SSL
❌ Leave required fields empty
❌ Use invalid email formats
❌ Test without starting API first
❌ Ignore validation errors

---

## 🔍 API Server Checks

### Check if API is Running:

**Method 1: cURL**
```bash
curl http://10.246.184.25:8000/health
```

**Method 2: Browser**
```
http://10.246.184.25:8000/health
```

**Method 3: Apps Script**
```javascript
// Run testHealth() function
```

---

### View API Logs:

**Docker:**
```bash
docker-compose logs -f
```

**Direct Python:**
```
# Logs appear in terminal
```

---

### Restart API if Needed:

**Docker:**
```bash
docker-compose restart
```

**Direct Python:**
```bash
# Stop with Ctrl+C
python main.py
```

---

## 📧 Email Delivery Issues

### Email Not Received:

1. **Check spam folder**
   - Gmail may filter new senders

2. **Check promotions tab** (Gmail)
   - Automated emails sometimes go here

3. **Verify email address**
   - Must be valid format
   - Must be accessible

4. **Check API logs**
   ```bash
   docker-compose logs -f | grep email
   ```

5. **Verify email settings in .env**
   ```bash
   SENDER_EMAIL=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

---

## 🎯 Your Specific Fix

Based on your error log, do this:

### 1. Update Apps Script

Replace your script with: `docs/gs_script_fixed.txt`

Change line 13 to:
```javascript
const WEBHOOK_URL = "http://10.246.184.25:8000/webhook/sheet-row";
```

### 2. Fill Row 4 Required Fields

| Field | Current | Fill With |
|-------|---------|-----------|
| Company Name | (empty) | `Sample Food Company` |
| Contact Person Name | (empty) | `John Doe` |
| Email Address | (empty) | `your-email@gmail.com` |

### 3. Test Again

1. Save script
2. Run `testWebhook`
3. Check logs
4. Wait 60 seconds
5. Check email

---

## 📞 Still Having Issues?

### Check These:

1. **API Running?**
   ```bash
   curl http://10.246.184.25:8000/health
   ```

2. **Correct Protocol?**
   - HTTP for local IP ✅
   - HTTPS for production domain ✅

3. **Required Fields?**
   - Run `findIncompleteRows()` in Apps Script

4. **Firewall?**
   - Port 8000 must be open
   - Test from same network

5. **API Logs?**
   ```bash
   docker-compose logs -f
   ```

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ `testHealth()` returns 200 OK
2. ✅ `testWebhook()` shows "Test completed successfully"
3. ✅ API logs show webhook received
4. ✅ Email arrives in ~60 seconds
5. ✅ PDF contains correct company data
6. ✅ Charts show all 9 departments

---

**Need more help?** Check the complete setup guide in `docs/GOOGLE_SHEETS_SETUP.md`

---

*Last Updated: 2024-11-05*
