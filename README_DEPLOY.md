# AXORA — Internet Deployment

This build serves the AXORA frontend and FastAPI backend from one Render Web Service.

## Render settings
- Root Directory: `axora-prototype` (if repository root contains the parent folder)
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn backend_main:app --host 0.0.0.0 --port $PORT`

After deployment, open the generated `https://*.onrender.com` URL.
The frontend calls `/api/...` on the same domain, so no localhost configuration is needed online.

## Demo login
Email: operator@factory.com
Password: AXORA@1234

## Note
The current user store is in memory for the hackathon prototype. It is not persistent across server restarts/redeploys. Google/Microsoft buttons are demo OAuth flows, not real provider OAuth.
