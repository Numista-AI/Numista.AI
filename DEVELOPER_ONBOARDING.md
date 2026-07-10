# Numista.AI — Developer Onboarding Playbook

This document describes how to set up the development environment, run the components locally, and contribute safely.

---

## 📋 Prerequisites

Before starting, ensure you have the following installed on your development machine:
1. **Flutter SDK** (Channel: `stable`, version 3.22+ recommended)
2. **Node.js** (v18+ or v20+)
3. **Python** (v3.10 or v3.11)
4. **Git**
5. **Firebase CLI** (`npm install -g firebase-tools`)
6. **SQLite** (for working with local catalogs)

---

## 🏗️ Local Environment Setup

### 1. Backend Python Setup (`numista_backend/`)
Navigate to `numista_backend` and initialize the virtual environment:
```bash
cd numista_backend
python -m venv .venv
# Activate in Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Activate in Bash/macOS:
source .venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```
To run the FastAPI server locally:
```bash
python main.py
```

### 2. Frontend Flutter Setup (`numista_mobile/`)
Navigate to `numista_mobile` and get packages:
```bash
cd numista_mobile
flutter pub get
```
To run the web app in debug mode:
```bash
flutter run -d chrome
```

### 3. Admin Portal Next.js Setup (`numista_admin/`)
Navigate to `numista_admin` and install packages:
```bash
cd numista_admin
npm install
```
To start the development server:
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the portal.

---

## 🔒 Credentials & Configuration

To connect the backend and frontend to Google Cloud/Firebase services, copy the credentials:
- **Service Account Key**: Place `serviceAccountKey.json.json` in `numista_backend/`.
- **Environment Variables**: Create a `.env` file in `numista_backend/` following `.env.example`.
- **Firebase Config**: Run `firebase login` and choose the target project `studio-9101802118-8c9a8`.

---

## 🚀 Sandbox Testing & Verification

### Deploying a Sandbox Preview
To test UI changes without pushing code to GitHub and without impacting the production site, deploy to a Firebase Hosting preview channel:

1. **Build the web application**:
   ```bash
   cd numista_mobile
   flutter build web --release
   ```
2. **Deploy to a preview channel**:
   ```bash
   firebase hosting:channel:deploy wishlist-redesign --site numista-vault
   ```
This command generates a secure, temporary live URL (active for 7 days) that you can share with the team for review.

---

## 🛑 Git & Deployment Safety Rules

* **Branching Strategy**:
  - Make all code modifications on the `dev` branch or an agent feature branch (e.g. `agent/feature-name`).
  - **NEVER** push code changes directly to the `main` branch. Pushing to `main` deploys to the live production site (`numista-vault.web.app`) and requires explicit owner approval.
* **Auto-Generated and Temp Files**:
  - Never stage or commit `scratch/`, `output/`, `*.db`, or local caching files. They are Git-ignored.
