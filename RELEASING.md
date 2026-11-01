# Releasing

This repository is prepared for public release but no registry publication is implied by its presence. Never publish before the matching API and secrets features have passed staging verification. The SDK does not deploy or configure the service.

## GitHub setup (maintainer)

Create an empty **public** repository named runnee-sdk-python under `Runnee-cloud` (or update all repository URLs first). From the prepared SDK folder:

```sh
git init -b main
git add .
git commit -m "Initial public SDK release"
git remote add origin https://github.com/Runnee-cloud/runnee-sdk-python.git
git push -u origin main
```

Review `git diff --cached` before committing. Never upload the parent application repository. Enable GitHub private vulnerability reporting, dependency alerts and branch protection. Create the `pypi` GitHub Actions environment; restrict it to main and require a maintainer review if available for your account. The workflow only publishes when manually requested with publish=true on main. Ordinary pushes and tags run CI only. A manual run with publish=false builds downloadable artifacts without publishing.

## Versioning

Use semantic versioning. Update all version constants and CHANGELOG.md together. Search for the previous version in tracked files, including HTTP User-Agent strings; review the diff and regenerate distribution files. The workflow checks the expected version before building. Once published, treat versioned artifacts as immutable. After publication, tag the exact tested commit `vVERSION` and attach checksums and artifacts to a GitHub release.

## PyPI

1. Confirm `runnee` availability and ownership at https://pypi.org/project/runnee/. A 404 does not reserve the name. If unavailable, select another distribution name and update pyproject.toml and installation documentation consistently.
2. Run the checks in CONTRIBUTING.md, `python -m build`, and `python -m twine check dist/*`. Inspect both the wheel and source archive.
3. In your PyPI account, add a **pending publisher** for project `runnee`: owner `Runnee-cloud`, repository `runnee-sdk-python`, workflow `release.yml`, environment `pypi`. For an existing project, add the same configuration in its Publishing settings.
4. Actions → Release → Run workflow on main; set the expected version and publish=true. Approve the pypi environment job. The workflow publishes the previously built distributions using OIDC; no PyPI token belongs in GitHub secrets.
5. Verify in a clean environment using `pip install runnee==VERSION` and check sync and async imports. Also verify `uv add runnee==VERSION`.

See [PyPI pending publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) and [publishing with OIDC](https://docs.pypi.org/trusted-publishers/using-a-publisher/).
