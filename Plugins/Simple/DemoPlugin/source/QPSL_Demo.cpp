#ifndef __QPSL_DCAM__
#define __QPSL_DCAM__
#include <stdio.h>
#include <stdlib.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef long int32;
#define DLL_EXPORT __declspec(dllexport)

struct DemoTest{
    int height;
    int width;
};

int32 DLL_EXPORT QPSL_ReadImage(DemoTest *test, char* pImage){

}
}
#endif
#endif