update: git_up git_up_sub permissions restart

git_up:
	git pull origin master

git_up_sub:
	git submodule update --remote

permissions:
	chown -R www-data:www-data .

restart:
	restart jspasat
