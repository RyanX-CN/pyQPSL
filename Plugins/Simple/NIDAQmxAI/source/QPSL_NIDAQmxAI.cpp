#ifndef __QPSL_NIDAQmxAI__
#define __QPSL_NIDAQmxAI__
#include "NIDAQmx.h"
#include <stdio.h>
#include <stdlib.h>
#ifdef __cplusplus
extern "C" {
#endif
#define DLL_EXPORT __declspec(dllexport)
#define DAQmxErrChk(functionCall)                 \
    if (DAQmxFailed(error_code = (functionCall))) \
        return deal_err(error_code, error_buffer, len2);
#define DAQmxErrChk_task(functionCall)                  \
    if (DAQmxFailed(task->error_code = (functionCall))) \
        return deal_err_task(task);
struct DAQmxAnalogInputChannel {
    char physical_channel_name[256];
};
struct DAQmxAnalogInputTask {
    TaskHandle handle;
    DAQmxAnalogInputChannel *channels;
    uInt32 channel_number;
    char trigger_source[1024];
    float64 sample_rate;
    int32 sample_mode;
    int32 sample_per_channel;
    float64 min_val;
    float64 max_val;
    int32 error_code;
    char error_buffer[1024];
};
int32 DLL_EXPORT QPSL_DAQmxGetErrorString(int32 error_code, char *error_buffer, uInt32 len) {
    return DAQmxGetErrorString(error_code, error_buffer, len);
}
int32 DLL_EXPORT QPSL_DAQmxGetExtendedErrorInfo(char *error_buffer, uInt32 len) {
    return DAQmxGetExtendedErrorInfo(error_buffer, len);
}
int32 deal_err(int32 error_code, char *error_buffer, uInt32 len) {
    if (DAQmxFailed(error_code)) {
        char temp[1024]{};
        DAQmxGetExtendedErrorInfo(temp, 1024);
        sprintf(error_buffer, "DAQmx Error: %s\n", temp);
    }
    return error_code;
}
int32 deal_err_task(DAQmxAnalogInputTask *task) {
    if (DAQmxFailed(task->error_code)) {
        char temp[1024]{};
        DAQmxGetExtendedErrorInfo(temp, 1024);
        sprintf(task->error_buffer, "DAQmx Error: %s\n", temp);
    }
    if (task->handle != 0) {
        DAQmxStopTask(task->handle);
        DAQmxClearTask(task->handle);
        task->handle = 0;
    }
    return task->error_code;
}
int32 DLL_EXPORT QPSL_DAQmxGetDeviceList(char *name_list, uInt32 len, char *error_buffer, uInt32 len2) {
    int error_code;
    DAQmxErrChk(DAQmxGetSystemInfoAttribute(DAQmx_Sys_DevNames, name_list, len));
    return 0;
}
int32 DLL_EXPORT QPSL_DAQmxGetAIChannelList(const char *device_name, char *name_list, uInt32 len, char *error_buffer, uInt32 len2) {
    int error_code;
    DAQmxErrChk(DAQmxGetDevAIPhysicalChans(device_name, name_list, len));
    return 0;
}
int32 DLL_EXPORT QPSL_DAQmxGetDevTerminals(const char *device_name, char *terminal_list, uInt32 len, char *error_buffer, uInt32 len2) {
    int32 error_code;
    DAQmxErrChk(DAQmxGetDevTerminals(device_name, terminal_list, len));
    return 0;
}
int32 DLL_EXPORT QPSL_DAQmxAI_init(DAQmxAnalogInputTask *task) {
    DAQmxErrChk_task(DAQmxCreateTask("", &task->handle));
    char buffer[1024]{}, *cursor = buffer;
    for (uint32_t i = 0; i < task->channel_number; i++) {
        if (i) *cursor++ = ',';
        cursor += sprintf(cursor, "%s", task->channels[i].physical_channel_name);
    }
    DAQmxErrChk_task(DAQmxCreateAIVoltageChan(task->handle, buffer, "", DAQmx_Val_Cfg_Default, task->min_val, task->max_val, DAQmx_Val_Volts, nullptr));
    DAQmxErrChk_task(DAQmxCfgSampClkTiming(task->handle, task->trigger_source, task->sample_rate, DAQmx_Val_Rising, task->sample_mode, task->sample_per_channel));
    return 0;
}
int32 DLL_EXPORT QPSL_DAQmxAI_start(DAQmxAnalogInputTask *task) {
    DAQmxErrChk_task(DAQmxStartTask(task->handle));
    return 0;
}
int32 DLL_EXPORT QPSL_DAQmxAI_stop(DAQmxAnalogInputTask *task) {
    DAQmxErrChk_task(DAQmxStopTask(task->handle));
    return 0;
}
int32 DLL_EXPORT QPSL_DAQmxAI_clear(DAQmxAnalogInputTask *task) {
    DAQmxErrChk_task(DAQmxClearTask(task->handle));
    task->handle = 0;
    return 0;
}
int32 DLL_EXPORT QPSL_DAQmxReadAnalogF64(DAQmxAnalogInputTask *task, int32 *num_of_read, float64 *buffer, uInt32 buffer_len, int32 sample_per_channel) {
    DAQmxErrChk_task(DAQmxReadAnalogF64(task->handle, sample_per_channel, 10.0, DAQmx_Val_GroupByChannel, buffer, buffer_len, num_of_read, nullptr));
    return 0;
}
int32 DLL_EXPORT QPSL_DAQmxAI_register_everyn_callback(DAQmxAnalogInputTask *task, uInt32 n_samples, DAQmxEveryNSamplesEventCallbackPtr callback, void *callback_data) {
    DAQmxErrChk_task(DAQmxRegisterEveryNSamplesEvent(task->handle, DAQmx_Val_Acquired_Into_Buffer, n_samples, 0, callback, callback_data));
    return 0;
}
int32 DLL_EXPORT QPSL_DAQmxAI_register_done_callback(DAQmxAnalogInputTask *task, DAQmxDoneEventCallbackPtr callback, void *callback_data) {
    DAQmxErrChk_task(DAQmxRegisterDoneEvent(task->handle, 0, callback, callback_data));
    return 0;
}
int32 DLL_EXPORT QPSL_DAQmxGetBufInputBufSize(DAQmxAnalogInputTask *task, uInt32 *data) {
    DAQmxErrChk_task(DAQmxGetBufInputBufSize(task->handle, data));
    return 0;
}
int32 DLL_EXPORT QPSL_DAQmxSetBufInputBufSize(DAQmxAnalogInputTask *task, uInt32 data) {
    DAQmxErrChk_task(DAQmxSetBufInputBufSize(task->handle, data));
    return 0;
}

#ifdef __cplusplus
}
#endif
#endif