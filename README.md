# EvalTrack: Employee Evaluation System

EvalTrack is a web-based employee evaluation system built using Django (backend API) and a frontend using HTML, Tailwind CSS, and JavaScript.

It allows employees to submit evaluations and managers to review and score them in a centralized system.

---

## 🚀 Features

- Employee login and authentication  
- Role-based access (Employee & Manager)  
- Employee self-evaluation submission  
- Dynamic objective creation and deletion  
- Validation of total objective weights  
- Manager evaluation and scoring  
- Full CRUD operations via API  

---

## 🧠 Architecture

Frontend → API → Django Backend → Database → Response → Frontend

---

## 🛠️ Technologies

- Django, Django REST Framework  
- HTML, Tailwind CSS, JavaScript  
- PostgreSQL  

---

## 📡 API Endpoints

- `/api/employees/`  
- `/api/evaluations/`  
- `/api/evaluations/<id>/`  
- `/api/objectives/`  
- `/api/levels/`  

---

## ⚙️ Setup

```bash
git clone https://github.com/chrisaph/EvalTrack.git
cd EvalTrack

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
