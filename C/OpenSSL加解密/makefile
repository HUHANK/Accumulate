all: test aes

test: test.cpp 
	g++ test.cpp -lcrypto -o test

aes: aes.c
	gcc -g  aes.c -lcrypto -o aes

clean: aes test
	rm -rf aes test
