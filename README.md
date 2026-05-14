# 🛍️ LUXE STORE — E-Commerce Web App

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask">
  <img src="https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql">
  <img src="https://img.shields.io/badge/Status-Active-green?style=for-the-badge">
</div>

<br>

A full-stack e-commerce web application built with **Flask** and **MySQL**, featuring a sleek dark luxury UI.

---

## ✨ Features

- 🔐 **Authentication** — Register, Login, Logout with hashed passwords (`werkzeug`)
- 🛒 **Shopping Cart** — Session-based cart with AJAX add/remove
- 📦 **Product Catalog** — Filter by category, search by name
- ✅ **Order System** — Checkout with automatic stock updates
- 👤 **User Profile** — Order history and login statistics
- 🌙 **Dark Luxury UI** — Responsive design with gold accents

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/Ahmed-za55/luxe-store.git
cd luxe-store
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup the database
```bash
mysql -u root -p < database.sql
```

### 4. Configure your DB password
In `app.py`, update:
```python
password='YOUR_MYSQL_PASSWORD'
```

### 5. Run the app
```bash
python app.py
```

Visit: **http://127.0.0.1:5000**

---

## 📁 Project Structure

```
luxe-store/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── database.sql            # Database schema & seed data
├── templates/
│   ├── base.html           # Base layout with navbar
│   ├── index.html          # Products page
│   ├── login.html          # Login page
│   ├── register.html       # Register page
│   ├── cart.html           # Shopping cart
│   ├── checkout.html       # Order confirmation
│   └── profile.html        # User profile
└── static/
    └── css/
        └── style.css       # Dark luxury stylesheet
```

---

## 🗃️ Database Schema

| Table | Description |
|-------|-------------|
| `CUSTOMER` | Users with hashed passwords |
| `CUSTOMER_ADDRESS` | Shipping addresses |
| `CATEGORY` | Product categories |
| `PRODUCT` | Products with stock tracking |
| `ORDER` | Customer orders |
| `ORDER_PRODUCT` | Order-product junction table |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | MySQL, mysql-connector-python |
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| Security | werkzeug password hashing, Flask sessions |
| Fonts | Playfair Display, Cairo (Google Fonts) |
| Icons | Font Awesome 6 |

---

## 📸 Pages

- **/** — Product catalog with search & filter
- **/login** — Secure login form
- **/register** — New account creation with validation
- **/cart** — Shopping cart with totals
- **/checkout** — Order confirmation
- **/profile** — User info & order history

---

## 👨‍💻 Developer

**Ahmed Sameh Sharaf**  
Faculty of Artificial Intelligence — Kafrelsheikh University

[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat&logo=github)](https://github.com/yourusername)

---

## 📄 License

MIT License — Free to use and modify.
