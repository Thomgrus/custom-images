# docker-size-extractor

This script is an utility script for extracting size used by all tags group by image on a repository docker.

In order to use it you can simply run `docker-size-extractor` with appropriate arguments.

To use it

```shell
docker-size-extractor docker-registry-push.cube-net.org -e
```

This script create 2 files:

* a cache file `${registry}-${date}.json` with information fetch from target docker registry
* a `extracts-${registry}-${date}.json` file a sorted structure by size, number or tags and image

You can reprocess from cache with:
```shell
docker-size-extractor $REGISTRY -c -e -d 20210628
```
