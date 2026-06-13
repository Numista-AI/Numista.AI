// Application-wide constants for Numista.AI.
//
// Centralising the backend URL here means a deployment to a new Cloud Run
// revision (or a staging environment) only needs a single-line edit.

// Base URL of the Numista backend (Cloud Run).
// Every HTTP call in the app should reference this constant rather than
// hardcoding the full Cloud Run URL inline.
const String kApiBaseUrl =
    'https://numista-backend-qntvrqvxma-uc.a.run.app';
