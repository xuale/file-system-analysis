# NAME: Richard Yang, Alexander Xu
# EMAIL: ryang72@ucla.edu, xualexander1@gmail.com
# ID: 704936219, 504966392

default: build

build:
	cp lab3b.py lab3b
	chmod 755 lab3b lab3b.py
dist:
	tar -cvzf lab3b-704936219.tar.gz lab3b.py README
clean:
	rm -f lab3b lab3b-704936219.tar.gz
