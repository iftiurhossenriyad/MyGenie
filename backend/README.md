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

\- ✅ Business-mode responses grounded in the business profile, published FAQs, active products, and active services

\- ✅ Personal-mode assistant instructions that do not claim access to personal records

\- ✅ Human handoff workflow

\#### What the AI can answer

In a **business workspace**, MyGenie can answer questions about product names,
descriptions, listed prices and recorded stock; service descriptions, prices
and durations; and business hours, contact details, delivery, and policies.
It uses the current workspace's business profile, active catalog entries, and
published FAQs. Draft FAQs, archived products, and data from other workspaces
are not included in its context.

Examples of supported questions include “এই পণ্যের দাম কত?” / “What is the
listed price?”, “দোকান কখন খোলা?” / “What are your opening hours?”, and “এই
সার্ভিস কতক্ষণ?” / “How long is this service?”. The answer uses the actual
workspace data; it must not make up missing prices, stock, hours, delivery
rules, or policies. Recorded stock is not a live reservation. Chat cannot
create an order or booking or check appointment availability; customers should
use the configured order/booking process or the **Handoff to Staff** control.

In a **personal workspace**, MyGenie can help plan, draft, learn, and organize,
but it cannot read or modify saved tasks, notes, or appointments through chat.

To make business answers accurate, add the real details under the workspace's
Business Profile, add products and services to their catalogs, and create and
publish FAQs for business-specific questions. Do not add fictional prices,
policies, opening hours, or delivery promises as examples in production data.



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
