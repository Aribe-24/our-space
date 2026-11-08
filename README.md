# 💖 Our Space

A warm, private, mobile-first web app created for **Jojo** and **Jay** to share their days across the miles. Built with Python, Django, SQLite, and vanilla HTML/CSS/JavaScript with zero heavy frontend frameworks.

---

## ✨ Features

1. **"Our Day" Dashboard**:
   - **Side-by-side Local Clocks**: Live clocks for Kampala (Jojo) and London/Jay with context-aware awake and asleep indicators (🌙, ☕, ☀️, 🌆).
   - **Days Together Counter**: Counts elapsed days from your anniversary.
   - **Reunion Countdown**: Live countdown to the next time you see each other.
   - **In-App Quick Editors**: Tap the countdown or your avatar icon to change your city, timezone, anniversary date, or reunion date without touching code.
2. **Daily Check-In**:
   - Pick a mood emoji and write a short *"Today I..."* note.
   - Instantly view your partner's latest mood and note.
3. **"Thinking of You" Button**:
   - One tap triggers a burst of floating hearts on your screen.
   - An animated banner pops up the next time your partner opens the app: *"Jay was thinking of you at 3:42 PM 💕"*.
4. **Question of the Day (Double-Blind Privacy)**:
   - One fun, deep, or romantic question each day (65+ pre-seeded questions).
   - **Double-Blind Reveal**: Your answer remains locked and private until **both** of you have answered!
5. **Photo of the Day**:
   - Upload one photo a day with an optional caption.
   - Shared Polaroid-style memory gallery with full-screen lightbox.
6. **Love Notes Wall**:
   - Shared corkboard of colorful sticky notes (blush, cream, lavender, peach, plum).
   - Pin your favorite notes and inside jokes to the top 📌.
7. **Playful Extras**:
   - **This or That**: Pick options (e.g., *"Morning coffee in bed"* vs *"Late night dessert"*) to see if you match!
   - **Our Soundtrack**: Shared playlist of songs that remind you of each other with direct Spotify / YouTube links.
   - **Our Story**: Key milestones timeline.
8. **Theme & Polish**:
   - Warm pinks, soft cream, and deep plum palette.
   - One-tap **Dark Mode** (intimate plum night theme).
   - Mobile-first bottom navigation dock.

---

## 🚀 Running Locally

### 1. Requirements
- Python 3.10+
- Django 5.x
- Pillow (for photo uploads)

### 2. Setup Virtual Environment & Dependencies
```bash
# Clone or navigate to the directory
cd /path/to/our-space

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install django pillow
```

### 3. Run Migrations & Seed Default Data
```bash
python manage.py migrate
python manage.py setup_our_space
```

This creates:
- **Jojo's Account**: username `jojo` | password `jojolove`
- **Jay's Account**: username `jay` | password `jaylove`
- Seeds 65+ questions, initial love notes, playlist songs, and milestones!

### 4. Run Development Server
```bash
python manage.py runserver
```

Open your browser and visit:  
**`http://127.0.0.1:8000/`** (or `http://localhost:8000/`)

---

## 🌍 Free / Cheap Deployment (For Jojo & Jay)

Because you and Jay live in different countries, here are two simple, beginner-friendly ways to deploy this online so you can both access it from your phones:

### Option A: PythonAnywhere (Easiest & Free)

1. Sign up for a free account at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Go to the **Consoles** tab and start a **Bash** console.
3. Clone your code:
   ```bash
   git clone <your-github-repo-url> our-space
   cd our-space
   python3 -m venv venv
   source venv/bin/activate
   pip install django pillow
   python manage.py migrate
   python manage.py setup_our_space
   ```
4. Go to the **Web** tab:
   - Click **Add a new web app** -> Choose **Manual configuration** -> Select **Python 3.10+**.
   - Set **Virtualenv**: `/home/<username>/our-space/venv`
   - Set **Source code**: `/home/<username>/our-space`
   - In **Static Files**:
     - URL: `/static/` -> Directory: `/home/<username>/our-space/static`
     - URL: `/media/` -> Directory: `/home/<username>/our-space/media`
5. Edit the **WSGI configuration file** (link is on the Web tab):
   ```python
   import os
   import sys

   path = '/home/<username>/our-space'
   if path not in sys.path:
       sys.path.append(path)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
6. Click the green **Reload** button! Your app is live at `https://<username>.pythonanywhere.com`.

---

### Option B: Render.com (Free Tier)

1. Create a `requirements.txt`:
   ```text
   Django>=5.0
   Pillow>=10.0
   gunicorn>=21.0
   ```
2. Create a `render.yaml` or create a new **Web Service** on [render.com](https://render.com) connected to your GitHub repository.
3. **Build Command**:
   ```bash
   pip install -r requirements.txt && python manage.py migrate && python manage.py setup_our_space && python manage.py collectstatic --no-input
   ```
4. **Start Command**:
   ```bash
   gunicorn config.wsgi:application
   ```
5. Add an Environment Variable:
   - `DJANGO_SECRET_KEY`: `<generate-a-random-secret-key>`
   - `DJANGO_DEBUG`: `False`

---

## 🔒 Privacy Notice
This web application is strictly private. There is no registration page. Only the two accounts created via `setup_our_space` (`jojo` and `jay`) or created in the Django admin (`/admin/`) can log in.
