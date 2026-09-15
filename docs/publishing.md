# Publishing releases

This is how this package is published to [PyPI](https://pypi.org/project/discord-build-number-scrapper/)
from GitHub Actions.

Thanks to
[uv-dynamic-versioning](https://github.com/ninoseki/uv-dynamic-versioning/),
the [`release.yml`](https://github.com/MFDI-hub/discord_build_number_scrapper/blob/main/.github/workflows/release.yml)
workflow (semantic-release), and the [`publish.yml`](https://github.com/MFDI-hub/discord_build_number_scrapper/blob/main/.github/workflows/publish.yml)
workflow, tagged GitHub Releases publish the matching version to PyPI.

You can release in either way:

1. **Automatic (recommended):** push Conventional Commits to `main`/`master`. The
   semantic-release workflow creates a GitHub Release + `vX.Y.Z` tag when commits warrant
   a bump. That release triggers `publish.yml`.
2. **Manual:** create a tagged release yourself in the GitHub UI or with `gh` (below).

Local alternative: `scripts/publish.py` can `uv build` and upload with twine using tokens
from `.env` (`TEST_PYPI_API_TOKEN`, `PYPI_API_TOKEN`). CI trusted publishing is preferred.

### First-time setup

These steps assume the GitHub repo already exists. The package name on PyPI is
`discord_build_number_scrapper`.

1. **Get a PyPI account** at [pypi.org](https://pypi.org/) and sign in.

2. **Authorize** this repository to publish to PyPI:

   - Go to [the publishing settings page](https://pypi.org/manage/account/publishing/).

   - Find “Trusted Publisher Management” and register the GitHub repo as a trusted
     publisher (or complete a pending one).

   - Project name: `discord_build_number_scrapper`
   - Owner: `MFDI-hub`
   - Repository: `discord_build_number_scrapper`
   - Workflow name: `publish.yml` (leave environment name blank unless you configured one)

3. **Create a first release** so versioning starts on `0.x` (optional but recommended
   if no tags exist yet):

   semantic-release’s first release is `1.0.0` if no tags exist. To stay on `0.x`, create
   an initial tag once after setup:

   ```shell
   git tag v0.1.0
   git push origin v0.1.0
   gh release create v0.1.0 --generate-notes
   ```

   Later bumps follow Conventional Commits automatically.

4. **Confirm it publishes to PyPI**

   - Watch for the publish workflow in the GitHub Actions tab.

   - If it succeeds, the package appears at
     [https://pypi.org/project/discord-build-number-scrapper/](https://pypi.org/project/discord-build-number-scrapper/).

### Publishing subsequent releases

Follow this checklist for each new release.

#### Pre-release checklist

1. **Verify all changes are committed and pushed:**

   ```shell
   git status
   git log origin/main..HEAD  # should be empty if pushed
   ```

2. **Run linting and tests locally:**

   ```shell
   make lint
   make test
   ```

3. **Confirm CI is passing:**

   ```shell
   gh run list --limit 3
   ```

   Or check the Actions tab on GitHub.

4. **Determine the new version number** (manual releases only):

   ```shell
   gh release list --limit 1
   ```

   Use [semantic versioning](https://semver.org/) / Conventional Commits:

   - **fix:** → patch (e.g. `v0.5.8` → `v0.5.9`)
   - **feat:** → minor (e.g. `v0.5.9` → `v0.6.0`)
   - **BREAKING CHANGE** / `!` → major (e.g. `v0.6.0` → `v1.0.0`)

#### Create the release

5. **Automatic:** merge Conventional Commits to `main` and let `release.yml` create the
   GitHub Release.

6. **Manual — create the release with `gh`:**

   ```shell
   NEW_TAG="vX.Y.Z"  # Replace with actual version
   LAST_TAG=$(gh release list --limit 1 --json tagName -q '.[0].tagName')

   gh release create "${NEW_TAG}" \
     --title "${NEW_TAG}" \
     --notes "$(cat <<'EOF'
   ## What's Changed

   [Summarize changes here--see format guide below]

   ### Full Changelog

   https://github.com/MFDI-hub/discord_build_number_scrapper/compare/${LAST_TAG}...${NEW_TAG}
   EOF
   )"
   ```

   Alternatively, use `--generate-notes` for GitHub’s auto-generated notes, or
   `--notes-file FILENAME` to read from a file.

7. **Verify the release published successfully:**

   ```shell
   # Check the release workflow:
   gh run list --workflow=publish.yml --limit 1
   ```

   Then confirm on PyPI (may take a minute):
   [https://pypi.org/project/discord-build-number-scrapper/](https://pypi.org/project/discord-build-number-scrapper/)

### Release notes format

Use this structure for release notes (manual releases):

```markdown
## What's Changed

### Bug Fixes

**Short title of fix**

Description of what was fixed and why it matters.

### New Features

**Short title of feature**

Description of the new capability.

### Breaking Changes

**Short title of breaking change**

Description of what changed and how to migrate.

### Full Changelog

https://github.com/MFDI-hub/discord_build_number_scrapper/compare/vPREVIOUS...vNEW
```

Guidelines:

- Use `## What's Changed` as the top-level heading.

- Group changes under `### Bug Fixes`, `### New Features`, `### Breaking Changes`, etc.
  as appropriate.

- Use `**bold**` for short titles of individual changes.

- Include technical details only when helpful for users.

- Always include the Full Changelog compare link at the end.

- For small releases, a simple bullet list is acceptable instead of full sections.
