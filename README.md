### 1. Install Dependencies

```bash
pip install pillow requests
```


> Django will auto-create subfolders like `tryon_results/` and `user_bodies/`, but the root `media/` folder must exist.

---

## ⚙️ Django Setup

### 2. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin User

```bash
python manage.py createsuperuser
```

### 4. Run the Server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🔐 Admin Workflow

1. Go to: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
2. Login with superuser credentials.
3. Add `Category` objects (name + image of clothing).
4. You can optionally create test users or view profiles.

---

## 👤 User Flow

### Step-by-step Instructions

1. Go to: [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login)
2. Log in with an admin-created user.
3. Browse clothing items on the homepage.
4. Click **"Add to Wardrobe"** on any item.
5. Click the **shirt icon (Wardrobe)** in the header to open wardrobe.
6. In the wardrobe:
   - Upload your **full-body image**
   - Click **"Try On"** next to any item to generate a preview
   - Click **"Remove"** to delete clothing from wardrobe

---

## 📸 Image Handling

- Avatar and try-on result images are saved in `media/`:
  ```
  media/
  ├── user_bodies/
  └── tryon_results/
  ```

- New avatar uploads replace old ones.
- New try-on results overwrite older result for that user.
- URLs are cache-busted to prevent old images from appearing.

---

## 🌐 API Integration

Try-On API is called via RapidAPI:

### Configuration

In `views.py`, set your API credentials:

```python
headers = {
    "x-rapidapi-key": "your_api_key_here",
    "x-rapidapi-host": "try-on-diffusion.p.rapidapi.com"
}
```

---


## 🚫 Troubleshooting

- **Old image still appears after upload?**  
  → The app uses timestamp-based cache busting. Confirm your template includes:
  ```html
  <img src="{{ result_url }}?t={{ timestamp }}">
  ```

- **Media files not saving?**  
  → Ensure `media/` folder exists and is writable.

- **404 on `/accounts/profile/`?**  
  → Add `LOGIN_REDIRECT_URL = '/'` in `settings.py`.

---

## ✅ To-Do / Enhancements

-UI Improvement right now only basic HTML
-redirect the sign in account to /login
---


## 🙋‍♂️ Maintainer

**Aditya Pillai**
