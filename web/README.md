# Optional web interface

Use the Python toolkit on its own, or add the existing Vue / Three.js editor.

## Local development

From the repository root, in the activated Python environment:

```bash
python -m pip install ".[web]"
bcgs serve
```

In another terminal, with Node.js 20+:

```bash
cd web/frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to `http://127.0.0.1:5000`.
Prediction, explanation, optimization, and material choices all use that API.
The modeling interface uses its existing browser workflow; the small packaged graph example can be run through the CLI or `/example` endpoint.

## Configuration

Optional: copy `frontend/env.example` to `frontend/.env.local`.

| Variable | Default | Meaning |
|---|---|---|
| VITE_API_URL | /api | Prediction, explanation, material API |
| VITE_API_URL_OPT | VITE_API_URL | Optional separate optimization API |
| BCGS_API_PROXY | http://127.0.0.1:5000 | Vite development proxy target |

To run the API on another port, use `bcgs serve --port 5002` and change `BCGS_API_PROXY` accordingly.

## Build / hosting

```bash
cd web/frontend
npm run build
```

The result is `web/frontend/dist`. For hosting without a reverse proxy, set `VITE_API_URL=https://your-api.example` before building. `/api` is only automatically proxied by the Vite development server.

The root `vercel.json` targets the new frontend directory. Vercel hosts the frontend, not the PyTorch API. Deploy your backend separately with an appropriate WSGI server. For example, after installing the web extra and gunicorn on a Linux host:

```bash
gunicorn --workers 1 --threads 1 --timeout 300 --bind 0.0.0.0:5000 "bcgs.server:create_app()"
```

The single worker/thread avoids overlapping explanation hooks and expensive model operations. This local toolkit does not provide a job queue, authentication, or multi-user resource management.
