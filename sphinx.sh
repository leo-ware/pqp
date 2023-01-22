#!/usr/bin/bash

SOURCEDIR="python/pqp/docs/source"
BUILDDIR="python/pqp/docs/build"
PACKAGEDIR="python/pqp"

if [ "$1" = "build" ]; then
    sphinx-build $SOURCEDIR $BUILDDIR
# elif [$1 -eq "livehtml"]; then
#     sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)"
# elif [$1 -eq "autodoc"]; then
#     sphinx-apidoc -f -o "$(SOURCEDIR)" "$(PACKAGEDIR)"
# elif [$1 -eq "buildpush"]; then
#     cd "$(BUILDDIR)"
#     git init
#     git add .
#     git commit -m "deploy"

#     git remote add origin https://github.com/leo-ware/casptone-docs.git
#     git branch -M main
#     git push -u origin main

#     git rm -fr .git
# elif [$1 -eq ""]; then
#     echo "No argument provided. Valid arguments are: build, livehtml, autodoc"
else
    echo "Invalid argument. Valid arguments are: build, livehtml, autodoc, buildpush"
fi