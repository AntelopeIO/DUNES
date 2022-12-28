# How to prepare new DUNE release?

1. Make sure you are logged in with docker login, example command: `docker login ghcr.io -u <your_username> --password-stdin`
2. Change version in `packaging/generate_package.sh`
3. Run `./bootstrap.sh` in your DUNE directory
4. Change below `X.Y.Z` to your version and in DUNE directory run:
```
docker tag dune ghcr.io/antelopeio/dune:latest
docker push ghcr.io/antelopeio/dune:latest
docker tag dune ghcr.io/antelopeio/dune:X.Y.Z
docker push ghcr.io/antelopeio/dune:X.Y.Z
```

