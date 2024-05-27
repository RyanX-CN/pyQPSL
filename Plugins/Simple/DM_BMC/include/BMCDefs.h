#pragma once
#ifndef BMCDEFS_H
#define BMCDEFS_H

/// For compatibility with Windows MAX_PATH
#define BMC_MAX_PATH 260

#define BMC_SERIAL_NUMBER_LEN 11

#if !defined(BMCMIF_API)
  #ifdef __cplusplus
    #include <cstdint>
  #else
    #include <stdint.h>
  #endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

/*! \file
*	\section defs Definitions and Error codes.
*/

/*! \brief \enum DRVTYPE an enumeration of the driver interfaces.
*
*	These values are for the type argument in BMCOpen().
*/
typedef enum DRVTYPE {
	BMC_USB,	/*!< USB Driver. */
	BMC_PCIE,	/*!< PCIe Driver. */
	BMC_DUMMY_DRV	/*!< Dummy driver for application testing */
} DRVTYPE;

/*! Maximum DM size. */
#define MAX_DM_SIZE 4096

/*! Default value of ::DM::DevId used to select a device automatically.
 */
#define BMC_DEV_ID_ANY 0U
/*! Special value of ::DM::DevId used to query device information.
 */
#define BMC_DEV_ID_QUERY_PROFILE 0x10000U

struct DM_PRIV;

/*! \struct DM_DRIVER
 * \brief The DM_DRIVER struct stores information about the drive electronics.
 */
typedef struct DM_DRIVER
{
    /// Number of DACs
    unsigned int channel_count;
    /// Driver serial number
    char         serial_number[BMC_SERIAL_NUMBER_LEN+1];
    unsigned int reserved[7];
} DM_DRIVER;

/*! \struct DM
*	\brief The DM struct stores the device info necessary to access the driver.
*
*	When passed to BMCOpen() this struct should have been allocated,
*	but empty. The function will fill it in. For all other functions 
*	this struct is used as a means to pass all identifying values 
*	together.
*
*	Driver_type - Driver interface. USB, PCIe, or DPIO2.
*	DevId - The driver's ID as seen by the system. 
*	ActCount - Number of actuators on the driver/mirror.
*/
typedef struct DM
{
	unsigned int	Driver_Type;		/*!< Driver interface type. */
	unsigned int	DevId;				/*!< Driver ID number. */
	unsigned int	HVA_Type;			/*!< Config ID for PCIe based drivers. */
	unsigned int	use_fiber;			/*!< PCIe board uses fiber */
	unsigned int	use_CL;				/*!< PCIe board uses CameraLink*/
	unsigned int	burst_mode;			/*!< PCIe board burst mode. */
	unsigned int	fiber_mode;			/*!< PCIe board fiber mode. "Kilo" or "S-Driver."*/
	unsigned int	ActCount;			/*!< Number of actuators. */
    unsigned int	MaxVoltage;			/*!< Maximum driver voltage output.
                                             Opaque, do not modify.*/
    unsigned int	VoltageLimit;		/*!< Voltage limit.
                                             Opaque, do not modify. */
    char			mapping[BMC_MAX_PATH];	/*!< name of mapping. */
    unsigned int	inactive[MAX_DM_SIZE];	/*!< Store inactive actuators. */
    char			profiles_path[BMC_MAX_PATH]; /*!< profiles search directory */
    char			maps_path[BMC_MAX_PATH]; /*!< maps search directory */
    char            cals_path[BMC_MAX_PATH]; /*!< calibration search directory */
    char			cal[BMC_MAX_PATH];      /*!< name of calibration file. */
    /// DM Serial Number
    char            serial_number[BMC_SERIAL_NUMBER_LEN+1];
    DM_DRIVER       driver;             /*!< Driver information */

    struct DM_PRIV* priv;               /*!< Private data used internally.
                                             Opaque, do not touch. */
} DM;
typedef struct DM* DMHANDLE;

