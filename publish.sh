mkdir -p public
rsync -av ./ public --exclude=dot_ssh --exclude=dot_gitconfig --exclude=.git --exclude=public
