# Migrating from the original repository

| Previous location / behavior | Toolkit release |
|---|---|
| gcn_frontend_app-main/ | web/frontend/ |
| gcn_backend-gpu--main/ | API entry at web/backend/app.py; implementation in src/bcgs/ |
| Separate prediction and optimization servers | `bcgs serve`, one port (5000) |
| Working-directory-relative model / materials | Assets shipped inside the Python package |
| node.xlsx + adjmatrix.xlsx + placeholder energy labels | JSON or the first two Excel files only |
| Custom explanation / perturbation tables | Documented PyG attribute and edge masks |
| Buffered optimization stream | JSON results (`stream: false`) |
| CPU and CUDA environment definitions with different PyTorch versions | One package dependency definition; install the suitable PyTorch build first |

Install `python -m pip install ".[web]"` from the repository root. The old backend scripts and intermediate files remain available in Git history.

For an existing Vercel project, set its root to the repository root to use the updated `vercel.json`, or to `web/frontend` to use the frontend configuration. Set `VITE_API_URL` to your own API's HTTPS address before building. The toolkit changes do not automatically migrate a hosted backend.

The material API now lives at `/materials/wall_select.xlsx` on the same backend. The web interface reads it through the shared API configuration.

Direct checkpoint predictions are regression-tested against the original code. Optimization and explanation outputs have the documented changes above; they should not be compared as if they were identical implementations.
