To download a lastest standalone binary, you can use the following one-liner:

```bash
pushd . > /dev/null && cd `mktemp -d` && git clone git@github.com:spiricn/DevUtils.git && cd DevUtils && ./archive.sh du_app && popd > /dev/null && cp -v `cd -`/du_app ./
```
