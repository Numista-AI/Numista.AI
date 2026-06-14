# Legacy Vault Audit: Numista.AI Architecture

## 1. Data Storage
The legacy application utilizes a "hybrid" storage approach rather than traditional REST API endpoints or raw JSON files.

- **Primary Cloud Storage (Firestore):** The actual coin collections are stored in Google Cloud Firestore. The data is organized linearly by email address: `users/{user_email}/coins`. Other supporting collections include `wishlist`, `review_queue`, and `staging_area`.
- **Local Numismatic Data (SQLite):** There is a local 925KB database located at `database/numista_coins.db`. This is used as a reference catalog to map colloquial terms (like "Lincoln Cent") to official Numista database identifiers.
- **Media Vault (Cloud Storage):** Uploaded files, queues, and documents are pushed directly to a Google Cloud Storage bucket (`numista-uploads-studio-9101802118-8c9a8`).

## 2. Management Logic
The legacy application is built as a monolithic **Python Streamlit** application. 

- **Location of Logic:** All business logic for 'Adding', 'Editing', 'Deleting', and 'Sorting' is embedded directly into the 3,800+ line UI file: `app.py`.
- **Architecture Flow:** There is no distinct "backend". The application uses Server-Side UI rendering where button clicks immediately trigger Google Cloud Server SDK methods (`db.collection().set()`, `batch.delete()`, etc.) mixed in alongside HTML/CSS layout definitions.
- **Authentication:** It bypasses standard client security by using application-default privileged credentials alongside Firebase Admin SDK (`firebase_admin.auth`), essentially acting as an all-powerful super-admin on the backend.

## 3. The Migration Bridge
**Good News:** The data structure **DOES NOT** need to be refactored. We can keep the data exactly as-is and avoid any massive data migrations!

- **Flutter Integration:** Flutter has first-party support for Firebase via the `cloud_firestore` package. We can simply point the new Flutter UI directly to `Firestore -> users/{email}/coins`.
- **Refactoring Requirement:** Because the legacy CRUD logic was deeply entangled inside the Python UI (`app.py`), we cannot reuse the Python functions. We will need to rewrite the data "Repositories" in Dart (Flutter) to securely handle the 'Add', 'Edit', and 'Delete' operations directly from the mobile/desktop app.
- **Security Note:** The current database rules (`firestore.rules`) are completely open (`allow read, write: if true;`). For now, this makes the Flutter bridge incredibly easy to set up. However, as we establish the Flutter framework, we should securely lock this to authenticated users.

> [!TIP]
> **Next Steps**
> Because the data lives in Firestore, establishing the bridge in Flutter simply means importing the `cloud_firestore` package, grabbing the user's email, and subscribing to their specific collection path. 
