# build the docs
cd python/pqp/docs/
make build

# new fake git repo
cd build
git init
git add .
git commit -m "deploy"

# push to gh-pages branch
git push https://github.com/leo-ware/capstone gh-pages -f

# remove fake git repo
rm -fr .git