# assay-watch

Checks https://assay.cascadiantech.com/health every 5 minutes from GitHub Actions and sends the founder a Pushover
alert when the answer is not 200 or the ledger is not `ready`. No state: while Assay is down it alerts on every run.
GitHub documents that scheduled runs can be delayed or skipped under load.

Source of truth: `watcher/` in exquest/assay, where `check.py` is tested.
