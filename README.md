# audit-github-actions

## Disclaimer

I would not recommend this solution or approach, as it it unlikely to give complete results in all but the simplest repositories.

Despite not being referenced in any way I can see from the API documentat, [this document outlines current limitations in the code search API](https://docs.github.com/en/search-github/searching-on-github/searching-code), including two specific limitations that render this approach invalid:

- Only repositories that have had activity or have been returned in search results in the last year are searchable.
  - so some potentially large subset of repositories will not be searched.
- At most, search results can show two fragments from the same file, but there may be more results within the file.
  - so longer workflow files with many `uses: ` clauses will only match the first few and ignore the rest.

[I've raised an issue to clearly indicate ALL the limitations of the code search API](https://github.com/github/docs/issues/37124) in, y'know, the code seach API documentation 🤦

In the meantime - I've briefly explored other options.

### Actions policies

I can't see these options in my own `brabster` GitHub org, but I can in my `temperedworks` org. I'm able to allow only specific actions and workflows to execute in my org, so I can effectively disable any actions from a provider that I don't trust. Under `Settings`, in `Actions`, `General`, I can specify only GitHub-provided actions, and a comma-separated list of other providers I trust.

![actions policy page with only github checked and google/aws actions allowed](https://github.com/user-attachments/assets/313ea460-90a0-4d0d-80df-b57250abb891)

I'm not the trusting type, so I wanted to see what happened. I set up a public repo with three workflows - one using only `actions/checkout` (allowed), another using `google-github-actions/setup-gcloud` (allowed) and a third using `azure/setup-helm` (not allowed). Running the workflows...

![the google and github actions ran successfully, the azure one did not](https://github.com/user-attachments/assets/60446121-1596-480b-ad48-bde0707b584d)

The error on the failed action shows it was the actions policies that failed it.

`azure/setup-helm@v4.3.0 is not allowed to be used in temperedworks/workflow-policy-experiments. Actions in this workflow must be: within a repository owned by temperedworks, created by GitHub, or matching the following: aws-actions/*, google-github-actions/*.`

[Here are the official docs for actions policies.](https://docs.github.com/en/enterprise-cloud@latest/admin/enforcing-policies/enforcing-policies-for-your-enterprise/enforcing-policies-for-github-actions-in-your-enterprise#allow-enterprise-and-select-non-enterprise-actions-and-reusable-workflows). It seems that private repositories are only supported in certain payment plans, so that might be a consideration.


## Original README begins

I don't think it's possible to directly check for actions you don't trust at the GitHub search UI, due to limitations in regex support and an inability to combine clauses to operate on the same line rather than in the same file.

This is an attempt at a simple, dependency-free, one-file script to enumerate untrusted GitHub actions in an org. It can help you identify actions that you're not expecting, but is experimental and may not check all repositories. It can help you identify problematic actions, but doesn't offer any guarantees.

You can and probably should double check findings in the GitHub UI. A query to enumerate all examples of `uses:` in the directory tree below `.github` in an org to get you started: `org:brabster path:.github NOT is:fork "uses: "`

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

### Logging

Basic logging is set up and can be controlled by the `LOG_LEVEL` env var. Set to `WARN` to disable rate limit info. Logging will go to the console, and you can redirect just the audit output to a file like this: `python audit_actions.py --org equalexperts > out.txt`

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
