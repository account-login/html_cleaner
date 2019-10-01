#!/usr/bin/env bash

set -ex

mkdir -p dist
rm -rv dist
python3 setup.py sdist bdist_wheel
HTTPS_PROXY='socks5://127.0.0.1:1081' twine upload -u account-login --verbose dist/*
