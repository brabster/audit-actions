# audit-actions

I don't think it's possible to directly check for actions you don't trust at the GitHub search UI, due to limitations in regex support and an inability to combine clauses to operate on the same line rather than in the same file.

This is an attempt at a simple, dependency-free, one-file script to enumerate untrusted GitHub actions in an org. It can help you identify actions that you're not expecting, but is experimental and may not check all repositories. It can help you identify problematic actions, but doesn't offer any guarantees.

You can and should double check findings in the GitHub UI. A query to enumerate all examples of `uses:` in the directory tree below `.github` in an org to get you started: `org:brabster path:.github NOT is:fork "uses: "`

**This repository is provided without warranty or commitment to maintain. I reserve the right to reject pull requests and issues raised at my discretion.**

## Contributions

Contributions and issues are welcome - please be respecful to all, keep it simple, one standalone script, and no dependencies. Raise an issue first to avoid wasting your time.

I aim for it be straightforward enough that an inexperienced Python user can read it and understand everything that it's doing in a few minutes. Unit tests with several recent versions of Python.

## Usage

The script allows you to specify actions providers that you trust, and filter them out of the results. That makes it much easier to spot what's left. You can specify multiple providers to trust and filter.

### GitHub access tokens

The script requires a GitHub access token in the environment variable `GH_TOKEN`. This is the case even for public repositories as [GitHub does not allow unauthenticated code search](https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-code).

I've not yet found the correct permissions to search private repositories in an org with a fine-grained access token, but it works with a classic token that has full repo permissions. Will update when more minimal permissions are confirmed.

**Don't just trust me! Review the script to satisfy yourself that it is safe for you to run with your GitHub token!**

```console
$ python audit_actions.py --help
usage: audit_actions.py [-h] [-o ORG] [-t TRUSTED]

options:
  -h, --help            show this help message and exit
  -o ORG, --org ORG     GitHub org to query
  -t TRUSTED, --trusted TRUSTED
                        trusted actions provider, may be used more than once
```

### Audit with no trusted providers

```console
$ python audit_actions.py --org brabster
brabster/dbt_materialized_udf: actions/checkout@v4 ".github/workflows/deploy.yml"
brabster/dbt_materialized_udf: google-github-actions/auth@v2 ".github/workflows/deploy.yml"
brabster/pypi_vulnerabilities: actions/setup-python@v5 ".github/actions/setup_dbt/action.yml"
brabster/dbt-adapters-issue-10135: actions/setup-python@v5 ".github/workflows/pip.yml"
brabster/audit-actions: actions/checkout@v4 ".github/workflows/qa.yml"
brabster/audit-actions: actions/setup-python@v5 ".github/workflows/qa.yml"
brabster/dbt_materialized_udf: actions/upload-artifact@v3 ".github/actions/dbt_build/action.yml"
brabster/pypi_vulnerabilities: actions/upload-artifact@v4 ".github/actions/dbt_build/action.yml"
...
```

### Audit with GitHub as a trusted provider

```console
$ python audit_actions.py --org brabster --trust actions
brabster/dbt_materialized_udf: google-github-actions/auth@v2 ".github/workflows/deploy.yml"
brabster/pypi_vulnerabilities: google-github-actions/auth@v2 ".github/workflows/deploy.yml"
brabster/dbt_bigquery_template: google-github-actions/auth@v2 ".github/workflows/deploy.yml"
brabster/dbt_template_demo: google-github-actions/auth@v2 ".github/workflows/deploy.yml"
```

### Audit with Google as a trusted provider

```console
$ python audit_actions.py --org brabster --trust google-github-actions
brabster/dbt_materialized_udf: actions/checkout@v4 ".github/workflows/deploy.yml"
brabster/pypi_vulnerabilities: actions/setup-python@v5 ".github/actions/setup_dbt/action.yml"
brabster/dbt-adapters-issue-10135: actions/setup-python@v5 ".github/workflows/pip.yml"
brabster/audit-actions: actions/checkout@v4 ".github/workflows/qa.yml"
brabster/audit-actions: actions/setup-python@v5 ".github/workflows/qa.yml"
brabster/dbt_materialized_udf: actions/upload-artifact@v3 ".github/actions/dbt_build/action.yml"
...
```

### Audit with both Github and Google as trusted providers

```console
$ python audit_actions.py --org brabster --trust google-github-actions --trust actions
$
```

## Issues

GitHub rate limits calls to the code search API to 10 per minute. I do not handle the 403 error that happens if you hit this limit as I have not had the problem. Happy to look at simple solutions if you need to solve that problem and wish to contribute back.