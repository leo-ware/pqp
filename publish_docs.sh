#!/usr/bin/bash

cd "python/docs/build" || (echo "fail" && exit)
git init
git add .
git commit -m "deploy"

git branch -M gh-pages
git remote add origin https://github.com/leo-ware/capstone
git pull origin gh-pages -s ours --allow-unrelated-histories --no-edit
git push -u origin gh-pages

rm -f -r .git
echo "removed temporary repo"