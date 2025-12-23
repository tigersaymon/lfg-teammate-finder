# 🎮 LFG Teammate Finder

![Build Status](https://img.shields.io/badge/build-passing-brightgreen) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Django](https://img.shields.io/badge/django-4.2-green) ![HTMX](https://img.shields.io/badge/HTMX-dynamic-orange)

**LFG (Looking For Group)** is a web platform designed to solve the chaos of solo-queue matchmaking. It allows players to find teammates for competitive games like **CS2, Dota 2, and Valorant** by creating structured lobbies with specific roles and rank requirements.

> **Check out the Live Demo:** https://lfg-teammate-finder.onrender.com/

---

## ✨ Key Features

* **🏆 Multi-Game Support:** Scalable architecture supporting various games (CS2, Dota 2, Overwatch, etc.) with game-specific roles.
* **👥 Lobby Management:**
    * Create public or private lobbies.
    * **Slot System:** Lock slots for specific roles (e.g., "Need Sniper" or "Need Support").
    * **Live Updates:** Join, leave, or kick players dynamically without full page reloads (powered by **HTMX**).
* **🔒 Concurrency Safety:** Implemented `select_for_update` and atomic transactions to prevent race conditions (e.g., two users joining the last slot simultaneously).
* **👤 Custom User Profiles:** Users have separate ranks/profiles for each game.
* **🛠 Developer Friendly:** Includes automated scripts to populate the database with games and test data.

## 🛠 Tech Stack

* **Backend:** Python 3, Django 5
* **Database:** SQLite (Dev) / PostgreSQL (Prod)
* **Frontend:** HTML5, Bootstrap 5, HTMX
* **Media Storage:** Cloudinary
* **Deployment:** Render

## 📸 Screenshots

| Lobby List |              Lobby Details               |
|:---:|:----------------------------------------:|
| ![Lobby List](docs/lobby_list.png) | ![Lobby Details](docs/lobby_details.png) |


## 🏗 Database Schema

The project uses a relational database with strict constraints to ensure data integrity.

![DB Schema](docs/db_schema.png)

---

## 🚀 Local Installation & Setup

Follow these steps to get the project running on your local machine in **under 2 minutes**.

### 1. Clone the repository
```bash
git clone [https://github.com/](https://github.com/tigersaymon/lfg-teammate-finder.git
cd lfg-teammate-finder
```

### 2. Set up Virtual Environment
```bash
python -m venv .venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.sample .env
```
Open `.env` and fill in your Cloudinary credentials (required for game icons). Example:
```ini
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

### 5. Apply Migrations
```bash
python manage.py migrate
```

### 6. ⚡ Populate Database (The Magic Step)
Instead of manually creating games and roles, run this custom management command:
```bash
python manage.py setup_dev
```
> **What this does:**
> * Creates games (CS2, Dota 2, Valorant, etc.) and their specific roles.
> * Creates a Superuser (`admin` / `AdminPassword1`).
> * Creates a Test User (`player1` / `PlayerPassword1`).
> * Creates demo lobbies to populate the list.

### 7. Run the Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` to start using the app!

---

## 🧪 Testing

To run the automated test suite (checking auth, lobby logic, and permissions):
```bash
python manage.py test
```

## 🤝 Contributing

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feat/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feat/AmazingFeature`)
5.  Open a Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.