# AI-Driven Auto Investment Platform

## 1. Introduction

Retail investors often face significant challenges while making investment decisions due to the overwhelming volume of financial data, lack of analytical expertise, and difficulty in constructing well-balanced portfolios. Traditional investment tools either require deep financial knowledge or provide limited insights without personalization.

This project proposes an **AI-Driven Auto Investment Platform** that assists users in making informed, data-driven investment decisions by combining **fundamental analysis** with **AI-based quantitative modeling**. The system is designed as a **decision-support framework**, not as a real-time trading system.

---

## 2. Problem Statement

The core problem addressed by this project is:

> **How can an intelligent system assist users in analyzing a large universe of financial assets and generate optimized, risk-aware investment portfolios using AI techniques in an explainable and user-friendly manner?**

Key challenges include:
- Filtering thousands of financial instruments
- Understanding fundamental and quantitative signals
- Constructing diversified portfolios
- Explaining AI-driven decisions clearly to users

---

## 3. Project Objectives

The primary objectives of this project are:

1. To design a modular investment decision system.
2. To reduce a large asset universe into a manageable and relevant subset.
3. To apply AI-based quantitative modeling for asset ranking and portfolio allocation.
4. To generate risk-aware and explainable portfolio recommendations.
5. To present insights through a clean and intuitive user interface.
6. To support experimentation and academic research use cases.

---

## 4. Scope Definition

### 4.1 In Scope

The following features are included in the project scope:

- Historical data-based investment analysis
- Simulation-based portfolio construction
- Multi-engine backend architecture
- Fundamental asset screening
- AI-based quantitative modeling (via Microsoft Qlib)
- Portfolio allocation and rebalancing
- Interactive visualization dashboard
- Academic experimentation and evaluation

---

### 4.2 Out of Scope

The following features are **explicitly excluded**:

- Live trading or brokerage integration
- Real money transactions
- Guaranteed profit claims
- Regulatory or legal compliance automation
- High-frequency or real-time trading systems

This ensures academic safety and ethical compliance.

---

## 5. Target User Persona

**Primary User:**
- Beginner to intermediate investor
- Limited financial expertise
- Interested in AI-assisted insights
- Seeking decision support rather than automation

---

## 6. System Overview

The system follows a **multi-layered, modular architecture** consisting of:

- A web-based user interface
- A backend API server
- A fundamental analysis engine
- An AI-based quantitative engine
- A portfolio allocation engine

The design emphasizes separation of concerns, scalability, and explainability.

---

## 7. High-Level Architecture

<img width="1024" height="1536" alt="image" src="https://github.com/user-attachments/assets/9f488804-869f-466d-9082-5c0c0f1dda13" />

---

## 8. Detailed System Flow

1. User provides investment preferences via the UI.
2. Backend validates and processes the input.
3. Fundamental Engine filters and scores assets.
4. AI Engine predicts returns and ranks assets.
5. Portfolio Engine allocates funds and reserves cash.
6. Results are returned to the UI for visualization.

---

## 9. User Interface Design (Conceptual)

The UI is designed to be **professional, minimal, and data-centric**, inspired by modern fintech platforms.

### Key Screens:
- **Landing Page:** Project overview and system capabilities
- **Input Page:** Investment parameters and preferences
- **Analysis Page:** System processing visualization
- **Portfolio Dashboard:** Allocation charts and metrics
- **Explainability Page:** AI decision rationale
- **Backtesting Page:** Historical simulation results

The goal is to create a strong first impression while maintaining clarity and usability.

---

## 10. Technology Stack (Planned)

### Backend
- Python
- FastAPI / Flask
- Pandas, NumPy
- AI Quant Engine

### Frontend
- Web-based UI (HTML/CSS/JavaScript + React)
- Charting libraries for data visualization

### Deployment
- Web application
- Optional Android APK via WebView

---

## 11. Academic & Research Orientation

This project is designed with academic research in mind and can be extended into a research paper by:

- Evaluating different asset selection strategies
- Comparing AI-based portfolios with benchmarks
- Analyzing risk-adjusted returns
- Documenting architectural and methodological contributions

---

## 12. Stage 1 Completion Summary

At the end of Stage 1, the project has:

- Clearly defined problem and scope
- Well-structured system architecture
- User flow and UI design concepts
- Academic and ethical clarity
- Strong foundation for implementation

**No functional code is implemented at this stage.**

---

---

## Stage 2 — Project Setup & Development Guidelines (For Team Members)

This section explains **how new contributors and teammates should set up the project locally**, understand the structure, and start working safely without breaking the system.

---

## 1. Repository Overview

This project consists of **two independent applications**:

1. **Backend** — Building using FastAPI (Python)
2. **Frontend** — Building using React with Vite (JavaScript)

These two applications communicate using **REST APIs**.

Frontend (React) ⇄ Backend (FastAPI)


They must be run **separately** during development.

---

## 2. Branching Rules (IMPORTANT)

- **Do NOT work directly on `main`**
- Each team member must:
  1. Pull the latest `main`
  2. Create their **own feature branch**
  3. Commit changes only to their branch
  4. Create a Pull Request (PR) to `main`

Example branch names:
- `frontend-dashboard`
- `backend-fundamental-engine`
- `api-portfolio`

---

## 3. Initial Setup (After Cloning / Pulling Main)

### Step 1: Clone the repository (first time only)
```bash
git clone https://github.com/planav/ai-auto-investment
cd AUTOINVEST
```

Or, if already cloned:
```bash
git checkout main
git pull origin main
```

---

## 4. Backend Setup (FastAPI)

### 4.1 Navigate to backend
```bash
cd backend
```

### 4.2 Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4.3 Run the backend server
```bash
uvicorn app.main:app --reload
```

### 4.4 Verify backend is running

Open in browser:

**Health check:**
```
http://127.0.0.1:8000/health
```

**API documentation (Swagger UI):**
```
http://127.0.0.1:8000/docs
```

If these work, backend setup is successful.

---

## 5. Frontend Setup (React)

### 5.1 Navigate to frontend
```bash
cd frontend/web
```

### 5.2 Install frontend dependencies
```bash
npm install
```

### 5.3 Run frontend development server
```bash
npm run dev
```

### 5.4 Verify frontend is running

Open in browser:
```
http://localhost:5173
```

You should see the base React application.

---

## 6. Project Structure Explanation

### Backend (backend/)
```
backend/
├── app/
│   ├── main.py        # Application entry point
│   ├── api/           # API routes
│   └── core/          # Configuration & utilities
├── requirements.txt   # Python dependencies
```

### Frontend (frontend/web/)
```
frontend/web/
├── src/
│   ├── pages/         # Full pages (Dashboard, Inputs, Results)
│   ├── components/    # Reusable UI components
│   ├── services/      # API calls to backend
│   ├── App.jsx        # Root React component
│   └── main.jsx       # Application entry point
```

---

## 7. Development Rules

- Backend logic goes only inside `backend/`
- Frontend UI goes only inside `frontend/web/`
- Frontend should never directly access data files or models
- All communication must happen via APIs
- Keep commits small and meaningful
- Always test before pushing

---

## 8. Current Stage Status

At this stage:

- ✅ Backend skeleton is running successfully
- ✅ Frontend skeleton is running successfully
- ⏳ No business logic is implemented yet
- ⏳ No AI or data processing is added yet

---