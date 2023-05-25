# How to prepare new DUNES release?

## How to generate a package on Windows?
1. Edit `packaging\dunes\dunes.nuspec` and edit the current version in XML tag `version`
2. If you do not have yet [Chocolatey](https://chocolatey.org/) installed open Windows console as administrator.
Otherwise you can open Windows console as a regular user.
3. Go to `packaging` directory and run `generate_chocolatey.bat` (if you run it for the first time then Chocolatey will be installed)
4. `*.nupkg` file will be created in your current directory


## How to prepare new DUNES docker image?
1. Ensure `src/dune/version.py` contains the correct version information.
2. Make sure you are logged in with docker login, example command: `docker login ghcr.io -u <your_username> --password-stdin`.
3. Update `VERSION_SUFFIX` if necessary in `packaging/generate_package.sh`/
4. Update `RELEASE` in `packaging/generate_deb.sh` and `packaging/generate_rpm.sh` if necessary. (This is the package version, not the executable version.)
5. Run `./bootstrap.sh --release --push` in your DUNES directory.
