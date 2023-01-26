#!/usr/bin/bash

SOURCEDIR="python/pqp/docs/source"
BUILDDIR="python/pqp/docs/build"
# PACKAGEDIR="python/pqp"

if [ "$1" = "build" ]; then
    sphinx-build $SOURCEDIR $BUILDDIR
elif [ "$1" = "livehtml" ]; then
    sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)"
elif [ "$1" = "autodoc" ]; then
    sphinx-apidoc -f -o "$(SOURCEDIR)" "$(PACKAGEDIR)"
elif [ "$1" = "deploy" ]; then
    cd "$(BUILDDIR)" || exit
    git init
    git add .
    git commit -m "deploy"

    git branch -M gh-pages
    git remote add origin https://github.com/leo-ware/capstone
    git pull origin gh-pages -s ours --allow-unrelated-histories --no-edit
    git push -u origin gh-pages

    rm -f -r .git
elif [ "$1" = "" ]; then
    echo "No argument provided. Valid arguments are: build, livehtml, autodoc"
else
    echo "Invalid argument. Valid arguments are: build, livehtml, autodoc, buildpush"
fi