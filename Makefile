# NAME: Richard Yang, Alexander Xu
# EMAIL: ryang72@ucla.edu, xualexander1@gmail.com
# ID: 704936219, 504966392

default: build

build:
	gcc -Wall -Wextra -g lab3b.c -o lab3bb
dist:
	tar -cvzf lab3b-704936219.tar.gz lab3b.c README
clean:
	rm -f lab3b lab3b-704936219.tar.gz
