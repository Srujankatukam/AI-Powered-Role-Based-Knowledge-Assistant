# Google Sheets Setup Guide - Complete Instructions

This guide walks you through connecting your Google Sheet to the AI Audit Agent.

---

## 📋 Your Sheet Structure

### Required Columns (in any order):

#### Basic Information (Columns 1-6)
1. **Company Name** - Name of the company being audited
2. **Contact Person Name** - Recipient of the report
3. **Email Address** - Where to send the report
4. **Industry** - Company's industry sector
5. **Company Size** - e.g., "Medium (51-200 employees)"
6. **Annual Revenue** - e.g., "180 Cr"

#### Department Questions (Columns 7-25)

**Leadership & Management:**
7. How do you track business performance metrics?
8. How often do you analyze competitor activities?

**Customer Engagement:**
9. How do you handle customer inquiries?
10. Average response time to customer queries

**Human Resources:**
11. How do you handle recruitment and screening?
12. Employee attendance tracking method

**Sales & Marketing:**
13. How do you manage leads and follow-ups?
14. Do you use any sales forecasting?
15. How do you generate proposals/quotations?

**Operations:**
16. How are repetitive tasks currently handled?
17. Process documentation and SOPs

**Inventory & Supply Chain:**
18. How do you track inventory levels?
19. Vendor/supplier communication method

**Quality Control:**
20. How do you perform quality checks?
21. Defect and complaint tracking

**Finance & Accounting:**
22. Invoice generation and management
23. Expense tracking and approval

**IT & Technology:**
24. Do you have a company website?
25. Data backup and security practices

---

## 🚀 Setup Steps

### Step 1: Prepare Your Google Sheet

1. **Open your Google Sheet**
2. **Verify column headers** match the names above EXACTLY (case-sensitive)
3. **Row 1** = Headers
4. **Row 2+** = Data

**Example:**

| Company Name | Contact Person Name | Email Address | Industry | ... |
|--------------|---------------------|---------------|----------|-----|
| ABC Corp | John Doe | john@abc.com | Technology | ... |
| XYZ Ltd | Jane Smith | jane@xyz.com | Manufacturing | ... |

---

### Step 2: Open Apps Script Editor

1. In your Google Sheet, go to **Extensions → Apps Script**
2. Delete any existing code
3. Open the file: **`docs/gs_script_updated.txt`**
4. Copy the ENTIRE contents
5. Paste into Apps Script editor
6. Click **Save** (💾 icon or Ctrl+S)
7. Name your project: "AI Audit Agent"

---

### Step 3: Configure Webhook URL

Find this line in the script:
```javascript
const WEBHOOK_URL = "https://your-domain.com/webhook/sheet-row";
```

Replace with YOUR server URL:

**For local testing:**
```javascript
const WEBHOOK_URL = "http://your-local-ip:8000/webhook/sheet-row";
// Example: "http://192.168.1.100:8000/webhook/sheet-row"
```

**For production:**
```javascript
const WEBHOOK_URL = "https://your-domain.com/webhook/sheet-row";
// Example: "https://audit.yourdomain.com/webhook/sheet-row"
```

**Save the script again!**

---

### Step 4: Test the Script

1. Make sure your sheet has at least **one data row** (row 2 or later)
2. In Apps Script editor, select **`testWebhook`** from the function dropdown
3. Click **Run** (▶️ play button)
4. **First time only:** You'll be asked to authorize
   - Click "Review Permissions"
   - Choose your Google account
   - Click "Advanced" → "Go to AI Audit Agent (unsafe)" - it's safe, it's your script!
   - Click "Allow"
5. Check **Execution log** (View → Logs or Ctrl+Enter)

**Expected output:**
```
Testing with row: 2
Extracted data: {...}
✓ Success: {"status":"accepted",...}
✓ Test completed successfully!
```

---

### Step 5: Set Up Automatic Trigger

1. Click the **clock icon** (⏰ Triggers) in the left sidebar
2. Click **"+ Add Trigger"** button (bottom right)

**Configure the trigger:**

| Setting | Value |
|---------|-------|
| Choose which function to run | **onEdit** |
| Choose which deployment | **Head** |
| Select event source | **From spreadsheet** |
| Select event type | **On edit** |

3. Click **Save**
4. Authorize again if prompted

---

### Step 6: Test the Trigger

1. Go back to your Google Sheet
2. **Edit a cell** in any data row (row 2+) - just type something and press Enter
3. **Wait 2-3 seconds**
4. Check your API server logs
5. **Check email** - report should arrive in ~60 seconds!

---

## 🧪 Verification Checklist

### Before Testing:
- [ ] All 25 column headers match exactly
- [ ] At least one complete data row exists
- [ ] Apps Script code pasted and saved
- [ ] Webhook URL updated
- [ ] Script authorized
- [ ] Trigger created

### During Testing:
- [ ] `testWebhook` runs without errors
- [ ] Execution log shows success
- [ ] API server receives webhook
- [ ] Background processing starts
- [ ] Email delivered successfully

---

## 🔍 Verify Column Mapping

Run this function to see your column mapping:

1. In Apps Script editor, select **`showColumnMapping`**
2. Click **Run**
3. View → Logs
4. Verify all columns are mapped correctly

---

## 📊 Sample Data for Testing

Copy this into your sheet (row 2):

