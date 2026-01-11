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


![alt text](image.png)


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