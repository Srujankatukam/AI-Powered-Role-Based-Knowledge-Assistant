# 🦙 Install Ollama for AI Audit Agent

Complete guide to set up Ollama locally and use it instead of Hugging Face API.

---

## 🎯 Benefits of Using Ollama

- ✅ **Free** - No API costs
- ✅ **Fast** - Runs locally, no network latency
- ✅ **Private** - Your data never leaves your machine
- ✅ **No rate limits** - Use as much as you want
- ✅ **Works offline** - No internet required after download

---

## 📥 Step 1: Install Ollama

### On macOS:

```bash
# Download and install
curl -fsSL https://ollama.com/install.sh | sh

# Or using Homebrew
brew install ollama
```

### On Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### On Windows:

Download from: https://ollama.com/download/windows

---

## 🚀 Step 2: Start Ollama

```bash
# Start Ollama service
ollama serve
```

**Leave this terminal running!** Ollama needs to be running in the background.

---

## 📦 Step 3: Download Llama 3 Model

**In a NEW terminal:**

```bash
# Download Llama 3 8B (Recommended - 4.7GB)
ollama pull llama3

# Or for better quality (larger model - 26GB):
ollama pull llama3:70b

# Or for faster/smaller (lighter - 2.3GB):
ollama pull llama3:8b-instruct-q4_0
```

**Wait for download to complete.** First time takes a few minutes.

---

## ⚙️ Step 4: Update Your .env

```bash
cd ai_audit_agent
nano .env

# Add these lines:
USE_OLLAMA=true
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

# Comment out or remove Hugging Face settings:
# HF_API_KEY=...
# HF_MODEL_URL=...

# Keep your email settings:
SENDER_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
```

---

## 🧪 Step 5: Test Ollama

```bash
# Test if Ollama is running
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Hello, this is a test.",
  "stream": false
}'

# Should return JSON with response
```

---

## 🔄 Step 6: Restart Your Application

```bash
# If using Docker:
docker-compose restart

# If running directly:
# Stop with Ctrl+C, then:
python main.py
```

---

## ✅ Step 7: Verify It Works

```bash
python test_llm_directly.py
```

**Should show:**
```
Using Ollama at http://localhost:11434
Model: llama3
✅ This appears to be a REAL LLM response!
✅ Company name 'TestCorp' found in summary
```

---

## 🎯 Complete .env Example

```bash
# Ollama Configuration (Local LLM)
USE_OLLAMA=true
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

# Email Configuration
SENDER_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465

# Application Configuration
LOG_LEVEL=INFO
```

---

## 📊 Model Recommendations

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `llama3:8b-instruct-q4_0` | 2.3GB | ⚡⚡⚡ Fast | Good | Testing/Development |
| `llama3` (8B) | 4.7GB | ⚡⚡ Fast | Better | **Recommended** ⭐ |
| `llama3:70b` | 26GB | ⚡ Slower | Best | Production (if you have RAM) |

**Recommendation:** Start with `llama3` (8B) - good balance of speed and quality.

---

## 🔧 Troubleshooting

### Issue: "Connection refused"

**Solution:**
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, check:
curl http://localhost:11434/
# Should return: "Ollama is running"
```

---

### Issue: "Model not found"

**Solution:**
```bash
# List downloaded models
ollama list

# Download the model
ollama pull llama3
```

---

### Issue: "Out of memory"

**Solutions:**
1. Use smaller model: `ollama pull llama3:8b-instruct-q4_0`
2. Close other applications
3. Restart Ollama: `killall ollama && ollama serve`

---

### Issue: Application still using Hugging Face

**Solution:**
```bash
# Make sure USE_OLLAMA=true in .env
cat .env | grep USE_OLLAMA

# Should show: USE_OLLAMA=true
# If not, add it and restart
```

---

## 🚀 Performance Comparison

### Hugging Face (Cloud):
- **Speed:** 10-30 seconds per request
- **Cost:** API limits
- **Requires:** Internet + API key

### Ollama (Local):
- **Speed:** 2-5 seconds per request ⚡
- **Cost:** Free
- **Requires:** Just local resources

**Ollama is typically 3-5x faster!**

---

## 💡 Pro Tips

### 1. Keep Ollama Running

Add to your startup/cron:
```bash
# macOS/Linux - add to ~/.bashrc or startup
ollama serve &
```

### 2. Pre-load Model (Faster First Request)

```bash
# Warm up the model
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Hello",
  "stream": false
}'
```

### 3. Monitor Usage

```bash
# Check running models
ollama ps

# Check logs
ollama logs
```

---

## 🔄 Switching Between Hugging Face and Ollama

You can easily switch:

**Use Ollama:**
```bash
USE_OLLAMA=true
```

**Use Hugging Face:**
```bash
USE_OLLAMA=false
HF_API_KEY=your_key
```

Just change `.env` and restart!

---

## 📈 Expected Results

After switching to Ollama:

- ✅ **3-5x faster** response times
- ✅ **No API costs**
- ✅ **Works offline**
- ✅ **Same or better quality**
- ✅ **Customized reports** for each company

---

## 🎯 Quick Start Commands

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Start Ollama
ollama serve &

# 3. Download model
ollama pull llama3

# 4. Update .env
echo "USE_OLLAMA=true" >> .env
echo "OLLAMA_MODEL=llama3" >> .env
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env

# 5. Restart app
docker-compose restart

# 6. Test
python test_llm_directly.py
```

---

## ✅ Success Checklist

- [ ] Ollama installed
- [ ] `ollama serve` running
- [ ] Model downloaded (`ollama pull llama3`)
- [ ] `.env` updated with `USE_OLLAMA=true`
- [ ] Application restarted
- [ ] Test shows "Using Ollama"
- [ ] PDFs are customized per company

---

**Next:** See `ollama_llm_client.py` for the implementation details.

---

*Last Updated: 2024-11-05*
