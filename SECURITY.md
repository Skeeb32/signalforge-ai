# Security policy

This is a local research demo, not an enterprise-secure service. Do not expose it publicly with the default configuration or put private customer data in the public repository. Configure an authentication gateway, tenant authorization, TLS, retention/deletion rules, encrypted backups and secret rotation before production use.

Report vulnerabilities privately through the repository's GitHub security advisory facility when available; otherwise contact the repository owner privately without posting exploitable secrets. Dependency scans run in CI. Optional API keys use constant-time comparison; strict request schemas, upload/batch limits and rate limiting constrain abuse. Local keys are held in browser session storage; OIDC token handling requires a production redesign.

Joblib/cloudpickle artifacts can execute code. Load only trusted locally trained or verified/signed deployment artifacts. Model-upload endpoints are intentionally absent. MLflow should remain private. The local Redis test server was loopback-only; production Redis needs authentication/TLS/network isolation. No credentials belong in source or Terraform state committed to Git.
