\# MyGenie Backend API



\*\*An Intelligent AI-Powered Personal and Business Assistant\*\*



MyGenie is a Bangla-first, bilingual AI assistant for small businesses with a secure Personal Mode for individual productivity. This is the backend API built with FastAPI.



\---



\## 🎯 Features



\### Authentication \& Security

\- ✅ JWT-based authentication (register, login, refresh)

\- ✅ Secure password hashing (bcrypt)

\- ✅ Server-side authorization

\- ✅ Rate limiting ready



\### Personal Mode

\- ✅ Tasks (CRUD + priority + due dates)

\- ✅ Notes (CRUD + full-text search)

\- ✅ Appointments (CRUD + cancel)

\- ✅ Automatic Personal Workspace on register



\### Business Mode

\- ✅ Business Profile (with hours, policies, delivery info)

\- ✅ FAQs (Bangla + English bilingual)

\- ✅ Products (CRUD + inventory adjustments)

\- ✅ Customers (with consent tracking)

\- ✅ Orders (with lifecycle + server-calculated totals)

\- ✅ Services + Bookings (availability check)

\- ✅ Multi-workspace with RBAC



\### AI Chat

\- ✅ Conversation + Message models

\- ✅ Provider-agnostic AI adapter (Mock, Gemini, OpenAI)

\- ✅ Grounded responses from workspace FAQs

\- ✅ Human handoff workflow



\---



\## 🛠️ Tech Stack



| Layer | Technology |

|---|---|

| \*\*Framework\*\* | FastAPI |

| \*\*Database\*\* | PostgreSQL 18 |

| \*\*ORM\*\* | SQLAlchemy 2.x |

| \*\*Migrations\*\* | Alembic |

| \*\*Authentication\*\* | JWT (python-jose) |

| \*\*Password Hashing\*\* | bcrypt (passlib) |

| \*\*Validation\*\* | Pydantic v2 |

| \*\*AI Providers\*\* | Mock, Google Gemini, OpenAI |

| \*\*Server\*\* | Uvicorn |



\---



\## 📋 Prerequisites



Before running this project, ensure you have:



\- \*\*Python\*\* 3.11+ (\[Download](https://www.python.org/downloads/))

\- \*\*PostgreSQL\*\* 15+ (\[Download](https://www.postgresql.org/download/))

\- \*\*Git\*\* (\[Download](https://git-scm.com/downloads))



\---



## Setup Instructions

Clone the repository, create a virtual environment, and install the dependencies:

```bash
git clone https://github.com/iftiurhossenriyad/mygenie.git
cd mygenie/backend
python -m venv venv
```

Activate the virtual environment, install dependencies, copy `.env.example` to
`.env`, and configure PostgreSQL and a random `SECRET_KEY`. Then run:

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

For hosted deployment, use the repository-level [deployment guide](../DEPLOYMENT.md).
