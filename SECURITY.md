# Security Policy

## Supported versions

Security fixes are provided for the latest release on the `main` branch.

| Version | Supported |
| --- | --- |
| Latest release | Yes |
| Older releases | Best effort |

## Reporting a vulnerability

Please do not disclose a suspected vulnerability in a public issue. Use [GitHub private vulnerability reporting](https://github.com/LittleCurry/oss-doctor/security/advisories/new), or contact the repository owner privately if that feature is unavailable.

Include the affected version, reproduction steps, potential impact, and any suggested mitigation. Do not include real credentials or unrelated personal data. You should receive an acknowledgement within seven days; please allow reasonable time for investigation and a coordinated fix before public disclosure.

## Local security considerations

OSS Doctor is designed to audit only the repository path supplied by the user. Reports can contain local paths and repository findings, so review them before publishing. The CLI does not need and should not be given GitHub tokens for local audits.
