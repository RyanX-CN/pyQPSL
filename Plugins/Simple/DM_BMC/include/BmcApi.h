#pragma once
#ifndef BMCAPI_H
#define BMCAPI_H

/*! \mainpage
 *  \section Introduction
*	The Boston Micromachines Deformable Mirror (DM) Software Development Kit
*   (SDK) provides a common interface to all BMC products. It allows users to
*   write one code base that can be used with any product.<BR>
*   BMC DMs are supplied with a variety of drive electronics (DE). The
*   functionality of the SDK is organized
*	into two tiers, one common to all products and one tier based around
*	the type of interface to the drive electronics. The top level functions 
*	are prefixed with BMC****. The lower level functions are prefixed with 
*	type of interface to the drive electronics, USB**** or PCIe****. <BR>
*
*   One DM per DE is supported.<BR>
*
*	Dynamic link libraries are provided for use from C or C++ on Windows x64.
*   The .lib files are in
*	[Install Folder]/LibXX and .dll files in [Install Folder]/BinXX.<BR>
*   Additional dynamic library wrappers are provided to interface from the
*   following software:
*   <ul>
*       <li>Mathworks MATLAB (2008 or newer)</li>
*       <li>National Instruments Labview</li>
*       <li>Python (2.x)</li>
*   </ul>
*   Function names may differ between the software platforms, but the general
*   method of operation remains the same.  Refer to documentation inside the
*   software (e.g. <CODE>help BMCOpenDM</CODE> in MATLAB).
*
*   \section Overview
*   The DM-SDK supports continuous face-sheet and segmented DMs from BMC. The
*   number of actuators is considered the "size" of the DM. Individual actuators
*   can be addressed for any mirror, with indexes from 0 to size-1.<BR>
*	Actuator values are passed to the SDK as a double float value in the range
*   [0,1].
*	This value is internally converted to the nearest suitable 16-bit driver
*	DAC value.<BR>
*   All actuators may be set at a time, or individually.<BR>
*
*   \see BMCSetArray(), BMCSetSingle()
*   \subsection segment Open Loop Segment Control
*   There is additional functionality for segmented DMs (SLMs). Some SLMs
*   have more than one actuator per segment. Segments can be manipulated,
*   with open loop control over all actuators for the segment. Segments are
*   indexed from 0 and may not map sequentially to actuator indexes. For these
*   functions, values are passed in user units (e.g. nm) and are converted
*   internally to the nearest suitable 16-bit driver DAC values for the
*   appropriate actuators.<BR>
*
*   \see BMCSetSegment(), BMCGetSegmentRange()
*
*   \section basicop Basic Operation
*   To use the API, include this file:
*   \code #include <BmcApi.h> \endcode
*   and link to the BMC, BMC_PCIeAPI, and BMC_USBAPI DLLs.
*
*	In order to apply voltage to the DM the following sequence of function
*	calls are required:
*
*	BMCOpen();<BR>
*	BMCLoadMap();<BR> 
*	BMCSetArray(); or BMCSetSingle(); or BMCSetSegment()<BR>
*	BMCClose();<BR>
*	
*	This sequence nearly encompasses the minimum calls needed by the BMC level 
*	API. Other funtionality is available through the hardware specific APIs. 
*	The SDK was designed such that once the driver connection is opened, the 
*	DM struct can be used to call any level function. However, care must be 
*	taken to pass the appropriate input arguments, since the BMC level commands
*	manage many of the data types for the user. The DM struct should not be
*   modified by the user. Other than the actuator count
*   and driver type, the DM struct is intended to be opaque.
*
*   All functions return an error code that should be checked. Use
*   BMCErrorString() to get a readable error message from the code.
*
*   \section DM Profile
*   A configuration file for every DM and associated DE is provided with the
*   hardware.  The file is referred to as a "profile" and should have the name
*   "<DM_Serial_Number>.dm". The SDK expects these profiles to be installed in:
*   [Install Folder]/Profiles<BR>
*   The serial number is required to operate the DM.
*   In case a different configuration path is desired, the following functions
*   are provided to configure the SDK:
*
*   BMCSetProfilesPath();
*   BMCSetMapsPath();
*   BMCSetCalibrationsPath();
*   BMCConfigureLog();
*
*   \section platforms Supported Platforms
*   Windows 7 and newer. 64-bit only.<BR>
*   The library is built with Microsoft Visual Studio 2015 but any version 2010
*   or newer is supported.
*
*   Linux 64-bit. Ubuntu 17.04 or newer recommended.
*   The library is built on Ubuntu 17.04 with GCC 6.3.0.
*
*   \section cpp C++ Notes
*   The API provided is a C API. All functions are in the global namespace.
*   This is subject to change in future releases.
*	
*   \section links API Documentation
*	\ref defs <BR>
*	\ref bmc <BR>
*	\ref usb <BR>
*	\ref pcie
*
*   \section Changes
*   See the \ref ChangeLog and \ref releasenotes for changes that may
*   effect your code.
*/

