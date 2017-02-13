#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>

int digits10( unsigned long long v ){
    if (v < 10) return 1;
    if (v < 100) return 2;
    if (v < 1000) return 3;
    if (v < 10000) return 4;
    if (v < 100000) return 5;
    if (v < 1000000) return 6;
    if (v < 10000000) return 7;
    if (v < 100000000) return 8;
    if (v < 1000000000) return 9;
    if (v < 10000000000) return 10;
    return 10 + digits10(v / 10000000000);
}

int ll2string(char* dst, size_t dstlen, long long svalue){
    static const char digits[201] =
        "0001020304050607080910111213141516171819"
        "2021222324252627282930313233343536373839"
        "4041424344454647484950515253545556575859"
        "6061626364656667686970717273747576777879"
        "8081828384858687888990919293949596979899";
    int negative;
    unsigned long long value;

    if (svalue < 0) {
        value = -svalue;
        negative = 1;
    } else {
        value = svalue;
        negative = 0;
    }

    int const length = digits10(value)+negative;
    /*check length*/
    if (length >= dstlen) return 0;

    int next = length;
    dst[next] = '\0';
    next--;
    while (value >= 100) {
        const int i = (value % 100) * 2;
        value /= 100;
        dst[next] = digits[i + 1];
        dst[next - 1] = digits[i];
        next -= 2;
    }

    if (value < 10) {
        dst[next] = '0' + value;
    }else{
        const int i = value * 2;
        dst[next] = digits[i + 1];
        dst[next - 1] = digits[i];
    }

    /* Add sign. */
    if (negative) dst[0] = '-';
    return length;
}

/*TEST*/
int main( int argc , char* argv[] )
{
    char buf[128];
    time_t start = time(0);
    printf("程序启动时间：%ld\n", start);

    long long i = 100000000;
    for ( ; i <= 10000000000; ++i){
        ll2string( buf, 128, i );
    //  printf("%s\t", buf);
    }
    time_t end = time(0);
    printf("程序结束时间：%ld\n", end);
    printf("总共用时：%ld\n", (end - start));
}


