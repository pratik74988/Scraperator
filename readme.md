# 🤖 AI Web Scraper


Hey there! 👋 Welcome to  AI-powered web scraping beast. This bad boy uses Groq's 70B LLM to scrape websites and extract data like a boss. No more "right-click → inspect element → copy pasta" nonsense!

![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/django-5.0-green?style=for-the-badge&logo=django)
![AI](https://img.shields.io/badge/AI-Powered-purple?style=for-the-badge)

---

## 🎯 What's This About?

Ever tried scraping a website and ended up with a mess of HTML soup? Yeah, me too. So I built this thing that:

- **Scrapes ANY website** (okay, most websites... we're not magicians)
- **Understands what you want** using AI (just tell it in plain English!)
- **Handles both static AND dynamic sites** (JavaScript? Bring it on!)
- **Gives you clean JSON data** (not some XML nightmare from 2005)
- **Has a sick chat interface** (because ChatGPT made us all spoiled)

Basically, it's like having a really smart intern who never sleeps and loves scraping websites. 🧑‍💻

---

## ✨ Cool Features

### 🧠 AI-Powered Extraction
No more writing XPath selectors at 2 AM! Just tell it:
> "Hey, grab all the product names and prices from this page"

And boom! Done. ✅

### 💬 clean Interface
Forget boring forms. Chat with the AI like you're texting a friend:
- "What's on this page?"
- "Extract the pricing info"
- "Get me all the links"

### 🎨 Actually Looks Good
Not your typical Django admin panel vibes. This has:
- Smooth gradients 🌈
- Animations that don't suck ✨
- Mobile-friendly (your thumb will thank you) 📱

### ⚡ Smart Auto-Detection
The scraper is smart enough to figure out if a site needs:
- **BeautifulSoup** (for simple HTML)
- **Selenium** (for fancy JavaScript sites)

You don't have to choose. It just... knows. 🔮

---

## 🚀 Quick Start

### Prerequisites
You need:
- Python 3.10+ (time to upgrade if you're still on 3.6...)
- A Groq API key ([grab one here](https://console.groq.com) - it's free!)
- Chrome (for Selenium to work its magic)

### Setup (2 Minutes)

```bash
# 1. Clone this beauty
git clone <https://github.com/pratik74988/Scraperator.git>
cd Scraperator

# 2. Make a virtual environment (be responsible!)
python -m venv venv
source venv/bin/activate  # Windows? Use: venv\Scripts\activate

# 3. Install the goodies
pip install -r requirements.txt

# 4. Set up your secrets
cp .env.example .env
# Edit .env and add your Groq API key

# 5. Database magic
python manage.py migrate

# 6. Fire it up! 🔥
python manage.py runserver
```

Open `http://127.0.0.1:8000` and you're in business! 🎉

---

## 🎮 How to Use

### Option 1: The Chat Way 
1. Go to **AI Assistant** in the nav
2. Drop a URL
3. Chat with it like: *"What products are on this page provide me exact data?"*
4. Get your answer and scrapped stuff ✨

### Option 2: The Form Way (Old School)
1. Hit **"New Scrape"**
2. Paste your URL
3. Tell it what you want
4. Click the big blue button
5. Profit! 💰

### Option 3: The API Way (Nerds)
```bash
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "user_instructions": "Get me everything!"
  }'
```

---

## 🏗️ Tech Stack

**Backend:**
- Django 5.0 (because it's 2025, not 2014)
- LangChain (AI orchestration)
- Groq (70B LLM - it's FAST ⚡)
- BeautifulSoup (the OG scraper)
- Selenium (for the fancy stuff)

**Frontend:**
**Not a frontEnd Developer soo ignore css made using GPT**
- Tailwind CSS (utility classes FTW)
- Vanilla JS (keeping it simple)
- Font Awesome (icons that don't look like 💩)

**AI:**
- Groq's Llama 3.1 70B (beast mode activated)
- LangChain for the smart stuff

---

## 📸 Screenshots
### Droping them Soon

<!-- ### Dashboard
*Stats cards that actually look good*
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Screenshot)

### AI Chat Interface
*ChatGPT vibes but for web scraping*
![Chat](https://via.placeholder.com/800x400?text=Chat+Interface)

### Results Page
*Your data, beautifully formatted*
![Results](https://via.placeholder.com/800x400?text=Results+Page) -->

---

## 🎯 Use Cases

### For Students
- Research data collection
- Project datasets
- Competitive analysis

### For Developers
- API testing data
- Website monitoring
- Content aggregation

### For Everyone Else
- Price tracking
- Job listings
- News aggregation
- Whatever you can think of!

---

## 🛠️ Project Structure

```
Scraperator/
├── 📁 backend/              # Core backend config (settings, logs)
│   ├── 📁 config/          # Django settings and environment setup
│   └── 📁 logs/            # Log files for debugging
|   |__ 📁 scrapper/             # Main Django app
│   |   ├── 🧠 agent/           # LangChain agents and AI logic
│   |   ├── 📁 migrations/      # Django migration files
│   |   ├── 🐍 __init__.py      # App initializer
│   |   ├── 🛡️ admin.py         # Admin panel config
│   |   ├── ⚙️ apps.py          # App configuration
│   |   ├── 📊 models.py        # Database models
│   |   ├── 🕷️ scraper.py       # Scraping logic
│   |   ├── 🧪 tests.py          # Unit tests
│   |   ├── 🌐 urls.py           # URL routing
│   |   └── 🎨 views.py          # API views and endpoints
|   |___📄 manage.py             # Django management script            
├── 📁 frontend/
│   └── 📁 templates/
│       └── 📁 scraper/     # HTML templates for UI
|           |__📁static/
|           |   |__📁js/       #js files here
|           |   |__📁css/      # css files here
│           ├── 🧠 ai_test.html      # AI test interface
│           ├── 📝 create_job.html   # Job creation form
│           ├── 📊 dashboard.html    # Main dashboard
│           ├── 🔍 job_detail.html   # Job detail view
│           └── 🗑️ removedStuff.txt  # Deprecated or removed code
```

Clean, modular, maintainable. Chef's kiss! 👨‍🍳💋

---

## 🐛 Known Issues

- **Selenium can be slow**: Yeah, running a full browser takes time. Deal with it. ⏱️
- **Some sites block scrapers**: They're onto us. Try using proxies (not included... yet)
- **Rate limiting**: Don't be that person who sends 1000 requests/second.

---

## 🚀 Roadmap

Things I wanna add (maybe... probably... eventually):

- [ ] **Celery for async scraping** (because waiting is boring)
- [ ] **Export to Excel/CSV** (for the Excel warriors)
- [ ] **Scheduled scraping** (cron jobs, baby!)
- [ ] **Proxy support** (for the sneaky ones)
- [ ] **Dark mode** (obviously)
- [ ] **User authentication** (so you can save your stuff)
- [ ] **Webhook notifications** (get pinged when scrape is done)

Vote with stars! ⭐

---

## 🤝 Contributing

Found a bug? Want to add a feature? PRs are welcome!

---

## 📝 License

 Do whatever you want with it. Build a startup, make millions, just remember me when you're rich! 💸

---

## 🙏 Acknowledgments (aabhari aahot yaanche)

- **Groq** for the insanely fast LLM API
- **LangChain** for making AI integration not suck
- **Django** for being Django
- **Coffee** for existing ☕
- **Stack Overflow** for... obvious reasons

---

## 📬 Contact

Built by Pratik Ingle !!

- 📧 Email: inglepratik126@gmail.com
- 💼 LinkedIn: [https://www.linkedin.com/in/pratik-ingle-a50589288/]
- 🌐 Portfolio: creating one wait!!

---

## ⚠️ Disclaimer

This tool is for educational purposes. Please:
- ✅ Respect robots.txt
- ✅ Don't overload servers
- ✅ Follow the website's Terms of Service
- ✅ Be a decent human being

Basically, don't be a jerk. The internet is for everyone! 🌍

---

## 💡 Pro Tips

1. **Start with BeautifulSoup mode** - It's faster
2. **Be specific with instructions** - "Get all links" works better than "scrape this"
3. **Check the logs** - They're actually useful!
4. **Use the chat interface** - It's more fun than forms
5. **Star this repo** - It makes me happy 😊

---

## 🔥 Fun Facts

- Powered by caffeine and determination ☕
- 0 lines of PHP (thankfully)
- 100% bug-free* 


*\*bugs may or may not exist*

---

## 🎉 Thank You!

Thanks for checking this out! If you like it:

⭐ Star this repo  
🐛 Report bugs  
💡 Suggest features  
☕ Buy me a coffee (jk... unless?)

Happy Scraping! 🕷️✨

---

**Made with ❤️**

*Now go scrape something!* 