/*!	\file BMCApi.h
*	\section bmc BMC general API for all drivers.
*
*   Link to the BMC, BMC_PCIeAPI, and BMC_USBAPI DLLs to use this API.
*/

#if defined(_WIN32)
    #ifdef BMC_EXPORTS
    #define BMC_API __declspec(dllexport)
    #else
    #define BMC_API __declspec(dllimport)
    #endif
#else
    #define BMC_API
#endif

#include "BMCDefs.h"

#ifdef __cplusplus
extern "C" {
#endif

/*! \brief Open DM and driver with the specified serial number.
*
*	Opens the connection to the drive electronics.
*	The necessary information (driver type, actuator count, maximum voltage, 
*	and mapping file) are read from a profile identified from the serial number.
*
*	The DM *pMirror struct has been allocated but not defined, with exception of
*   the following. It is recommended to zero the struct before use.
*
*   Some settings may be configured on the DM struct prior to calling BMCOpen():
*   see BMCSetProfilesPath(), BMCSetMapsPath(), and BMCSetCalibrationsPath().
*
*   For PCIe devices, the @a pMirror->DevId field may be set to an index starting
*   with 1 to select a PCIe interface card when more than one is installed. If
*   set to 0 or a value higher than the number of cards, this field is ignored,
*   except for the following special values.
*
*   If @a pMirror->DevId is BMC_DEV_ID_QUERY_PROFILE, the driver is not opened
*    and ::ERR_NO_HW is returned.
*
*	@param pMirror		Pointer to the allocated structure used to internally ID
*        the driver.
*	@param serial_number	The mirror serial number. Must be an 11 character
*       NUL-terminated string.
*
*	@return
*	::BMCRC		Error status. Possible values:<BR>
*				::NO_ERR, ::ERR_REGISTRY, ::ERR_X64_ONLY,
*               ::ERR_INVALID_DRIVER_TYPE,
*				::ERR_INIT_DRIVER, ::ERR_NO_HW,
*               ::ERR_OPENFILE, ::ERR_FILE_PERMISSIONS, ::ERR_FILE_FORMAT,
*               ::ERR_PCIE_REGRD, ::ERR_PCIE_REGWR
*/
BMC_API BMCRC BMCOpen(struct DM *pMirror, const char *serial_number);

/*! \brief Open and read a driver to actuator mapping files.
*
*	Opens the mapping file for the driver and mirror. If @a map_path is NULL
*	the default mapping specified be the profile will be used. The user must
*	take care to allocate enough memory for the lookup table, @a map_lut, based
*	on the ActCount member of the DM struct.
*
*	@param pMirror	Pointer to driver handle.<BR>
*   @param map_path	Path and name of mapping file. NULL to use default.<BR>
*	@param map_lut	Allocated array to hold mapping. It is recommended that the
*                       user allocate this array for MAX_DM_SIZE.  If NULL, then
*                       the memory is allocated internally.<BR>
*
*	@return
*	BMCRC		Error status. Possible value:<BR>
*				NO_ERR, ERR_OPENFILE, ERR_FILE_PERMISSIONS, ERR_FILE_FORMAT,
*               ERR_INVALID_LUT
*
*/
BMC_API BMCRC BMCLoadMap(struct DM *pMirror, const char* map_path, uint32_t *map_lut);

/*! \brief Apply opened driver to actuator number mapping.
*
*   \deprecated Mapping is loaded with BMCOpen() or BMCLoadMap()
*
*	This function will send the loaded mapping to the driver. Otherwise,
*	the mapping will be applied before data is sent to the driver. Only 
*	supported in PCI/PCIe based drivers. If you call this with a USB driver,
*	the function will do nothing and return NO_ERR. 
*
*	The mask array is used to enable or disable actuators. Locations with a
*	1 will be enabled and locations with a 0 will be disabled. Mask must have
*	the same length as @a map_lut.
*
*	@param pMirror	Pointer to driver handle.<BR>
*	@param map_lut	Actuator to driver channel mapping loaded with BMCLoadMap().<BR>
*	@param mask		The mask can be used to deactivate individual channels. It
*					should be an array the length of the mapping with zeros for
*					inactive channels and ones for active channels.
*
*	@return
*	BMCRC		Error Status. Possible values:<BR>
*				NO_ERR, ERR_NOT_IMPLEMENTED, ERR_X64_ONLY,
*				ERR_PCIE_REGRD, ERR_INVALID_LUT, ERR_PCIE_REGWR
*/
BMC_API BMCRC BMCApplyMap(struct DM *pMirror, uint32_t *map_lut, uint32_t *mask);

/*!	\brief Set the Value on a single actuator.
*
*	BMCSetSingle sets the value of a single actuator, ie. "poke". Only
*	PCIe based drivers can set one actuator independently of all others
*	without needing to send an entire frame, but the frame is buffered
*   internally for other drivers.<BR>
*   For drivers that require a channel mapping, the last loaded LUT is used.<BR>
*
*	@param pMirror	Pointer to driver handle.<BR>
*	@param Actuator	The actuator number to change.<BR>
*	@param Value	The actuator command value to write. This is converted to the
*					correct DAC value internally.
*
*	@return
*	BMCRC		Error status. Possible values:<BR>
*				NO_ERR, ERR_NOT_IMPLEMENTED, ERR_X64_ONLY, ERR_ACTUATOR_ID,
*				ERR_PCIE_REGWR 
*/ 
BMC_API BMCRC BMCSetSingle(struct DM *pMirror, uint32_t Actuator, double Value);

/*! \brief Set full array of actuator command values.
*
*	Sends a full frame of data specified by Value Array. Value array consists
*	of double precision numbers in the range [0,1]. Values are converted to 
*	the correct	output (DAC value) internally. Values outside the above range 
*	will be rounded to the appropriate end of the range.
*
*	@param pMirror		Pointer to driver handle.<BR>
*	@param ValueArray	Pointer to array containing command values in the
*                       range [0,1].<BR>
*	@param MAP_LUT		Mapping lookup table. If NULL, then the last
*                       loaded LUT is used. Does not override the last loaded
*                       LUT for future calls.<BR>
*
*	@return
*	BMCRC		Error Status. Possible values:<BR>
*				NO_ERR, ERR_MALLOC, ERR_X64_ONLY, ERR_INVALID_DRIVER_TYPE,
*				ERR_NO_HW, ERR_TIMEOUT, ERR_PCIE_BURST
*/
BMC_API BMCRC BMCSetArray(struct DM *pMirror, const double *ValueArray, const uint32_t *MAP_LUT);

/*! \brief Get a copy of the full array of the last command values.
*
*	@param pMirror		Pointer to driver handle.<BR>
*	@param ValueArray	Pointer to array containing command values.
*           Must be allocated for at least pMirror->ActCount values.<BR>
*   @param length       Length of the data array. Should equal pMirror->ActCount.
*
*	@return
*	BMCRC		Error Status. Possible values:<BR>
*				NO_ERR, ERR_MALLOC, ERR_X64_ONLY, ERR_INVALID_DRIVER_TYPE,
*				ERR_NO_HW, ERR_TIMEOUT, ERR_PCIE_BURST
*/
BMC_API BMCRC BMCGetArray(struct DM *pMirror, double *ValueArray, uint32_t length);

/*! \brief Clear (ie. set to zero) the entire array. 
*
*	BMCClearArray() is a convenience function to set all channels to zero. 
*	This could also be done by sending and array of zeros to BMCSetArray().
*
*	@param pMirror	Pointer to driver handle.<BR>
*	
*	@return
*	BMCRC		Error status. Possible values:<BR>
*				NO_ERR, ERR_X64_ONLY, ERR_INVALID_DRIVER_TYPE,
*				ERR_NO_HW, ERR_TIMEOUT, ERR_PCIE_REG_RD, ERR_ACTUATOR_ID,
*				ERR_PCIE_REGWR
*/
BMC_API BMCRC BMCClearArray(struct DM *pMirror);

// OPEN LOOP CONTROL FUNCTIONS ////////////////////////////////////////////////

/*!	\brief Set the Piston, X-Tilt, Y-Tilt, of a single segment of an SLM.
*
*   BMCSetSegment sets the tilt and piston value of a single segment of a
*   segmented DM. Unlike the actuator commands, the values passed to this
*   function are in user units.<BR>
*   A calibration table must be loaded before using this function.<BR>
*	Only PCIe based drivers can set one actuator independently of all others
*	without needing to send an entire frame.
*   Because some devices require an entire frame for all actuator DACs, the
*   frame is buffered internally. Use @a sendNow to control sending the frame.
*   The internally buffered frame may be overwritten by BMCSetSingle() or
*   BMCSetArray().<BR>
*
*	@param pMirror	Pointer to driver handle.<BR>
*	@param segment 	The segment number to change. For square segment or
*               continuous face-sheet mirrors, this corresponds to the
*               actuator number.<BR>
*   @param piston    The piston command value in nm. This is converted
*               to the correct DAC value(s) internally.<BR>
*   @param xTilt     The X-Tilt command value in radians. This is converted
*               to the correct DAC value(s) internally. This is ignored for
*               square segment or continous face-sheet mirrors.<BR>
*   @param yTilt     The Y-Tilt command value in radians. This is converted
*               to the correct DAC value(s) internally. This is ignored for
*               square segment or continous face-sheet mirrors.<BR>
*   @param applyOffsets Subtract the unpowered DM shape from the commanded
*               values. This should usually be set to TRUE. The unpowered
*               shape is provided in the calibration table.<BR>
*   @param sendNow   Send the frame of data to the DACs. If 0, the frame
*               is buffered internally until this function is called with
*               with sendNow=1 or BMCSetSingle() is called for a device that
*               requires an entire frame.<BR>
*
*	@return
*	BMCRC		Error status. Possible values:<BR>
*				NO_ERR, ERR_NOT_IMPLEMENTED, ERR_X64_ONLY, ERR_ACTUATOR_ID,
*				ERR_PCIE_REGWR, ERR_SEGMENT_ID, ERR_INVALID_CALIBRATION,
*               ERR_OUT_OF_LUT_RANGE
*/
BMC_API BMCRC BMCSetSegment(DMHANDLE pMirror,
                            uint32_t segment,
                            double piston,
                            double xTilt,
                            double yTilt,
                            int applyOffsets,
                            int sendNow);

/*!	\brief Get the Piston range for a given X-Tilt, Y-Tilt or tilt range given piston.
*
*   BMCGetSegmentRange gets the range of values of a single segment
*   of a segmented DM given values for the other two axes.
*   Unlike the actuator commands, the values passed to this
*   function are in user units.<BR>
*   A calibration table must be loaded before using this function.<BR>
*
*	@param pMirror	Pointer to driver handle.<BR>
*	@param segment 	The segment number to query. For square segment or
*               continuous face-sheet mirrors, this corresponds to the
*               actuator number.<BR>
*   @param axis    Query Piston, X-Tilt, or Y-Tilt. The given value
*               for this axis is not used.<BR>
*   @param piston    The piston command value in nm.<BR>
*   @param xTilt     The X-Tilt command value in radians. This is converted
*               to the correct DAC value(s) internally. This is ignored for
*               square segment or continous face-sheet mirrors. This is ignored
*               if @a axis == DM_XTilt.<BR>
*   @param yTilt     The Y-Tilt command value in radians. This is converted
*               to the correct DAC value(s) internally. This is ignored for
*               square segment or continous face-sheet mirrors. This is ignored
*               if @a axis == DM_YTilt.<BR>
*   @param applyOffsets Subtract the unpowered DM shape from the commanded
*               values. This should usually be set to TRUE. The unpowered
*               shape is provided in the calibration table. Use this
*               consistently with the same parameter to BMCSetSegment().<BR>
*   @param [out] minValue_out  Pointer to return the minimum
*               value in nm for the given X-Tilt, Y-tilt, and segment number.<BR>
*   @param [out] maxValue_out  Pointer to return the maximum
*               value in nm for the given X-Tilt, Y-tilt, and segment number.<BR>
*
*	@return
*	BMCRC		Error status. Possible values:<BR>
*				NO_ERR, ERR_NOT_IMPLEMENTED, ERR_ACTUATOR_ID,
*				ERR_SEGMENT_ID, ERR_INVALID_CALIBRATION,
*               ERR_OUT_OF_LUT_RANGE
*/
BMC_API BMCRC BMCGetSegmentRange(DMHANDLE pMirror,
                            uint32_t segment,
                            DMSegmentAxis axis,
                            double piston,
                            double xTilt,
                            double yTilt,
                            int applyOffsets,
                            double* minValue_out,
                            double* maxValue_out);

/*! \brief Read calibration file for user unit to DAC value conversion.
 *
 * The calibration is only used by functions that accept user units.<BR>
 * The following file formats are supported: .MAT (MATLAB) Version 7.0<BR>
 *
 *	@param pMirror	Pointer to driver handle.<BR>
 *	@param filePath	Path and name of calibration file.
 *              NULL to use default set in profile.<BR>
 *
 *	@return
 *	BMCRC		Error status. Possible values:<BR>
 *				NO_ERR, ERR_INVALID_DRIVER_TYPE,
 *				ERR_NO_HW, ERR_TIMEOUT, ERR_ACTUATOR_ID,
 *				ERR_INVALID_CALIBRATION
 */
BMC_API BMCRC BMCLoadCalibrationFile(DMHANDLE pMirror,
                                     const char* filePath);

/*! \brief Configure the sequencing hardware. PCIe card only.
*   Configure the on board sequence functionality.
*
*   Value array consists
*	of double precision numbers in the range [0,1]. Values are converted to
*	the correct	output (DAC value) internally. Values outside the above range
*	will be rounded to the appropriate end of the range.
*
*   @param pMirror Pointer to driver handle.
*   @param sequence pointer to sequence array of length frame_length*seq_length.
*       Max length is 4096, limited by FPGA memory.
*   @param delay Delay between sequence frames. Range is [0,0.25] seconds.
*   @param frame_length The number of actuators in each frame, up to ActCount.
*   @param seq_length Number of frames
*
*   @return
*   BMCRC       Error status. Possible values:<BR>
*               NO_ERR, ERR_INVALID_DRIVER_TYPE, ERR_INVALID_SEQUENCE, ERR_INVALID_SEQUENCE_RATE,
*				ERR_PCIE_REGWR.
*
*/
BMC_API BMCRC BMCConfigureSequence(
        struct DM *pMirror,
        const double *sequence,
        double delay,
        uint32_t frame_length,
        uint32_t seq_length);

/*! \brief Turn the the sequencing functionality on or off.
*
*    @param pMirror Pointer to driver handle.
*    @param frame_rate Frame rate of sequence frames. If the frame rate is 0 the
*    SMA trigger input will be used to advance frames.
*	 @param enable Turns sequencing on or off.
*
*    @return
*    BMCRC		Error status. Possible value:<BR>
*				NO_ERR, ERR_INVALID_SEQUENCE_RATE, ERR_PCIE_REGWR.
*/

BMC_API BMCRC BMCEnableSequence(struct DM *pMirror,
                                double frame_rate,
                                int enable);

/*! \brief Configure the dithering functionality.
*   The waveform is the sequence of frame magnitudes and gains is the value for each actuator
*	that will be dither on each frame. So the value actuator j in frame i will be
*	waveform[i]*gains[j].
*
*	@param pMirror Pointer to driver handle.
*	@param waveform Array of dither waveform in range [0,1]. Maximum length is 2048.
*	@param waveform_length Length of the dither waveform.
*	@param gains Array of actuator values to be dithered. This must match the mirror
*	size in length.
*
*	@return
*	BMCRC		Error status. Possible values:<BR>
*				NO_ERR, ERR_INVALID_DRIVER_TYPE, ERR_INVALID_DITHER_WVFRM, ERR_INVALID_DITHER_GAIN, ERR_PCIE_REGWR.
*/

BMC_API BMCRC BMCConfigureDither(
        struct DM *pMirror,
        const double *waveform,
        uint32_t waveform_length,
        const double *gains);



/*! \brief Turn the the dithering functionality on or off.
*
*    @param pMirror Pointer to driver handle.
*    @param frame_rate Frame rate of dither frames.
*	 @param enable Turns dithering on or off.
*
*    @return
*    BMCRC		Error status. Possible value:<BR>
*				NO_ERR, ERR_INVALID_DITHER_RATE, ERR_PCIE_REGWR.
*/

BMC_API BMCRC BMCEnableDither(
        struct DM *pMirror,
        double frame_rate,
        int enable);

/*! \brief Close driver.
*
*	This function closes the connection to the driver and NULLs out all
*	members of the DM struct.
*
*	@param pMirror	Pointer to driver handle.<BR>
*
*	@return
*	BMCRC		Errors status. Possible values:<BR>
*				NO_ERR, ERR_X64_ONLY, ERR_INVALID_DRIVER_TYPE,
*				ERR_NO_HW, ERR_TIMEOUT,
*/
BMC_API BMCRC BMCClose(struct DM *pMirror);

/*! \brief Return string describing error 
*
*	Provides a string describing an error code. Do NOT modify the string!
*
*	@param err BMC error code.<BR>
*
*	@return
*	const char*	  Static string. Do NOT modify.
*/
BMC_API const char *BMCErrorString(BMCRC err);

// SDK CONFIGURATION FUNCTIONS ////////////////////////////////////////////////

/*! \brief Set the path to search for driver profiles.
*
*   This effects future calls to BMCOpen()
*   The default path is [Install Folder]/Profiles
*
*	@param pMirror		Pointer to the allocated structure used to internally
*            ID the driver.<BR>
*	@param profiles_path	String containing the path containing driver profiles.
*       If NULL, reset to the install directory.
*
*	@return
*	BMCRC		Error status. Possible values:<BR>
*				NO_ERR, ERR_REGISTRY
*
*/
BMC_API BMCRC BMCSetProfilesPath(struct DM *pMirror, const char* profiles_path);

/*! \brief Set the path to search for driver mappings.
*
*   This effects future calls to BMCOpen()
*   The default path is [Profiles Folder]/../Map
*
*	@param pMirror		Pointer to the allocated structure used to internally
*            ID the driver.<BR>
*	@param maps_path	String containing the path containing driver mappings.
*       If NULL, reset to the install directory.
*
*	@return
*	BMCRC		Error status. Possible values:<BR>
*				NO_ERR, ERR_REGISTRY
*
*/
BMC_API BMCRC BMCSetMapsPath(struct DM *pMirror, const char* maps_path);

/*! \brief Set the path to search for calibration tables.
*
*   This effects future calls to BMCOpen()
*   The default path is [Profiles Folder]/../Calibration
*
*	@param pMirror		Pointer to the allocated structure used to internally
*            ID the driver.<BR>
*	@param cals_path	String containing the path containing calibration tables.
*       If NULL, reset to the install directory.
*
*	@return
*	BMCRC		Error status. Possible values:<BR>
*				NO_ERR, ERR_REGISTRY
*
*/
BMC_API BMCRC BMCSetCalibrationsPath(struct DM *pMirror, const char* cals_path);

/*! \brief Set the log file and log level.
*
*   The default log file is in the user's LOCALAPPDATA directory.<BR>
*   Call this before BMCOpen() to make sure the default file is not used.
*   It may be called at any time to change the setting.<BR>
*   The default path is [LOCALAPPDATA]/Boston Micromachines/DM-SDK.log
*
*	@param filePath	String containing the full path of the log file.
*       If NULL, reset to the default file.<BR>
*   @param level    Minimum level for log messages. Set to
*       BMC_LOG_ALL for maximal debugging output.
*
*   @return
*	BMCRC		Error status. Possible values:<BR>
*				NO_ERR,
*
*/
BMC_API BMCRC BMCConfigureLog(const char* filePath, BMC_LOGLEVEL level);

/*! \brief Return string version number.
*
*	@return
*	const char*	  Static string. Do NOT modify.
*/
BMC_API const char * BMCVersionString(void);

#ifdef __cplusplus
}
#endif

#endif // BMCAPI_H
