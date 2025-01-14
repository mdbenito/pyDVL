# Contributing to pyDVL

The goal of pyDVL is to be a repository of successful algorithms for the
valuation of data, in a broader sense. Contributions are welcome from anyone in
the form of pull requests, bug reports and feature requests.

We will consider for inclusion any (tested) implementation of an algorithm
appearing in a peer-reviewed journal (even if the method does not improve the
state of the art, for benchmarking and comparison purposes). We are also open to
improvements to the currently implemented methods and other ideas. Please open a
ticket with yours.

If you are interested in setting up a similar project, consider the template 
[pymetrius](https://github.com/appliedAI-Initiative/pymetrius).

## Local development

This project uses [black](https://github.com/psf/black) to format code and
[pre-commit](https://pre-commit.com/) to invoke it as a git pre-commit hook.
Consider installing any of [black's IDE
integrations](https://black.readthedocs.io/en/stable/integrations/editors.html)
to make your life easier.

Run the following command to set up the pre-commit git hook:

```shell script
pre-commit install
```

## Setting up your environment

We strongly suggest using some form of virtual environment for working with the
library. E.g. with venv:

```shell script
python -m venv ./venv
. venv/bin/activate  # `venv\Scripts\activate` in windows
pip install -r requirements-dev.txt
```

With conda:

```shell script
conda create -n pydvl python=3.8
conda activate pydvl
pip install -r requirements-dev.txt
```

A very convenient way of working with your library during development is to
install it in editable mode into your environment by running

```shell script
pip install -e .
```

In order to build the documentation locally (which is done as part of the tox
suite) you will need [pandoc](https://pandoc.org/). Under Ubuntu it can be
installed with:

```shell script
sudo apt-get update -yq && apt-get install -yq pandoc
```

Remember to mark all autogenerated directories as excluded in your IDE. In
particular `docs/_build` and `.tox` should be marked as excluded to avoid
slowdowns when searching or refactoring code.

If you use remote execution, don't forget to exclude data paths from deployment
(unless you really want to sync them).


## Testing

Automated builds, tests, generation of documentation and publishing are handled
by [CI pipelines](#CI). Before pushing your changes to the remote we recommend
to execute `tox` locally in order to detect mistakes early on and to avoid
failing pipelines. tox will:
* run the test suite
* build the documentation
* build and test installation of the package.
* generate coverage and pylint reports in html, as well as badges.

You can configure pytest, coverage and pylint by adjusting
[pyproject.toml](pyproject.toml).

Besides the usual unit tests, most algorithms are tested using pytest. This
requires ray for the parallelization and Memcached for caching. Please install
both before running the tests. We run [tests in CI](#ci) as well.

It is possible to pass optional command line arguments to pytest, for example to
run only certain tests using patterns (`-k`) or marker (`-m`).

```shell
tox -e base -- <optional arguments>
```

One important argument is `--do-not-start-memcache`. This prevents the test
fixture from starting a new memcache server for testing and instead expects an
already running local server listening on port 11211 (memcached's default port).
If you run single tests within PyCharm, you will want to add this option to the
run configurations.

To test modules that rely on PyTorch, use:

```shell
tox -e torch
```

To test the notebooks separately, run (see [below](#notebooks) for details):

```shell
tox -e notebooks
```

To create a package locally, run:
```shell script
python setup.py sdist bdist_wheel
```

## Notebooks

We use notebooks both as documentation (copied over to `docs/examples`) and as
integration tests. All notebooks in the `notebooks` directory are be executed
during the test run. Because run times are typically too long for large
datasets, you must check for the `CI` environment variable to work
with smaller ones. For example, you can select a subset of the data:

```python
# In CI we only use a subset of the training set
if os.environ.get('CI'):
    training_data = training_data[:10]
```

This switching should happen in a function, not in the notebook: we want to
avoid as much clutter and boilerplate as possible in the notebooks themselves.

Because we want documentation to include the full dataset, we commit notebooks
with their outputs running with full datasets to the repo. The notebooks are
then added by CI to the section
[Examples](https://appliedAI-Initiative.github.io/pyDVL/examples.html) of the
documentation.

### Hiding cells in notebooks

Switching between CI or not, importing generic modules and plotting results are
all examples of boilerplate code irrelevant to a reader interested in pyDVL's
functionality. For this reason we choose to isolate this code into separate
cells which are then hidden in the documentation.

In order to do this, cells are marked with metadata understood by the sphinx
plugin `nbpshinx`, namely adding the following to the relevant cells:

```yaml
metadata: {
  "nbphinx": "hidden"
}
```

It is important to leave a warning at the top of the document to avoid confusion.
Examples for hidden imports and plots are available in the notebooks, e.g. in
[Shapley for data valuation](https://appliedai-initiative.github.io/pyDVL/examples/shapley_basic_spotify.ipynb).


## Documentation

API documentation and examples from notebooks are built with
[sphinx](https://www.sphinx-doc.org/) by tox. Doctests are run during this step.
In order to construct the API documentation, tox calls a helper script that
builds `.rst` files from docstrings and templates. It can be invoked manually
with:

```bash
python build_scripts/update_docs.py
```

See the documentation inside the script for more details. Notebooks are an
integral part of the documentation as well, please read
[the section on notebooks](#notebooks) above.

It is important to note that sphinx does not listen to changes in the source
directory. If you want live updating of the auto-generated documentation (i.e.
any rst files which are not manually created), you can use a file watcher.
This is not part of the development setup of pyDVL (yet! PRs welcome), but
modern IDEs provide functionality for this.

Use the **docs** tox environment to build the documentation the same way it is
done in CI:

```bash
tox -e docs
```

Locally, you can use the **docs-dev** tox environment to continuously rebuild
documentation on changes to the `docs` folder:

```bash
tox -e docs-dev
```

**Again:** this only rebuilds on changes to `.rst` files and notebooks inside
`docs`.

### Using bibliography

Bibliographic citations are managed with the plugin 
[sphinx-bibtex](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/index.html).
To enter a citation first add the entry to `docs/pydvl.bib`. For team
contributor this should be an export of the Zotero folder `software/pydvl` in
the [TransferLab Zotero library](https://www.zotero.org/groups/2703043/transferlab/library).
All other contributors just add the bibtex data, and a maintainer will add it to
the group library upon merging.

To add a citation inside a module or function's docstring, use the sphinx role
`:footcite:t:`. A references section is automatically added at the bottom of
each module's auto-generated documentation.

### Writing mathematics

In sphinx one can write mathematics with the directives `:math:` (inline) or
`.. math::` (block). Additionally, we use the extension 
[sphinx-math-dollar](https://github.com/sympy/sphinx-math-dollar) to allow for
the more common `$` (inline) and `$$` (block) delimiters in RST files.

**Warning: backslashes must be escaped in docstrings!** (although there are
exceptions). For simplicity, declare the string as "raw" with the prefix `r`:

```python
# This will work
def f(x: float) -> float:
    r""" Computes 
    $$ f(x) = \frac{1}{x^2} $
    """
    return 1/(x*x)

# This throws an obscure sphinx error
def f(x: float) -> float:
    """ Computes 
    $$ \frac{1}{x^2} $$
    """
    return 1/(x*x)
```


## CI

We use workflows to:

* Run the tests.
* Publish documentation.
* Publish packages to testpypi / pypi.
* Mark issues as stale after 30 days. We do this only for issues with the label
  [`awaiting-reply`](https://github.com/appliedAI-Initiative/pyDVL/labels/awaiting-reply)
  which indicates that we have answered a question / feature request / PR and
  are waiting for the OP to reply / update his work.

### Tests

We test all algorithms with simple datasets in CI jobs. This can amount to a
sizeable amount of time, so care must be taken not to overdo it:
1. All algorithm tests must be on very simple datasets and as quick as possible
2. We try not to trigger CI pipelines when unnecessary (see [Skipping CI
runs](#skipping-ci-runs)).

### Skipping CI runs

One sometimes would like to skip CI for certain commits (e.g. updating the
readme). In order to do this, simply prefix the commit message with `[skip ci]`.
The string can be anywhere, but adding it to the beginning of the commit message
makes it more evident when looking at commits in a PR.

Refer to the official [GitHub documentation](https://docs.github.com/en/actions/managing-workflow-runs/skipping-workflow-runs) 
for more information.

## Release processes

### Automatic release process

In order to create an automatic release, a few prerequisites need to be
satisfied:

- The project's virtualenv needs to be active
- The repository needs to be on the `develop` branch
- The repository must be clean (including no untracked files)

Then, a new release can be created using the script
`build_scripts/release-version.sh` (leave out the version parameter to have
`bumpversion` automatically derive the next release version by bumping the patch
part):

```shell script
build_scripts/release-version.sh 0.1.6
```

To find out how to use the script, pass the `-h` or `--help` flags:

```shell script
build_scripts/release-version.sh --help
```

If running in interactive mode (without `-y|--yes`), the script will output a
summary of pending changes and ask for confirmation before executing the
actions.

Once this is done, a package will be automatically created and published from CI
to PyPI.

### Manual release process

If the automatic release process doesn't cover your use case, you can also
create a new release manually by following these steps:

1. (Repeat as needed) implement features on feature branches merged into
  `develop`. Each merge into develop will publish a new pre-release version 
   to TestPyPI. These versions can be installed using `pip install --pre 
   --index-url https://test.pypi.org/simple/`.
2. When ready to release: From the develop branch create the release branch and
   perform release activities (update changelog, news, ...). For your own
   convenience, define an env variable for the release version
    ```shell script
    export RELEASE_VERSION="vX.Y.Z"
    git checkout develop
    git branch release/${RELEASE_VERSION} && git checkout release/${RELEASE_VERSION}
    ```
3. Run `bumpversion --commit release` if the release is only a patch release,
   otherwise the full version can be specified using 
   `bumpversion --commit --new-version X.Y.Z release`
   (the `release` part is ignored but required by bumpversion :rolling_eyes:).
4. Merge the release branch into `master`, tag the merge commit, and push back to the repo. 
   The CI pipeline publishes the package based on the tagged commit.
    ```shell script
    git checkout master
    git merge --no-ff release/${RELEASE_VERSION}
    git tag -a ${RELEASE_VERSION} -m"Release ${RELEASE_VERSION}"
    git push --follow-tags origin master
    ```
5. Switch back to the release branch `release/vX.Y.Z` and pre-bump the version:
   `bumpversion --commit patch`. This ensures that `develop` pre-releases are
   always strictly more recent than the last published release version from 
   `master`.
6. Merge the release branch into `develop`:
    ```shell script
    git checkout develop
    git merge --no-ff release/${RELEASE_VERSION}
    git push origin develop
    ```
7. Delete the release branch if necessary: 
   `git branch -d release/${RELEASE_VERSION}`
8. Pour yourself a cup of coffee, you earned it! :coffee: :sparkles:
9. A package will be automatically created and published from CI to PyPI.

### CI and requirements for releases

In order to release new versions of the package from the development branch, the
CI pipeline requires the following secret variables set up:

```
TEST_PYPI_USERNAME
TEST_PYPI_PASSWORD
PYPI_USERNAME
PYPI_PASSWORD
```

The first 2 are used after tests run on the develop branch's CI workflow 
to automatically publish packages to [TestPyPI](https://test.pypi.org/).

The last 2 are used in the [publish.yaml](.github/workflows/publish.yaml) CI
workflow to publish packages to [PyPI](https://pypi.org/) from `develop` after
a GitHub release.

#### Release to TestPyPI

We use [bump2version](https://pypi.org/project/bump2version/) to bump the build
part of the version number, create a tag and push it from CI.

To do that, we use 2 different tox environments:

- **bump-dev-version**: Uses bump2version to bump the dev version,
  without committing  the new version or creating a corresponding git tag.
- **publish-test-package**: Builds and publishes a package to TestPyPI
