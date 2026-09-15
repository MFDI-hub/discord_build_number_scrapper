# Security Policy

## Supported versions

Security fixes are provided for the latest release on the default branch (`main` or
`master`). Older releases may not receive patches.

## Reporting a vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report security issues privately to **mfdisanchez@gmail.com**. Include:

- A description of the issue and potential impact
- Steps to reproduce or a proof of concept, if available
- Affected versions or commits

We aim to acknowledge reports within a few business days and will work with you on
a fix and coordinated disclosure when appropriate.

## Dependency updates

Known vulnerable dependencies are monitored in CI via Trivy and `pip-audit`. If you
discover a vulnerable dependency in this project, please include the package name
and advisory ID in your report when possible.
