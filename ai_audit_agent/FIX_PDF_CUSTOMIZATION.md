# 🔧 Fix: PDF Customization & LLM Issues

## 🎯 Problem

You reported:
1. **Same PDF for every user** - not customized
2. **Unsure if LLM is working** - might be using fallback

---

## ⚡ Quick Diagnosis (2 minutes)

### Step 1: Test LLM

```bash
cd ai_audit_agent
python test_llm_directly.py
```

**Look for this:**

✅ **If you see:**
```
✅ This appears to be a REAL LLM response!
✅ Company name 'TestCorp' found in summary
```
→ LLM is working! Issue might be elsewhere.

❌ **If you see:**
```
⚠️ WARNING: This looks like a FALLBACK response!
❌ Company name NOT found in summary
```
→ LLM is failing! Need to fix API key.

---

### Step 2: Check Logs

**Start your app:**
```bash
python main.py
# OR
docker-compose up
```

**In another terminal, send test:**
```bash
python test_api_directly.py
```

**Watch the logs for:**

✅ **Good:**
```
INFO: [audit_xxx] ✓ Response appears customized
INFO: [audit_xxx] ✓ Company name found in summary
```

❌ **Bad:**
```
WARNING: [audit_xxx] ⚠️ Response appears to be FALLBACK
WARNING: [audit_xxx] ⚠️ Company name NOT in summary
```

---

## 🔧 Fix #1: API Key Issue (Most Common)

### Check if HF_API_KEY is set:

```bash
cat .env | grep HF_API_KEY
```

### If Empty or Missing:

1. **Get API key:**
   - Go to https://huggingface.co/settings/tokens
   - Click "New token"
   - Copy the token (starts with `hf_...`)

2. **Add to .env:**
   ```bash
   # Open .env
   nano .env
   
   # Add or update this line:
   HF_API_KEY=hf_your_actual_token_here
   ```

3. **Restart:**
   ```bash
   # Docker:
   docker-compose restart
   
   # Direct:
   # Stop with Ctrl+C, then:
   python main.py
   ```

4. **Test again:**
   ```bash
   python test_llm_directly.py
   ```

---

## 🔧 Fix #2: Model Loading (First Time)

### Symptoms:
- Very slow first request (30+ seconds)
- Error: "Model is loading"

### Solution:
**Just wait!** First request loads the model.

```bash
# Try request
python test_api_directly.py

# If it times out, wait 30 seconds and retry
sleep 30
python test_api_directly.py
```

Second request will be much faster.

---

## 🔧 Fix #3: Verify Model URL

### Check .env:

```bash
cat .env | grep HF_MODEL_URL
```

### Should Be:

```bash
HF_MODEL_URL=https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct
```

### Or Just Remove It:

```bash
# Remove or comment out the line to use default
#HF_MODEL_URL=...
```

---

## ✅ Verify the Fix

### Test 1: LLM Direct Test

```bash
python test_llm_directly.py
```

**Expected:**
```
✅ This appears to be a REAL LLM response!
✅ Company name 'TestCorp Industries' found in summary
Summary length: 350 characters
Risk score: 68
```

---

### Test 2: Multiple Companies

Test with 2 different companies:

**Company A:**
```bash
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Small Tech Startup",
    "recipient_name": "Test",
    "recipient_email": "your-email@gmail.com",
    "industry": "Technology",
    "company_size": "Small (11-50)",
    "annual_revenue_inr": "10 Cr",
    "departments": {"IT": {"website": "No website", "backup_security": "No backup"}}
  }'
```

Wait 60 seconds, check email, note:
- Company name: "Small Tech Startup"
- Risk score: Should be HIGH (around 75-85)

**Company B:**
```bash
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Enterprise Manufacturing Corp",
    "recipient_name": "Test",
    "recipient_email": "your-email@gmail.com",
    "industry": "Manufacturing",
    "company_size": "Large (500+)",
    "annual_revenue_inr": "500 Cr",
    "departments": {"IT": {"website": "AI-powered website", "backup_security": "Real-time encrypted backup"}}
  }'
```

Wait 60 seconds, check email, note:
- Company name: "Enterprise Manufacturing Corp"
- Risk score: Should be LOW (around 25-35)

**Compare:**
- ✅ Different company names on cover
- ✅ Different summaries
- ✅ Different risk scores
- ✅ Different drawbacks

If IDENTICAL → LLM still using fallback!

---

## 📊 What Good Output Looks Like

### Company A (Small, No Tech):
```
Company: Small Tech Startup
Summary: "Small Tech Startup operates as a small technology company 
with 11-50 employees and 10 Cr annual revenue. The absence of a 
website and backup systems presents significant operational risks..."
Risk Score: 82
Maturity: Low
```

### Company B (Large, Advanced Tech):
```
Company: Enterprise Manufacturing Corp
Summary: "Enterprise Manufacturing Corp is a large manufacturing 
organization with 500+ employees and 500 Cr revenue. The company 
demonstrates high AI maturity through AI-powered website and 
real-time encrypted backups..."
Risk Score: 28
Maturity: High
```

**Completely different and customized!** ✅

---

## 🐛 Still Not Working?

### Run Full Diagnostics:

```bash
# 1. LLM test
python test_llm_directly.py > llm_test.log

# 2. API test with logs
python test_api_directly.py

# 3. Check logs
docker-compose logs > app_logs.txt
# OR if running directly, copy terminal output

# 4. Check environment
cat .env | grep -v PASSWORD
```

**Share:**
1. Output of `llm_test.log`
2. Last 50 lines of `app_logs.txt`
3. Do PDFs look identical or different?

---

## 💡 Common Mistakes

### 1. API Key Format Wrong
```bash
# ❌ Wrong:
HF_API_KEY=your_huggingface_api_key_here

# ✅ Correct:
HF_API_KEY=hf_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
```

### 2. Not Restarting After .env Change
```bash
# Always restart after editing .env!
docker-compose restart
# OR
# Stop and restart python main.py
```

### 3. Testing Too Fast
```bash
# LLM needs time to process
# Send request, then wait 60 seconds before checking email
sleep 60
```

### 4. Wrong Email
```bash
# Make sure you're checking the RIGHT email address
# The one you specified in recipient_email
```

---

## ✅ Success Checklist

After fix, verify:

- [ ] `python test_llm_directly.py` shows "REAL LLM response"
- [ ] Logs show "✓ Response appears customized"
- [ ] Logs show "✓ Company name found in summary"
- [ ] No "FALLBACK" warnings in logs
- [ ] Two test PDFs are different
- [ ] Company names different on cover page
- [ ] Summaries mention specific company names
- [ ] Risk scores are different
- [ ] Drawbacks are specific to each company

---

## 🎯 The Fix (Summary)

**Most likely issue:** Missing or incorrect HF_API_KEY

**Solution:**
1. Get key from https://huggingface.co/settings/tokens
2. Add to `.env`: `HF_API_KEY=hf_your_token`
3. Restart application
4. Test with: `python test_llm_directly.py`
5. Should see: "✅ REAL LLM response"

**Then test with different companies to verify PDFs are customized!**

---

**For complete diagnostics, see:** `DIAGNOSTICS_LLM_AND_PDF.md`

---

*Last Updated: 2024-11-05*
