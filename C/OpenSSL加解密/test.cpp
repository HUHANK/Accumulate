#include <openssl/rsa.h>
#include <openssl/pem.h>
//#include <unistd.h>
#include <iostream>
//#include <io.h>

const char *g_pPubFile = "public.pem";
const char *g_pPriFile = "private.pem";

const int g_nBits = 1024/2;

using namespace std;

int main()
{
	RSA *pRsa = RSA_generate_key(g_nBits,RSA_F4,NULL,NULL);
	if (pRsa == NULL)
   {
    cout << "rsa_generate_key error" << endl;
    return -1;
   }	

	BIO *pBio = BIO_new_file(g_pPubFile,"wb");
	if (pBio == NULL)
   {
    cout << "BIO_new_file " << g_pPubFile << " error" << endl;
    return -2;
   }
	
	if(PEM_write_bio_RSAPublicKey(pBio,pRsa) == 0)
   {
    cout << "write public key error" << endl;
    return -3;
   }
   BIO_free_all(pBio);

	pBio = BIO_new_file(g_pPriFile,"w");
   if (pBio == NULL)
   {
    cout << "BIO_new_file " << g_pPriFile << " error" << endl;
    return -4;
   }
   if(PEM_write_bio_RSAPrivateKey(pBio,pRsa,NULL,NULL,0,NULL,NULL) == 0)
   {
    cout << "write private key error" << endl;
    return -5;
   }
   BIO_free_all(pBio);
   RSA_free(pRsa);
   
	
	return 0;
}
