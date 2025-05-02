# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Here are the versions that are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of AcronymMeaning seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report a Security Vulnerability?

Please send a detailed description of the vulnerability to [security@acronymmeaning.com](mailto:security@acronymmeaning.com).

Your report should include:

* Type of vulnerability
* Full path of source file(s) related to the manifestation of the vulnerability
* Location of the affected source code (tag/branch/commit or direct URL)
* Step-by-step instructions to reproduce the vulnerability
* Proof-of-concept or exploit code (if possible)
* Impact of the vulnerability

### Response Process

1. We will acknowledge receipt of your vulnerability report within 48 hours
2. We will assign a primary handler to investigate the report
3. We will keep you informed of the progress towards a fix
4. We will notify you when the vulnerability has been fixed

### Disclosure Policy

* Please do not discuss this security vulnerability publicly until we have had a chance to address it
* We will credit researchers who report security vulnerabilities that we confirm
* We aim to resolve all vulnerabilities within 90 days of responsible disclosure

## Security Best Practices

### API Security

* All API endpoints use HTTPS
* Rate limiting is implemented
* API keys are required for sensitive operations
* Regular security audits are performed

### Data Protection

* All sensitive data is encrypted at rest
* Personal information is handled according to GDPR guidelines
* Regular backups are performed
* Access to production data is strictly controlled

### Sponsor Information

* Sponsor relationships are verified through secure channels
* Changes to sponsor information require multi-factor authentication
* Audit logs are maintained for all sponsor-related changes

### Development Security

* Dependencies are regularly updated
* Security patches are applied promptly
* Code reviews include security considerations
* Automated security scanning is part of our CI/CD pipeline

## Responsible Disclosure

We kindly ask that you:

* Make every effort to avoid privacy violations, degradation of user experience, disruption to production systems, and destruction of data
* Only interact with accounts you own or with explicit permission of the account holder
* Use the minimum amount of data necessary to demonstrate a vulnerability
* Keep confidential any information about vulnerabilities that you've discovered until we've had a chance to address them

## Bug Bounty Program

We currently do not have a bug bounty program, but we greatly appreciate responsible disclosure of security vulnerabilities.

## Contact

For any security-related questions, please contact:
* Email: [security@acronymmeaning.com](mailto:security@acronymmeaning.com)
* PGP Key: [security-pgp.txt](https://acronymmeaning.com/security-pgp.txt)