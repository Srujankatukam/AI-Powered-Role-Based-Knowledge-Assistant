# 🔍 Diagnostics: LLM Output & PDF Customization

## 🎯 Your Issues

1. **Same PDF for every user** - Not customized based on input
2. **Unsure if LLM is working** - Might be using fallback responses

---

## 🧪 Step 1: Test LLM Directly

This will tell you if the LLM is actually working or always using fallback.

```bash
cd ai_audit_agent
python test_llm_directly.py
```

### What to Look For:

**✅ LLM Working (Good):**
```
✅ This appears to be a REAL LLM response!
✅ Company mentioned: True
✅ Company name 'TestCorp Industries' found in summary
Summary length: 350 characters
```

**❌ LLM Using Fallback (Bad):**
```
⚠️ WARNING: This looks like a FALLBACK response!
⚠️ The LLM might not be working properly
❌ Company name NOT found in summary (might be fallback)
Summary length: 200 characters
```

---

## 🔍 Step 2: Check API Logs

Run your application and watch the logs:

```bash
# If using Docker:
docker-compose logs -f

# If running directly:
# Logs appear in terminal where you ran: python main.py
```

### Send a Test Request:

```bash
python test_api_directly.py
```

### What to Look For in Logs:

**✅ Good (LLM Working):**
```
INFO: [audit_xxx] Calling LLM for analysis...
INFO: [audit_xxx] LLM analysis completed successfully
INFO: [audit_xxx] Summary length: 350 chars
INFO: [audit_xxx] ✓ Response appears customized
INFO: [audit_xxx] ✓ Company name found in summary
INFO: [audit_xxx] Creating PDF for: ABP
```

**❌ Bad (LLM Failing):**
```
ERROR: [audit_xxx] LLM API attempts failed, generating fallback
WARNING: [audit_xxx] ⚠️ Response appears to be FALLBACK
WARNING: [audit_xxx] ⚠️ Company name NOT in summary
```

---

## 🔧 Step 3: Common Causes & Fixes

### Cause 1: No Hugging Face API Key

**Check:**
```bash
cat .env | grep HF_API_KEY
```

**If empty or missing:**
```bash
# Add to .env:
HF_API_KEY=your_actual_huggingface_api_key_here
```

**Get your key:**
1. Go to https://huggingface.co/settings/tokens
2. Create a new token
3. Copy and add to `.env`

---

### Cause 2: Model Loading (First Time)

**Symptoms:**
- First request takes 30+ seconds
- Subsequent requests faster
- Logs show "Model is loading"

**Solution:**
- Wait 30 seconds
- Retry the request
- This is normal for first use

---

### Cause 3: API Rate Limiting

**Symptoms:**
- Error: "Rate limit exceeded"
- 429 status code in logs

**Solution:**
- Wait a few minutes
- Use a different API key
- Or upgrade Hugging Face account

---

### Cause 4: Wrong Model URL

**Check .env:**
```bash
cat .env | grep HF_MODEL_URL
```

**Should be:**
```bash
HF_MODEL_URL=https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct
```

**Or remove the line** to use default.

---

## 📊 Step 4: Test with Multiple Companies

This verifies PDFs are actually different:

```bash
# Test 1: Company A
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Alpha Tech",
    "recipient_name": "Test User",
    "recipient_email": "your-email@gmail.com",
    "industry": "Technology",
    "company_size": "Small",
    "annual_revenue_inr": "50 Cr",
    "departments": {"IT": {"website": "No website"}}
  }'

# Wait 60 seconds, check email, save PDF as "alpha.pdf"

# Test 2: Company B  
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Beta Manufacturing",
    "recipient_name": "Test User",
    "recipient_email": "your-email@gmail.com",
    "industry": "Manufacturing",
    "company_size": "Large",
    "annual_revenue_inr": "500 Cr",
    "departments": {"IT": {"website": "Advanced AI-powered website"}}
  }'

# Wait 60 seconds, check email, save PDF as "beta.pdf"
```

### Compare PDFs:

**✅ Should be DIFFERENT:**
- Company names different
- Industries different
- Summaries customized
- Risk scores different
- Drawbacks specific to each

