# Contributing

We would love your help in maintaining and improving this project.

## Environment Setup

- Before committing code, install [`pre-commit` hooks](https://pre-commit.com/)
  with `pre-commit install`. We run `isort`, `black`, and `mypy`.

- To run the tests, run `tox` in the root directory. PostgreSQL must be installed.
  To debug unit tests, run `tox -- --pdb` to drop into the debugger upon failure.

## Submit Your Code

To submit your code, [fork the repository](https://help.github.com/en/articles/fork-a-repo),
[create a new branch](https://help.github.com/en/desktop/contributing-to-projects/creating-a-branch-for-your-work),
and [open a Pull Request](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork)
when your work is ready for review.
