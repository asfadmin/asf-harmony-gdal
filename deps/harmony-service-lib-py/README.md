# harmony-service-lib

A library for Python-based Harmony services to parse incoming messages, fetch data, stage data, and call back to Harmony

## Installing

### Using pip

Install the latest version of the package from the Earthdata Nexus repo using pip:

    $ pip install --extra-index-url https://maven.earthdata.nasa.gov/repository/python-repo/simple/ harmony-service-lib

Or a specific version:

    $ pip install --extra-index-url https://maven.earthdata.nasa.gov/repository/python-repo/simple/ harmony-service-lib==0.0.7

In a requirements.txt file:

```
--extra-index-url https://maven.earthdata.nasa.gov/repository/python-repo/simple/
harmony-service-lib~=0.0.9
```

### Using conda

In a conda environment, you may still use pip to install the harmony service lib, as shown above.
However, in a conda environment.yml file, in addition to the conda dependencies, you can specify
pip dependencies as shown here:

```
dependencies:
  - ...
  - pip:
    - --extra-index-url https://maven.earthdata.nasa.gov/repository/python-repo/simple/
    - harmony-service-lib~=0.0.9
    - ...
```

### Other methods:

The package is installable from source via

    $ pip install git+https://git.earthdata.nasa.gov/scm/harmony/harmony-service-lib-py.git

If using a local source tree, run the following in the source root directory instead:

    $ pip install .

## Usage

Services that want to work with Harmony can make use of this library to ease
interop and upgrades.  To work with Harmony, services must:

1. Receive incoming messages from Harmony.  Currently the CLI is the only
supported way to receive messages, though HTTP is likely to follow.  `harmony.cli`
provides helpers for setting up CLI parsing while being unobtrusive to non-Harmony
CLIs that may also need to exist.
2. Extend `harmony.BaseHarmonyAdapter` and implement the `#invoke` to
adapt the incoming Harmony message to a service call and adapt the service
result to call to one of the adapter's `#completed_with_*` methods. The adapter
class provides helper methods for retrieving data, staging results, and cleaning
up temporary files, though these can be overridden or ignored if a service
needs different behavior, e.g. if it operates on data in situ and does not
want to download the remote file.

A full example of these two requirements with use of helpers can be found in
[example/example_service.py](example/example_service.py)

## Environment

The following environment variables can be used to control the behavior of the
library and allow easier testing:

REQUIRED:

* `STAGING_BUCKET`: When using helpers to stage service output and pre-sign URLs, this
       indicates the S3 bucket where data will be staged
* `STAGING_PATH`: When using helpers to stage output, this indicates the path within
       `STAGING_BUCKET` under which data will be staged
* `ENV`: The name of the environment.  If 'dev' or 'test', callbacks to Harmony are
       not made and data is not staged unless also using localstack
* `OAUTH_UID`, `OAUTH_PASSWORD`: Used to acquire a shared EDL token
       needed for downloading granules from EDL token-aware data
       sources. Services using data in S3 do not need to set this.

       NOTE: If `FALLBACK_AUTHN_ENABLED` is set to True (CAUTION!)
       these credentials will be used to download data *as* the EDL
       application user. This may cause problems with metrics and can
       result in users getting data for which they've not approved a
       EULA.
* `OAUTH_CLIENT_ID`: The Earthdata application client ID.
* `OAUTH_HOST`: Set to the correct Earthdata Login URL, depending on
       where the service is being deployed. This should be the same
       environment where the `OAUTH_*` credentials are valid. Defaults
       to UAT.
* `OAUTH_REDIRECT_URI`: A valid redirect URI for the EDL application.
* `SHARED_SECRET_KEY`: The 32-byte encryption key shared between Harmony and backend services.
       This is used to encrypt & decrypt the `accessToken` in the Harmony operation message.
       In a production environment, this should be injected into the container running the service
       Docker image. When running the service within Harmony, the Harmony infrastructure will
       ensure that this environment variable is set with the shared secret key, and the Harmony
       service library will read and use this key. Therefore, the service developer need not
       be aware of this variable or its value.

OPTIONAL:

* `APP_NAME`: Defaults to first argument on commandline. Appears in log records.
* `AWS_DEFAULT_REGION`: (Default: `"us-west-2"`) The region in which S3 calls will be made
* `USE_LOCALSTACK`: (Development) If 'true' will perform S3 calls against localstack rather
       than AWS
* `LOCALSTACK_HOST`: (Development) If `USE_LOCALSTACK` `true` and this is set, will
       establish `boto` client connections for S3 & SQS operations using this hostname.
* `TEXT_LOGGER`: (Default: True) Setting this to true will cause all
       log messages to use a text string format. By default log
       messages will be formatted as JSON.
* `HEALTH_CHECK_PATH`: Set this to the path where the health check file should be stored. This
       file's mtime is set to the current time whenever a successful attempt is made to to read the
       message queue (whether or not a message is retrieved). This file can be used by a container's
       health check command. The container is considered unhealthy if the mtime of the file is old -
       where 'old' is configurable in the service container. If this variable is not set the path
       defaults to '/tmp/health.txt'.

OPTIONAL -- Use with CAUTION:

* `FALLBACK_AUTHN_ENABLED`: Default: False. Enable the fallback authentication that
  uses the EDL application credentials. See CAUTION note above.
* `EDL_USERNAME`: The Earthdata Login username used for fallback authn.
* `EDL_PASSWORD`: The Earthdata Login password used for fallback authn.

## Development Setup

Prerequisites:
  - Python 3.7+, ideally installed via a virtual environment such as `pyenv`
  - A local copy of the code

Install dependencies:

    $ make develop

Run linter against production code:

    $ make lint

Run tests:

    $ make test

Build & publish the package:

    $ make publish

## Releasing

Update the CHANGELOG with a short bulleted description of the changes
to be built & deployed. Replace `DATE` with the date on which the
feature will be released.

NOTE: Currently the service library Python package is versioned
by the Bamboo build number, and it only increments the patch version
of the library. Unless the base version of the Bamboo job is updated,
the resulting Python package version will not follow semantic
versioning. If a change requires a minor or major version number
increment, update the Bamboo job which builds the Python package (see
below) so that the base version of the newly-built package is correct.

New entries to the CHANGELOG should be of the form:

```
## DATE

Changes:

* Now uses a flux capacitor in the hydro-flange motivator circuit
* Tastes better & is less filling than previous release
```

The [Harmony Python Service Library Bamboo Build](https://ci.earthdata.nasa.gov/browse/HARMONY-PSL)
will be triggered on commits pushed to the
[BitBucket repo](https://git.earthdata.nasa.gov/projects/HARMONY/repos/harmony-service-lib-py/browse).
New versions of the Python package artifact will then be pushed to the [Earthdata Nexus Repository](https://maven.earthdata.nasa.gov/#browse/browse:python-repo:harmony-service-lib). It may then be installed using `pip`.
