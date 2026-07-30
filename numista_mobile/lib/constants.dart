// Application-wide constants for Numista.AI.
//
// Centralising the backend URL here means a deployment to a new Cloud Run
// revision (or a staging environment) only needs a single-line edit.

// Base URL of the Numista backend (Cloud Run).
// Every HTTP call in the app should reference this constant rather than
// hardcoding the full Cloud Run URL inline.
//
// Project:  studio-9101802118-8c9a8
// Service:  numista-backend  (revision 00061-lbh, Jun 14 2026)
// Region:   us-central1
const String kApiBaseUrl =
    'https://numista-backend-568985927038.us-central1.run.app';

// Dedicated Cloud Run service for layout recognition, checklist scan, and PDF generation
const String kScanServiceUrl =
    'https://numista-scan-service-568985927038.us-central1.run.app';

// Current application version (aligned with pubspec.yaml)
const String kAppVersion = 'v4.1';
const String kAppVersionFull = 'v4.1.0';

