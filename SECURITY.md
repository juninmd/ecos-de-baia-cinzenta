# Security Policy

## Supported Versions

Currently, only the main branch (`main`) is supported with security updates. We do not maintain older versions.

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please report it to us privately using GitHub's private vulnerability reporting feature, which can be found under the repository's "Security" tab. If this feature is not available, please email the maintainer. We take all security vulnerabilities seriously and will work to address them promptly.

**Please DO NOT open a public issue for security vulnerabilities.**

## OWASP Top 10 Compliance

This project strives to mitigate common vulnerabilities based on the OWASP Top 10 guidelines:

1. **Broken Access Control:** Environment variables are used for sensitive configurations. API routes and deployments are protected.
2. **Cryptographic Failures:** We do not commit secrets into the repository (`.gitignore` covers `.env`, `.key`, `*.pem`, etc.). HTTPS is enforced in CI/CD deployments.
3. **Injection:** All dependencies are regularly audited (`dependabot`, `pnpm audit`, `pip-audit`). Any dynamic SQL or script executions must be parameterized.
4. **Insecure Design:** Built following the Antigravity protocol for security-by-design. Least privilege principles apply across workflows.
5. **Security Misconfiguration:** Our `dependabot.yml` ensures timely patches. Unused features/frameworks should not be installed in production (`pnpm install --prod` on deployment). Security headers like CSP and HSTS are recommended for the static site hosting layer.
6. **Vulnerable and Outdated Components:** Automated scans with `Dependabot` verify components. We strive to keep `npm` and `pip` dependencies updated to secure versions.
7. **Identification and Authentication Failures:** N/A for static site generator content, but any backend integration must validate all inputs and securely manage tokens via CI secrets.
8. **Software and Data Integrity Failures:** CI pipelines prevent unsafe code integrations. GitHub Actions use pinned or verified actions to ensure integrity.
9. **Security Logging and Monitoring Failures:** All build steps log to standard outputs securely within GitHub Actions to prevent accidental secret leakages.
10. **Server-Side Request Forgery (SSRF):** Any automated fetch commands (e.g. `art_generation`) validate URLs and do not fetch untested or user-supplied endpoints.

## Secure Development Guidelines

* **Never commit secrets:** Always utilize `.env` files for local development and GitHub Secrets for CI/CD environments.
* **Keep dependencies updated:** Regularly review Dependabot PRs.
* **Run tests:** Ensure `PYTHONPATH=. pnpm run test` is executed and passes before any changes are merged.
* **Follow the Antigravity Protocol:** 150-line maximum per file, DRY, KISS, and SOLID principles.
