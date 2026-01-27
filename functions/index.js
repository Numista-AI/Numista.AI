const { onRequest } = require("firebase-functions/v2/https");
const logger = require("firebase-functions/logger");
const app = require("./server");

// Create and export the Cloud Function 'app'
// This will handle requests like https://region-project.cloudfunctions.net/app
// and will be the target of our hosting rewrites.
exports.app = onRequest({ region: "us-west1", minInstances: 0 }, app);