/*! \brief \enum BMCRC Return codes
*
*	All possible return codes from all functions.
*/
typedef enum BMCRC {
	NO_ERR,						/*!< 0: All is well. */
	ERR_UNKNOWN,				/*!< 1: General error. */
	ERR_NO_HW,					/*!< 2: No drivers found. */
	ERR_INIT_DRIVER,			/*!< 3: Error initializing driver. */
	ERR_SERIAL_NUMBER,			/*!< 4: Invalid serial number. */
	ERR_MALLOC,					/*!< 5: Error allocating memory */
	ERR_INVALID_DRIVER_TYPE,	/*!< 6: Invalid driver type. */
	ERR_INVALID_ACTUATOR_COUNT,	/*!< 7: Invalid Number of actuators. */
	ERR_INVALID_LUT,			/*!< 8: Invalid mapping lookup table. */
	ERR_ACTUATOR_ID,			/*!< 9: Incorrect actuator ID. */
	ERR_OPENFILE,				/*!< 10: Error opening mapping. */
	ERR_NOT_IMPLEMENTED,		/*!< 11: Function not implemented. */
	ERR_TIMEOUT,				/*!< 12: Operation timed out. */
	ERR_POKE,					/*!< 13: Error poking actuator. */
	ERR_REGISTRY,				/*!< 14: Error in system registry. */
	// PCIe specific
	ERR_PCIE_REGWR,				/*!< 15: Error writing register. */
	ERR_PCIE_REGRD,				/*!< 16: Error reading register. */
	ERR_PCIE_BURST,				/*!< 17: Error writing burst array. */
	ERR_X64_ONLY,				/*!< 18: Function Only available on 64-bit OS. */
	ERR_PULSE_RANGE,			/*!< 19: Sync pulse out of range. */
	ERR_INVALID_SEQUENCE,       /*!< 20: Invalid sequence. */
	ERR_INVALID_SEQUENCE_RATE,  /*!< 21: Invalid sequence rate. */
	ERR_INVALID_DITHER_WVFRM,   /*!< 22: Invalid dither waveform. */
	ERR_INVALID_DITHER_GAIN,    /*!< 23: Invalid dither gain. */
    ERR_INVALID_DITHER_RATE,    /*!< 24: Invalid dither rate. */
    /* New in 2.0 */
    ERR_BADARG,                 /*!< 25: Generic invalid argument. */
    ERR_SEGMENT_ID,             /*!< 26: Incorrect segment ID. */
    ERR_INVALID_CALIBRATION,    /*!< 27: Calibration table not set. */
    ERR_OUT_OF_LUT_RANGE,       /*!< 28: Values not found in lookup table. */
    ERR_DRIVER_NOT_OPEN,        /*!< 29: Tried to operate driver before opening. */
    ERR_DRIVER_ALREADY_OPEN,    /*!< 30: Tried to open driver when already open. */
    ERR_FILE_PERMISSIONS,       /*!< 31: Failed to read or write a file due to OS
                                  permissions. */
    /* New in 2.2 */
    ERR_FILE_FORMAT,            /*!< 32: Error reading file, likely it was
                                  formatted incorrectly. */
    ERR_USB_READ,               /*!< 33: Error reading USB. */
    ERR_USB_WRITE,              /*!< 34: Error writing USB. */
    ERR_USB_OTHER,              /*!< 35: Unknown USB error. Reserved: Name may change. */
} BMCRC;

/*! \brief \enum BMC_LOGLEVEL Log levels
 *
 * All messages above the given level will be logged to a file and to the
 *  console. \see BMCConfigureLog()
 */
typedef enum BMC_LOGLEVEL {
    BMC_LOG_ALL,                /*!< 0: Log all messages */
    BMC_LOG_TRACE = BMC_LOG_ALL,/*!< 0: Log all messages */
    BMC_LOG_DEBUG,              /*!< 1: Log all messages above debug level */
    BMC_LOG_INFO,               /*!< 2: Log all messages above info level */
    BMC_LOG_WARN,               /*!< 3: Log all messages above warning level */
    BMC_LOG_ERROR,              /*!< 4: Log all messages above error level */
    BMC_LOG_FATAL,              /*!< 5: Log only fatal error messages */
    BMC_LOG_OFF                 /*!< 6: Turn off all log messages */
} BMC_LOGLEVEL;

/*! \brief \enum DMSegmentAxis Segment axis of motion
 *
 * For some segmented DMs, the segments may be moved and tilted on more than
 * one axis. This enum selects which axis to set or query.
 *  \see BMCGetSegmentRange()
 */
typedef enum DMSegmentAxis {
    DM_Piston,      /*!< Piston */
    DM_XTilt,       /*!< Tilt in the X direction */
    DM_YTilt,       /*!< Tilt in the Y direction */
} DMSegmentAxis;

#ifdef __cplusplus
}
#endif

#endif // BMCDEFS_H
