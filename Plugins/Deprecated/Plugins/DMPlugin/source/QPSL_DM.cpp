#ifndef __QPSL_DM__
#define __QPSL_DM__
#include "BmcApi.h"
#if defined(_WIN32)
#include <Windows.h>
#include <conio.h>
#include <iostream>
#define strnlen strnlen_s
#define getch _getch
#endif
#ifdef __cplusplus
extern "C" {
#endif

#define DLL_EXPORT __declspec(dllexport)
typedef const char *(*func_type)(BMCRC);
bool DLL_EXPORT QPSL_BMCErrorString(int code, char *error_info) {
    static func_type func = nullptr;
    if (!func) {
        HINSTANCE hDllInst = LoadLibrary("BMC3.dll");
        if (hDllInst)
            func = (func_type)GetProcAddress(hDllInst, "BMCErrorString");
    }
    if (func) {
        sprintf(error_info, "%s", func(BMCRC(code)));
        return true;
    } else {
        sprintf(error_info, "%s", "failed to load BMC3.dll");
        return false;
    }
}
void deal_error(BMCRC bmcrc, int *error_code, char *error_info) {
    *error_code = bmcrc;
    QPSL_BMCErrorString(int(bmcrc), error_info);
}
bool DLL_EXPORT QPSL_BMCOpen(DM *dm, const char *serial_number, int *error_code, char *error_info) {
    BMCRC bmcrc = BMCOpen(dm, serial_number);
    deal_error(bmcrc, error_code, error_info);
    return bmcrc == NO_ERR;
}
bool DLL_EXPORT QPSL_BMCClose(DM *dm, int *error_code, char *error_info) {
    BMCRC bmcrc = BMCClose(dm);
    deal_error(bmcrc, error_code, error_info);
    return bmcrc == NO_ERR;
}
bool DLL_EXPORT QPSL_BMCLoadMap(DM *dm, uint32_t *map_lut, int *error_code, char *error_info) {
    BMCRC bmcrc = BMCLoadMap(dm, nullptr, map_lut);
    deal_error(bmcrc, error_code, error_info);
    return bmcrc == NO_ERR;
}
bool DLL_EXPORT QPSL_BMCSetArray(DM *dm, const double *ValueArray, const uint32_t *MAP_LUT, int *error_code, char *error_info) {
    BMCRC bmcrc = BMCSetArray(dm, ValueArray, MAP_LUT);
    deal_error(bmcrc, error_code, error_info);
    return bmcrc == NO_ERR;
}
#ifdef __cplusplus
}
#endif
#if defined(_WIN32)
#undef strnlen
#undef getch
#endif
#endif