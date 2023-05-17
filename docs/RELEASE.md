# How to prepare new DUNES release?

## How to generate a package on Windows?
1. Edit `packaging\dunes\dunes.nuspec` and edit the current version in XML tag `version`
2. If you do not have yet [Chocolatey](https://chocolatey.org/) installed open Windows console as administrator.
Otherwise you can open Windows console as a regular user.
3. Go to `packaging` directory and run `generate_chocolatey.bat` (if you run it for the first time then Chocolatey will be installed)
4. `*.nupkg` file will be created in your current directory


## How to prepare new DUNES docker image?
1. Make sure you are logged in with docker login, example command: `docker login ghcr.io -u <your_username> --password-stdin`
2. Change version in `packaging/generate_package.sh`
3. Run `./bootstrap.sh` in your DUNES directory
4. Change below `X.Y.Z` to your version and in DUNES directory run:
```
docker tag dunes ghcr.io/antelopeio/dunes:latest
docker push ghcr.io/antelopeio/dunes:latest
docker tag dunes ghcr.io/antelopeio/dunes:X.Y.Z
docker push ghcr.io/antelopeio/dunes:X.Y.Z
```