**❌ If IDENTICAL:**
- LLM is using fallback
- Fix API key issue
- Check logs for errors

---

## 🐛 Step 5: Debug LLM Response

Add this test to see RAW LLM output:

```python
# test_llm_raw.py
import asyncio
from llm_client import LLMClient

async def main():
    client = LLMClient()
    
    data = {
        "company_name": "YOUR COMPANY NAME",
        "industry": "YOUR INDUSTRY",
        "company_size": "Medium",
        "annual_revenue_inr": "100 Cr",
        "departments": {
            "IT": {"website": "Basic"}
        }
    }
    
    print("Calling LLM...")
    result = await client.generate_audit_analysis(data)
    
    print("\nRaw Result:")
    import json
    print(json.dumps(result, indent=2))
    
    # Check if customized
    summary = result['summary']['personalized_summary']
    if data['company_name'] in summary:
        print(f"\n✅ Company name '{data['company_name']}' is in summary")
    else:
        print(f"\n❌ Company name NOT in summary - using FALLBACK!")

asyncio.run(main())
```

Run:
```bash
python test_llm_raw.py
```

---

## 🔍 Step 6: Check Fallback Response

The fallback is triggered when LLM fails. It's a generic response.

**Fallback indicators:**
- Summary contains: "demonstrates foundational digital capabilities"
- Risk score is exactly 60
- All departments have identical drawbacks
- No company name mentioned
- Generic text

**To fix:** Resolve the LLM API issue (see Cause 1-4 above)

---

## ✅ Step 7: Verify Fix

After fixing, verify:

1. **LLM Test:**
   ```bash
   python test_llm_directly.py
   ```
   Should show: "✅ This appears to be a REAL LLM response!"

2. **Logs Show:**
   ```
   ✓ Response appears customized
   ✓ Company name found in summary
   ```

3. **Multiple PDFs are different:**
   - Different company names on cover page
   - Different summaries
   - Different risk scores
   - Specific drawbacks per company

---

## 🎯 Quick Checklist

Run through this checklist:

- [ ] HF_API_KEY is set in .env
- [ ] Model URL is correct (or use default)
- [ ] `python test_llm_directly.py` shows REAL response
- [ ] Logs don't show "FALLBACK" warnings
- [ ] Company name appears in summary
- [ ] Multiple test requests produce different PDFs
- [ ] Risk scores vary between companies
- [ ] Summaries are customized

---

## 💡 Most Common Issue: Missing API Key

**90% of the time, the issue is:**

```bash
# .env file doesn't have API key
HF_API_KEY=
```

**Fix:**
1. Go to https://huggingface.co/settings/tokens
2. Create new token (read access is enough)
3. Copy token
4. Add to .env:
   ```
   HF_API_KEY=hf_your_actual_token_here
   ```
5. Restart application
6. Test again

---

## 📞 Still Not Working?

### Share This Information:

1. **Output of:**
   ```bash
   python test_llm_directly.py
   ```

2. **Your .env (HIDE THE ACTUAL KEY):**
   ```bash
   cat .env | sed 's/hf_[^ ]*/hf_HIDDEN/g'
   ```

3. **API Logs when running test:**
   ```bash
   docker-compose logs | tail -50
   ```

4. **Do two PDFs look identical?**
   - Yes → LLM using fallback
   - No → LLM working, something else wrong

---

## 🚀 Expected Behavior (When Working)

### Company A (Small Tech):
- **Name:** Alpha Tech Solutions
- **Summary:** "Alpha Tech Solutions operates as a small technology company..."
- **Risk Score:** 75 (higher risk due to no website)
- **IT Drawbacks:** "Absence of online presence limits..."

### Company B (Large Manufacturing):
- **Name:** Beta Manufacturing Ltd
- **Summary:** "Beta Manufacturing Ltd is a large manufacturing organization..."
- **Risk Score:** 35 (lower risk due to advanced tech)
- **IT Drawbacks:** []  (no significant drawbacks)

**Both DIFFERENT and CUSTOMIZED!**

---

**Run the diagnostics and share the results!** 🔍

---

*Last Updated: 2024-11-05*
