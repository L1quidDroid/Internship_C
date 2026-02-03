# Security Policy

## Vulnerability Disclosure Policy

### Overview

This policy provides security researchers with clear guidelines for conducting vulnerability discovery activities and submitting discovered vulnerabilities to our team.

This policy describes:
- What systems and types of research are covered
- How to submit vulnerability reports
- Expected timeline for disclosure

We encourage responsible disclosure of potential vulnerabilities in our systems.

### Authorisation

If you make a good faith effort to comply with this policy during your security research, we will consider your research to be authorised and will work with you to understand and resolve the issue quickly.

### Research Guidelines

Under this policy, authorised research means activities in which you:

- Notify us as soon as possible after discovering a real or potential security issue
- Only use exploits to the extent necessary to confirm a vulnerability's presence
- Provide us a reasonable amount of time to resolve the issue before disclosing it publicly
- Do not submit a high volume of low-quality reports

### Scope

This policy applies to:
- The Triskele Labs Purple Team Environment codebase
- Official deployment configurations
- Plugin architecture and official plugins
- API endpoints and authentication mechanisms

Out of scope:
- Third-party dependencies (report to upstream maintainers)
- Social engineering or physical security testing
- Denial of service testing without prior approval

### What to Include in Your Report

To help us triage and prioritise submissions, please include:

- Operating system and Python version used
- Description of the vulnerability location and potential impact
- Detailed reproduction steps (proof of concept scripts or screenshots are helpful)
- Suggested remediation if available

Reports in English are preferred but not required.

### Our Commitment

When you share your contact information with us, we commit to coordinating with you as openly and quickly as possible:

- We will acknowledge receipt of your report within 10 business days
- We will confirm the vulnerability's existence and maintain transparent communication about remediation steps
- We will open reported issues to the public within 90 days or after a fix is released, whichever comes first
- We will maintain an open dialogue to discuss issues and challenges
- We will work with you on CVE issuance and ensure proper credit for your contribution

### Responsible Disclosure

Information submitted under this policy will be used for defensive purposes only to mitigate or remediate vulnerabilities. This is an open source project with no commercial backing, therefore there is no bug bounty programme. However, we will ensure appropriate credit is given to researchers who help improve platform security.

## Security Best Practices

When deploying the platform:

- Change all default passwords immediately after installation
- Use strong, unique passwords for all accounts
- Enable TLS/SSL for production deployments
- Restrict network access to required ports only
- Regularly update dependencies and apply security patches
- Use API key authentication for automated integrations
- Implement role-based access control
- Enable audit logging for all operations
- Regularly backup configuration and data
- Review and rotate API keys periodically

## See Also

- [Installation Guide](getting-started/installation.md) - Secure installation procedures
- [Configuration Reference](getting-started/configuration.md) - Security configuration options
- [Deployment Guide](deployment/local-deployment.md) - Production security considerations

