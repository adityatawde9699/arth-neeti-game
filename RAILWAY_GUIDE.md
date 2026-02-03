# Arth-Neeti Railway Deployment Guide

This guide will help you deploy the Arth-Neeti game (Backend + Database + Frontend) to [Railway.app](https://railway.app/).

## Prerequisites
1.  A GitHub account with this repository pushed to it.
2.  A [Railway](https://railway.app/) account (GitLab/GitHub login recommended).

---

## Part 1: Create Project & Database

1.  Log in to Railway and click **"New Project"**.
2.  Select **"Provision PostgreSQL"**.
3.  This will create a new project with a Postgres database service.
4.  Click on the **PostgreSQL** card.
6.  **Copy Connection String**:
    *   Go to the **Variables** tab of the PostgreSQL service.
    *   Copy the `DATABASE_URL` value (it looks like `postgresql://postgres:password@host:port/railway`).
    *   **Tip**: You will paste this into the Backend Service's variables in the next part.

---

## Part 2: Deploy Backend

1.  In the same project, click **"New"** (top right) -> **"GitHub Repo"**.
2.  Select your `Arth-Neeti` repository.
3.  Click **"Add Variables"** before deploying (or go to specific service settings later).
4.  **Configure Variables**:
    *   `PORT`: `8000`
    *   `SECRET_KEY`: (Generate a long random string)
    *   `DEBUG`: `False`
    *   `ALLOWED_HOSTS`: `*` (or your specific railway domain later)
    *   `DATABASE_URL`: (Paste the value from Part 1)
    *   `CSRF_TRUSTED_ORIGINS`: `https://your-frontend-url.vercel.app` (You can update this *after* deploying frontend, for now put `https://*`)
    *   `DISABLE_COLLECTSTATIC`: `0`

5.  **Configure Settings**:
    *   **Root Directory**: `/backend` (Important! Set this in Settings -> Root Directory)
    *   **Build/Start Commands**: Leave these **EMPTY** or default. Railway will use the `Dockerfile` I updated.
        *   *Note*: The `Dockerfile` now handles `collectstatic`, migrations, seeding, and starting the server automatically.
        *   If you entered commands previously, please **remove them**.

6.  **Deploy**: Click Deploy.
7.  **Generate Domain**:
    *   Go to **Settings** -> **Networking**.
    *   Click **"Generate Domain"**.
    *   Copy this URL (e.g., `web-production-1234.up.railway.app`).

---

## Part 3: Deploy Frontend

1.  Click **"New"** -> **"GitHub Repo"** (Select the same repo again).
2.  **Configure Variables**:
    *   `VITE_API_URL`: Paste the Backend URL from Part 2 (e.g., `https://web-production-1234.up.railway.app/api`)
        *   **Important**: Add `/api` at the end if your backend routes are prefixed with it, but looking at your code, the base URL is usually just the host. Check `frontend/src/api/index.js`. It appends endpoints like `/start-game/`. So if your backend URL is `https://xyz.railway.app`, `VITE_API_URL` should be `https://xyz.railway.app/api`.

3.  **Configure Settings**:
    *   **Root Directory**: `/frontend` (Important!)
    *   **Build Command**: `npm install && npm run build`
    *   **Start Command**: `npm start`
    *   **Output Directory**: `dist`

4.  **Deploy**: Click Deploy.
5.  **Generate Domain**:
    *   Go to **Settings** -> **Networking**.
    *   Click **"Generate Domain"**.

---

## Part 4: Final Connection

1.  Copy your **Frontend Domain** (e.g., `https://frontend-production.up.railway.app`).
2.  Go back to your **Backend Service** -> **Variables**.
3.  Update `CSRF_TRUSTED_ORIGINS` to include your frontend domain: `https://frontend-production.up.railway.app`.
4.  Update `ALLOWED_HOSTS` if you restricted it.
5.  Redeploy the backend (Railway often auto-redeploys on variable changes).

## Part 5: Initialize Data (Seeding)

To seed the scenarios:
1.  Install the Railway CLI (optional) or use the simplified method:
2.  Update the **Backend Build Command** temporarily to include seeding:
    `pip install -r backend/requirements.txt && python backend/manage.py migrate && python backend/manage.py seed_scenarios`
3.  Redeploy.
4.  Once deployed and seeded, remove the seed command to prevent re-seeding on every deploy.

Success! Your game should now be live.
