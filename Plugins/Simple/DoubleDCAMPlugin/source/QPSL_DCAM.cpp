#ifndef __QPSL_DCAM__
#define __QPSL_DCAM__
#include "dcamapi4.h"
#include "dcamprop.h"
// #include "console4.h"
#include <stdio.h>
#include <stdlib.h>
#include <cstring>
#if defined(UNICODE) || defined(_UNICODE)
#define	_T(str)	L##str
#else
#define	_T(str)	str
#endif
#ifdef __cplusplus
extern "C" {
#endif

#define DLL_EXPORT __declspec(dllexport)

#define DCAMErrChk(functionCall)\
    if (failed(controller->err_code =(functionCall)))\
        return deal_err(controller);

struct DCAMController{
    HDCAM hdcam;
    int index;
    const char* save_path; 
    DCAMERR err_code;
    char err_buffer[1024];    
};
int32 deal_err(DCAMController *controller){
    if(failed(controller->err_code)){
        sprintf(controller->err_buffer, "DCAM ERROR: %s\n", controller->err_code);
    }
    return controller->err_code;
}
/* Without Macro
int32 DLL_EXPORT QPSL_DCAMAPI_init(DCAMController *controller){
    DCAMERR err;
	DCAMAPI_INIT apiinit;	
	memset(&apiinit, 0, sizeof(apiinit));	
	apiinit.size = sizeof(apiinit);	
	err = dcamapi_init(&apiinit);
    if(int(err) < 0){
        return err;
    }
    return 0;
}
*/

int32 DLL_EXPORT QPSL_DCAMAPI_init(char *err_buffer){
    DCAMERR err;
	DCAMAPI_INIT apiinit;	
	memset(&apiinit, 0, sizeof(apiinit));	
	apiinit.size = sizeof(apiinit);	
	err = dcamapi_init(&apiinit);
    if(failed(err)){
        sprintf(err_buffer, "DCAMAPI ERROR: %d\n",err);
    }
    sprintf(err_buffer, "DCAMAPI Init Success\n");
    return 0;
}
int32 DLL_EXPORT QPSL_DCAMAPI_uninit(char *err_buffer){
    DCAMERR err;
    err = dcamapi_uninit();
    if(failed(err)){
        sprintf(err_buffer, "DCAMAPI ERROR: %d\n",err);
    }
    sprintf(err_buffer, "DCAMAPI Uninit Success\n");
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_open(DCAMController *controller){
    DCAMDEV_OPEN devopen;
    memset(&devopen, 0, sizeof(devopen));
	devopen.size = sizeof(devopen);	
	devopen.index = controller->index;
    DCAMErrChk(dcamdev_open(&devopen))
	else{
        controller->hdcam = devopen.hdcam;
	}
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_close(DCAMController *controller){
    DCAMErrChk(dcamdev_close(controller->hdcam))
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_getstring(DCAMController *controller, char *cameraid){
    DCAMDEV_STRING	param;
	memset(&param, 0, sizeof(param));
	param.size = sizeof(param);
    param.text = cameraid;
    param.textbytes = 256;    
	param.iString = DCAM_IDSTR_CAMERAID;
    DCAMErrChk(dcamdev_getstring(controller->hdcam,&param))
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_getvalue(DCAMController *controller, double *temperature){
    // double *temperature = new double;
    DCAMErrChk(dcamprop_getvalue(controller->hdcam,DCAM_IDPROP_SENSORTEMPERATURE,temperature))
    // delete temperature;
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_setROI(DCAMController *controller, int32 hpos, int32 vpos, int32 hsize, int32 vsize){
    DCAMErrChk(dcamprop_setvalue(controller->hdcam,DCAM_IDPROP_SUBARRAYHPOS,hpos));
    DCAMErrChk(dcamprop_setvalue(controller->hdcam,DCAM_IDPROP_SUBARRAYVPOS,vpos));
    DCAMErrChk(dcamprop_setvalue(controller->hdcam,DCAM_IDPROP_SUBARRAYHSIZE,hsize));
    DCAMErrChk(dcamprop_setvalue(controller->hdcam,DCAM_IDPROP_SUBARRAYVSIZE,vsize));
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_setExposureTime(DCAMController *controller, double exposuretime){
    DCAMErrChk(dcamprop_setvalue(controller->hdcam,DCAM_IDPROP_EXPOSURETIME,exposuretime));
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_setInternalTrigger(DCAMController *controller){
    DCAMErrChk(dcamprop_setvalue(controller->hdcam,DCAM_IDPROP_TRIGGERSOURCE,DCAMPROP_TRIGGERSOURCE__EXTERNAL));
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_setExternalTrigger(DCAMController *controller){
    DCAMErrChk(dcamprop_setvalue(controller->hdcam,DCAM_IDPROP_TRIGGERSOURCE,DCAMPROP_TRIGGERSOURCE__INTERNAL));
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_setSyncReadout(DCAMController *controller){
    DCAMErrChk(dcamprop_setvalue(controller->hdcam,DCAM_IDPROP_TRIGGERACTIVE,DCAMPROP_TRIGGERACTIVE__SYNCREADOUT));
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_setTriggerPositive(DCAMController *controller){
    DCAMErrChk(dcamprop_setvalue(controller->hdcam,DCAM_IDPROP_TRIGGERPOLARITY,DCAMPROP_TRIGGERPOLARITY__POSITIVE));
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_setTriggerNegative(DCAMController *controller){
    DCAMErrChk(dcamprop_setvalue(controller->hdcam,DCAM_IDPROP_TRIGGERPOLARITY,DCAMPROP_TRIGGERPOLARITY__NEGATIVE));
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_setTriggerDelay(DCAMController *controller, double delay){
    DCAMErrChk(dcamprop_setvalue(controller->hdcam,DCAM_IDPROP_TRIGGERDELAY,delay));
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_bufferRelease(DCAMController *controller){
    DCAMErrChk(dcambuf_release(controller->hdcam));
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_Capture(DCAMController *controller){
    HDCAMREC hrec = NULL;
	DCAMREC_OPEN recopen;
	memset(&recopen, 0, sizeof(recopen));
	recopen.size = sizeof(recopen);
	recopen.path = _T(controller->save_path);
	recopen.ext = _T("tiff");
	recopen.maxframepersession = 1;
	recopen.userdatasize_file = 0;
	recopen.usertextsize_file = 0;
	recopen.userdatasize_session = 0;
	recopen.usertextsize_session = 0;
	recopen.userdatasize = 0;
	recopen.usertextsize = 0;
    DCAMErrChk(dcamrec_open(&recopen))
    else{
        hrec = recopen.hrec;
    }
    HDCAMWAIT hwait = NULL;
    DCAMWAIT_OPEN waitopen;
    memset(&waitopen, 0, sizeof(waitopen));
    waitopen.size = sizeof(waitopen);
    waitopen.hdcam = controller->hdcam;
    DCAMErrChk(dcamwait_open(&waitopen))
    else{
        hwait = waitopen.hwait;
    }
    DCAMErrChk(dcambuf_alloc(controller->hdcam,1));
    if((hrec!=NULL) && (hwait!=NULL)){
        DCAMErrChk(dcamcap_record(controller->hdcam,hrec))
        else{
            DCAMErrChk(dcamcap_start(controller->hdcam, DCAMCAP_START_SNAP))
            else{
                DCAMWAIT_START waitstart;
                memset(&waitstart, 0, sizeof(waitstart));
                waitstart.size = sizeof(waitstart);
                waitstart.eventmask = DCAMWAIT_CAPEVENT_STOPPED;
                waitstart.timeout = DCAMWAIT_TIMEOUT_INFINITE;
                DCAMErrChk(dcamwait_start(hwait, &waitstart));
            }
        }
        DCAMErrChk(dcamrec_close(hrec));
    }  
    DCAMErrChk(dcambuf_release(controller->hdcam));
    DCAMErrChk(dcamwait_abort(hwait));
    return 0;
}
int32 DLL_EXPORT QPSL_DCAM_Live(DCAMController *controller, char *imagebuf){
    HDCAMWAIT hwait = NULL;
    DCAMWAIT_OPEN waitopen;
    DCAMWAIT_START waitstart;
    DCAMBUF_FRAME bufframe;
    int32 ox = bufframe.left;
    int32 oy = bufframe.top;
    int32 cx = bufframe.width;
    int32 cy = bufframe.height;
    int32 rowbytes = bufframe.rowbytes;
    int32 copyrowbytes = cx * 2;
    memset(&waitopen, 0, sizeof(waitopen));
    waitopen.size = sizeof(waitopen);
    waitopen.hdcam = controller->hdcam;
    DCAMErrChk(dcamwait_open(&waitopen))
    else{
        hwait = waitopen.hwait;
    }
    if(hwait!=NULL){
        memset(&waitstart, 0, sizeof(waitstart));
        waitstart.size = sizeof(waitstart);
        waitstart.eventmask = DCAMWAIT_CAPEVENT_FRAMEREADY;
        waitstart.timeout = DCAMWAIT_TIMEOUT_INFINITE;
        //bufframe param
	    memset(&bufframe, 0, sizeof(bufframe));
        bufframe.size = sizeof(bufframe);
        bufframe.iFrame = -1;    //last frame
    }
    DCAMErrChk(dcambuf_alloc(controller->hdcam,10));
    DCAMErrChk(dcamcap_start(controller->hdcam, DCAMCAP_START_SEQUENCE))
    else{
        for(int i=0;true;){
            controller->err_code = dcamwait_start(hwait, &waitstart);
            if(failed(controller->err_code)){
                if(controller->err_code == DCAMERR_ABORT){
                    break;
                }
                else continue;
            }
            DCAMErrChk(dcambuf_lockframe(controller->hdcam, &bufframe))

            char* pSrc = (char*)bufframe.buf + oy * bufframe.rowbytes + ox * 2;
            char* pDst = (char*)imagebuf;

            int y;
            for(y = 0;y < cy; y++)
            {
                memcpy_s(pDst, rowbytes, pSrc, copyrowbytes);
                pSrc += bufframe.rowbytes;
                pDst += rowbytes;
            }

            // ImageData<unsigned short> imagedata((unsigned short*)bufframe.buf,bufframe.width,bufframe.height);
            i++;
        }
        DCAMErrChk(dcamcap_stop(controller->hdcam));
    }
    DCAMErrChk(dcambuf_release(controller->hdcam));
    DCAMErrChk(dcamwait_abort(hwait));
}
int32 DLL_EXPORT QPSL_DCAM_Abort(DCAMController *controller){
    controller->err_code = DCAMERR_ABORT;
}
int32 DLL_EXPORT QPSL_DCAM_Scan(DCAMController *controller, int endframe){
    HDCAMREC hrec = NULL;
    HDCAMWAIT hwait = NULL;
    DCAMWAIT_OPEN waitopen;
    DCAMWAIT_START waitstart;
    DCAMBUF_FRAME bufframe;
	DCAMREC_OPEN recopen;
	memset(&recopen, 0, sizeof(recopen));
	recopen.size = sizeof(recopen);
	recopen.path = _T(controller->save_path);
	recopen.ext = _T("tiff");
	recopen.maxframepersession = endframe;
	recopen.userdatasize_file = 0;
	recopen.usertextsize_file = 0;
	recopen.userdatasize_session = 0;
	recopen.usertextsize_session = 0;
	recopen.userdatasize = 0;
	recopen.usertextsize = 0;
    DCAMErrChk(dcamrec_open(&recopen))
    else{
        hrec = recopen.hrec;
    }    
    memset(&waitopen, 0, sizeof(waitopen));
    waitopen.size = sizeof(waitopen);
    waitopen.hdcam = controller->hdcam;
    DCAMErrChk(dcamwait_open(&waitopen))
    else{
        hwait = waitopen.hwait;
        DCAMErrChk(dcambuf_alloc(controller->hdcam,10));
        if((hwait!=NULL) && (hrec!=NULL)){
            memset(&waitstart, 0, sizeof(waitstart));
            waitstart.size = sizeof(waitstart);
            waitstart.eventmask = DCAMWAIT_CAPEVENT_FRAMEREADY;
            waitstart.timeout = DCAMWAIT_TIMEOUT_INFINITE;
            //bufframe param
	        memset( &bufframe, 0, sizeof(bufframe) );
            bufframe.size = sizeof(bufframe);
            bufframe.iFrame = -1;    //last frame
            DCAMErrChk(dcamwait_start(hwait, &waitstart))
        }
        for(int i=0;i < endframe;){
            DCAMErrChk(dcamcap_start(controller->hdcam, DCAMCAP_START_SEQUENCE))
            if(controller->err_code == DCAMERR_ABORT){
                break;
            }
            else continue;
            DCAMErrChk(dcambuf_lockframe(controller->hdcam, &bufframe))
            i++;
        }
        DCAMErrChk(dcamcap_stop(controller->hdcam));
        DCAMErrChk(dcambuf_release(controller->hdcam));
    }
    DCAMErrChk(dcamrec_close(hrec));
    DCAMErrChk(dcamwait_abort(hwait));
}
#ifdef __cplusplus
}
#endif
#endif
