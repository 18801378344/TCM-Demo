# Temporary Render deployment

Submitted archive SHA-256: `a0ee9fe4ca854ba1a3ccece4626d446d09f9bd444539ca4462d1db3bc4268724`

This directory preserves every file from the submitted archive byte-for-byte. Additional deployment files supply PostgreSQL configuration, Gunicorn serving and two non-admin review accounts. This is a deployment derivative, not a claim that the deployed package is byte-identical to the ZIP.

## Steps
1. Register/sign in at https://dashboard.render.com/ and connect a GitHub repository containing these files at its root. Do not upload passwords or a live database.
2. Create a Blueprint from the repository's `render.yaml`. Confirm both resources use the Free plan; do not upgrade or add paid resources without choosing to do so.
3. Supply two different randomly generated passwords (at least 16 characters) as secret environment variables `DEMO_PASSWORD_1` and `DEMO_PASSWORD_2`. Share them privately with the reviewers, not in the repository. Username values are `reviewer1` and `reviewer2`.
4. Wait for successful deployment and copy the actual HTTPS URL from Render. Do not guess the URL.
5. Verify login with both accounts, valid/invalid CSV import and cross-account access denial. Record the deployed Git commit from Render and send it together with the original ZIP hash.
6. State a concrete availability date after deciding the interview period, and delete both resources afterwards.

The free service sleeps after 15 idle minutes; waking can take about a minute. Free PostgreSQL expires after 30 days. Uploaded records use PostgreSQL, not the ephemeral web-service filesystem. These limits must be communicated when sharing the demo.

## Verification status
The original tests must be rerun in the deployment environment. Render/PostgreSQL startup and the public browser workflow are pending account connection. No public URL or live accounts exist yet.

Official guide: https://render.com/docs/deploy-django
Free limits: https://render.com/docs/free
