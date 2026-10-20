# Validation of the toolkit reorganization

The original checkpoint was preserved. The reference graph and prediction in
`tests/reference.json` were obtained by executing the original repository's
`GCN9.py` and `GraphDataConstruct.py`, before replacing the web backend.

## Executed locally

- Windows, Python 3.10.16, PyTorch 2.8.0.dev20250424+cu128 using CPU, PyG 2.7.0,
  pandas 2.2.3, NumPy 2.2.6.
- 14 automated tests: input formats and validation, original feature order and
  prediction, node-order invariance, explanation masks and RNG preservation,
  optimization reproducibility and exported-candidate prediction, API and CLI.
- The documented 100-epoch explanation and 20-member / 5-generation optimization.
- Wheel construction and installation into a separate package directory;
  prediction and optimization executed with Python isolated mode from outside
  the repository, with the wheel's own model, example, and material files.
- Frontend type checking and production build with Node.js 22.15.0.
- Real HTTP prediction and material download through the Vite `/api` proxy.
- Browser smoke test: the modeling page rendered and a test room was created.

The wheel test reused the machine's installed third-party dependencies. It is
not a fresh download/install verification of every supported Python/OS combination.
The GitHub workflow is provided for future Ubuntu / Python 3.10 and 3.12 checks;
its remote execution is not implied by the local checks.

The browser's subsequent modeling confirmation blocked the automation session.
A complete four-step interactive browser walkthrough has therefore not been
verified in this pass. API-level prediction, explanations, and optimization were
verified separately.

## Scope

The test suite validates packaging and behavior; it does not reproduce the
published training metrics or establish accuracy on a new building dataset.
The frontend production build still reports a large JavaScript chunk, inherited
from the combined Three.js / chart / spreadsheet application.