| Column | Value |
|--------|-------|
| Company Name | Test Corporation |
| Contact Person Name | Your Name |
| Email Address | your-email@gmail.com |
| Industry | Technology |
| Company Size | Medium (51-200 employees) |
| Annual Revenue | 100 Cr |
| How do you track business performance metrics? | Excel spreadsheets |
| How often do you analyze competitor activities? | Quarterly |
| How do you handle customer inquiries? | Email and phone |
| Average response time to customer queries | 12-24 hours |
| How do you handle recruitment and screening? | Manual CV review |
| Employee attendance tracking method | Biometric system |
| How do you manage leads and follow-ups? | CRM software |
| Do you use any sales forecasting? | Based on past trends |
| How do you generate proposals/quotations? | Word templates |
| How are repetitive tasks currently handled? | Manually |
| Process documentation and SOPs | Word documents |
| How do you track inventory levels? | Excel sheets |
| Vendor/supplier communication method | Email |
| How do you perform quality checks? | Manual inspection |
| Defect and complaint tracking | Excel logs |
| Invoice generation and management | Tally software |
| Expense tracking and approval | Excel-based |
| Do you have a company website? | Yes, responsive |
| Data backup and security practices | Weekly backups |

---

## 🐛 Troubleshooting

### Script doesn't run when I edit cells

**Check:**
1. Is the trigger set up? (Clock icon → should see "onEdit" trigger)
2. Did you edit a data row (not header row)?
3. Check Executions log (Clock icon → Executions)

**Fix:**
- Delete and recreate the trigger
- Make sure "On edit" event type is selected

---

### "TypeError: Cannot read property 'source'"

**Cause:** Wrong trigger type or script error

**Fix:**
- Use **onEdit** trigger (not onFormSubmit) if entering data manually
- If using Google Forms, use **onFormSubmit**

---

### Data not sent / webhook fails

**Check:**
1. Is your API server running?
   ```bash
   curl http://localhost:8000/health
   ```
2. Is WEBHOOK_URL correct in script?
3. Is server accessible from internet? (for production)

**Fix:**
- For local testing, use your local IP: `http://192.168.1.XXX:8000/webhook/sheet-row`
- For production, ensure server is publicly accessible with domain/SSL

---

### Wrong data in report

**Check:**
1. Column headers match EXACTLY (case-sensitive)
2. Run `showColumnMapping` function to verify mapping

**Fix:**
- Update column names in sheet to match expected names
- Or update the script's `extractRowData` function

---

### Authorization errors

**Fix:**
1. Go to https://script.google.com/home/usersettings
2. Enable "Google Apps Script API"
3. Reauthorize the script

---

### "Service invoked too many times"

**Cause:** Google Apps Script daily quota exceeded

**Fix:**
- Wait 24 hours for quota reset
- Reduce number of automated triggers
- Use batch processing instead

---

## 💡 Pro Tips

### 1. Add Status Column

Add a column "Status" to track which rows were processed:

```javascript
// In sendToWebhook function, after successful send:
var sheet = SpreadsheetApp.getActiveSheet();
sheet.getRange(row, lastColumn + 1).setValue("Sent: " + new Date());
```

### 2. Test with Specific Row

Modify `testWebhook` to test any row:

```javascript
function testSpecificRow() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var rowNumber = 3; // Change this to test different rows
  var data = extractRowData(sheet, rowNumber);
  sendToWebhook(data);
}
```

### 3. Bulk Processing

To process multiple rows at once:

```javascript
function processBulk() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var lastRow = sheet.getLastRow();
  
  for (var i = 2; i <= lastRow; i++) {
    var data = extractRowData(sheet, i);
    sendToWebhook(data);
    Utilities.sleep(2000); // Wait 2 seconds between requests
  }
}
```

### 4. Error Notifications

Get notified of errors:

```javascript
function onError(error) {
  MailApp.sendEmail({
    to: "your-email@gmail.com",
    subject: "AI Audit Script Error",
    body: "Error: " + error.toString()
  });
}
```

---

## 📈 What Happens After Submission

1. **Immediate** (< 1 second)
   - Apps Script sends data to webhook
   - API returns success confirmation

2. **Background Processing** (~30-60 seconds)
   - LLM analyzes the data
   - PDF report generated with charts
   - Email sent with attachment

3. **Email Delivery**
   - Professional HTML email
   - PDF report attached
   - Arrives at Email Address from sheet

---

## 🎯 Best Practices

✅ **Do:**
- Test with one row first
- Use exact column names
- Fill all required fields
- Verify email addresses
- Check spam folder for first report

❌ **Don't:**
- Modify column names after setup
- Leave Company Name empty
- Use invalid email addresses
- Delete the header row
- Edit the header row while trigger is active

---

## 🔐 Security Notes

- Apps Script runs under YOUR Google account
- Only you can see and modify the script
- Data is sent to YOUR API endpoint
- No data is stored by Google Apps Script
- Use environment variables for sensitive data in your API

---

## 📞 Need Help?

1. **View Logs:**
   - Apps Script: View → Logs (or Ctrl+Enter)
   - Executions: Clock icon → Executions

2. **Check API:**
   ```bash
   # Test health
   curl http://localhost:8000/health
   
   # View logs
   docker-compose logs -f
   ```

3. **Common Issues:**
   - See troubleshooting section above
   - Check column names match exactly
   - Verify webhook URL is correct
   - Ensure API server is running

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Test script runs without errors
2. ✅ API server logs show webhook received
3. ✅ Email arrives with PDF report
4. ✅ Report contains correct company data
5. ✅ Charts and analysis look good

---

**Ready to go? Start with Step 1!**

For the complete Apps Script code, see: **`docs/gs_script_updated.txt`**

For sample input/output, see: **`docs/SAMPLE_INPUT.json`**

---

*Last Updated: 2024-11-05*
