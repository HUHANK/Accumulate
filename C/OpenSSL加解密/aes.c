
#include <openssl/aes.h>
#include <openssl/des.h>
#include <stdio.h>
#include <string.h>

#define BSIZE 64

int main(int argc, char **argv)
{
	char filePath[256] = {0};
	char enFilePath[256] = {0};
	char deFilePath[256] = {0};
	unsigned char userKey[128] = {"HuYouLiang"};	
	int i = 0;
	int ret = 0;
	DES_cblock key;
	DES_key_schedule key_schedule;	
	DES_cblock ivec;
	char inBuf[BSIZE] = {0};
	char outBuf[BSIZE] = {0};

	if (argc != 2) {
		printf("Noting to do!\n");
		return 0;
	}
	/*生成一个key*/
	DES_string_to_key(userKey, &key);
	if (DES_set_key_checked(&key, &key_schedule) != 0) {
		printf("convert to key_schedule failed!\n");
		return -1;
	}	
	
	strcpy(filePath, argv[1]);
	strcpy(enFilePath, filePath);
	strcat(enFilePath, ".enc");
	strcpy(deFilePath, filePath);
	strcat(deFilePath, ".dec");	
	
	/*加密*/	
	FILE *srcf = fopen(filePath, "rb");
	if (!srcf) {
		printf("Open file %s error!\n", filePath);
		return 1;
	}
	FILE *enf = fopen(enFilePath, "wb");
	if (!enf) {
		printf("Open file %s error!\n", enFilePath);
        return 1;
	}
	
	memset(inBuf, 0, sizeof(inBuf));	
	ret = fread(inBuf, 1, sizeof(inBuf), srcf);
	while( ret > 0 ) {
		//AES_ecb_encrypt(inBuf,  outBuf, &aes, AES_ENCRYPT);
		memset((char*)&ivec, 0, sizeof(ivec));
		memset(outBuf, 0, sizeof(outBuf));
		DES_ncbc_encrypt(inBuf, outBuf, sizeof(inBuf), &key_schedule, &ivec, DES_ENCRYPT);		
		fwrite(outBuf, 1, sizeof(inBuf), enf);
		memset(inBuf, 0, sizeof(inBuf));	
		ret = fread(inBuf, 1, sizeof(inBuf), srcf);			
	}
	
	fclose(enf);
	fclose(srcf);
	
	/*解密*/
	enf = fopen(enFilePath, "rb");
    if (!enf) {
        printf("Open file %s error!\n", enFilePath);
        return 1;
    }
	FILE *def = fopen(deFilePath, "wb");
	if (!def) {
		printf("Open file %s error!\n", deFilePath);
        return 1;
	}	

	/*	
	ret = AES_set_decrypt_key(userKey, 128, &aes);
	if ( ret < 0 ) {
        printf("AES SET ENCRYPT ERROR!\n");
        return 1;
    }*/

	memset(inBuf, 0, sizeof(inBuf));	
	ret = fread(inBuf, 1, sizeof(inBuf), enf);
	while( ret > 0 ) {
		memset((char*)&ivec, 0, sizeof(ivec));
		memset(outBuf, 0, sizeof(outBuf));
		//AES_ecb_encrypt(inBuf, outBuf, &aes, AES_DECRYPT);
		DES_ncbc_encrypt(inBuf, outBuf, sizeof(inBuf), &key_schedule, &ivec, 0);
		fwrite(outBuf, 1, sizeof(outBuf), def);
		memset(inBuf, 0, sizeof(inBuf));
		ret = fread(inBuf, 1, sizeof(inBuf), enf);
	}

	fclose(enf);
	fclose(def);
		
	return 0;
}
