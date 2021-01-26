<!-- slug: 2021/trigger-build-with-github-action -->
<!-- published: 2021-01-26 -->

# Building brntn.me when another Github Repo changes using Github Actions

The repository that builds my website ([sesh/brntn.me](https://github.com/sesh/brntn.me)) pulls in content from other repositories. I wanted my site to automatically rebuild any time one of those other repositories is updated.

There's a few examples of how to do this out there, but I wanted to jot down my quick and dirty solution in case it's helpful for anyone else.

We're going to be working with two different repositories here, so lets name them to make things simpler:

- `parent-repo` is the main repository. It should already have a Github Action that builds the site. In my case this is the repository for this website.
- `child-repo` is a second repository that should trigger the build of `parent-repo` on change.

## Step One: Add `repository_dispatch` to your build Github Action for `parent-repo`

In the `on` block of the Github Action that builds your parent project add a new `repository_dispatch` block. The `repository_dispatch` allows calls to the Github API to trigger your action. The `types` list is a list of dispatch types that will be used as triggers, in our case, we're going to add a single `build` type (we'll use this later).

```yaml
on:
  repository_dispatch:
    types:
      - build
```

## Step Two: Generate a Personal Access Token with `repo` permissions

To trigger the build you'll need a Personal Access token that has the `repo` set of scopes. You can create this from the [Developer Settings](https://github.com/settings/tokens) section of your Github settings.

Once created, copy this and keep it safe.

## Step Three: Add the secret to `child-repo`

In the Secrets section of the `child-repo` settings add the token that you just generated as a Repository Secret. I've named mine `NOTIFY_TOKEN` (you'll need this in the next step).

## Step Four: Add the Notify action to `child-repo`

The final step is to add a new action to your `child-repo` that triggers the build. This action uses the `NOTIFY_TOKEN` created above. You'll need to manually update the action with the `parent-repo` name (see placeholder below).

For my projects I've put this in `.github/workflows/notify.yml`:

```
name: Trigger rebuild of parent repo
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  notify:
    runs-on: ubuntu-20.04
    container: alpine/httpie
    steps:
      - name: Notify parent repo
        run: http post https://api.github.com/repos/<<YOUR_PARENT_REPO>>/dispatches "Authorization:token ${{ secrets.NOTIFY_TOKEN }}" event_type=build --ignore-stdin
```

And that's it! When your `child-repo` actions run (and we have it set to run on all pushes) it will trigger a build in the parent repo.
