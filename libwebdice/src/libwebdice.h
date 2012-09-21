//
// MATLAB Compiler: 4.17 (R2012a)
// Date: Fri Sep 21 07:01:19 2012
// Arguments: "-B" "macro_default" "-W" "cpplib:libwebdice" "-T" "link:lib"
// "-d" "/autonfs/home/mattgee/chicagowebdice/libwebdice/src" "-w"
// "enable:specified_file_mismatch" "-w" "enable:repeated_file" "-w"
// "enable:switch_ignored" "-w" "enable:missing_lib_sentinel" "-w"
// "enable:demo_license" "-v"
// "/autonfs/home/mattgee/chicagowebdice/src/cell2csv.m"
// "/autonfs/home/mattgee/chicagowebdice/src/DICE2007Param.m"
// "/autonfs/home/mattgee/chicagowebdice/src/DICE2007ParamExo.m"
// "/autonfs/home/mattgee/chicagowebdice/src/DICE2007Run.m"
// "/autonfs/home/mattgee/chicagowebdice/src/DICE2007Setup.m"
// "/autonfs/home/mattgee/chicagowebdice/src/DICE2007Step.m"
// "/autonfs/home/mattgee/chicagowebdice/src/diceDriver.m"
// "/autonfs/home/mattgee/chicagowebdice/src/OptimizeParam.m"
// "/autonfs/home/mattgee/chicagowebdice/src/OptimizeParamExo.m"
// "/autonfs/home/mattgee/chicagowebdice/src/OptimizeRun.m"
// "/autonfs/home/mattgee/chicagowebdice/src/simDICE.m" 
//

#ifndef __libwebdice_h
#define __libwebdice_h 1

#if defined(__cplusplus) && !defined(mclmcrrt_h) && defined(__linux__)
#  pragma implementation "mclmcrrt.h"
#endif
#include "mclmcrrt.h"
#include "mclcppclass.h"
#ifdef __cplusplus
extern "C" {
#endif

#if defined(__SUNPRO_CC)
/* Solaris shared libraries use __global, rather than mapfiles
 * to define the API exported from a shared library. __global is
 * only necessary when building the library -- files including
 * this header file to use the library do not need the __global
 * declaration; hence the EXPORTING_<library> logic.
 */

#ifdef EXPORTING_libwebdice
#define PUBLIC_libwebdice_C_API __global
#else
#define PUBLIC_libwebdice_C_API /* No import statement needed. */
#endif

#define LIB_libwebdice_C_API PUBLIC_libwebdice_C_API

#elif defined(_HPUX_SOURCE)

#ifdef EXPORTING_libwebdice
#define PUBLIC_libwebdice_C_API __declspec(dllexport)
#else
#define PUBLIC_libwebdice_C_API __declspec(dllimport)
#endif

#define LIB_libwebdice_C_API PUBLIC_libwebdice_C_API


#else

#define LIB_libwebdice_C_API

#endif

/* This symbol is defined in shared libraries. Define it here
 * (to nothing) in case this isn't a shared library. 
 */
#ifndef LIB_libwebdice_C_API 
#define LIB_libwebdice_C_API /* No special import/export declaration */
#endif

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV libwebdiceInitializeWithHandlers(
       mclOutputHandlerFcn error_handler, 
       mclOutputHandlerFcn print_handler);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV libwebdiceInitialize(void);

extern LIB_libwebdice_C_API 
void MW_CALL_CONV libwebdiceTerminate(void);



extern LIB_libwebdice_C_API 
void MW_CALL_CONV libwebdicePrintStackTrace(void);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxCell2csv(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDICE2007Param(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDICE2007ParamExo(int nlhs, mxArray *plhs[], int nrhs, mxArray 
                                      *prhs[]);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDICE2007Run(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDICE2007Setup(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDICE2007Step(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDiceDriver(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxOptimizeParam(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxOptimizeParamExo(int nlhs, mxArray *plhs[], int nrhs, mxArray 
                                      *prhs[]);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxOptimizeRun(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);

extern LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxSimDICE(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);


#ifdef __cplusplus
}
#endif

#ifdef __cplusplus

/* On Windows, use __declspec to control the exported API */
#if defined(_MSC_VER) || defined(__BORLANDC__)

#ifdef EXPORTING_libwebdice
#define PUBLIC_libwebdice_CPP_API __declspec(dllexport)
#else
#define PUBLIC_libwebdice_CPP_API __declspec(dllimport)
#endif

#define LIB_libwebdice_CPP_API PUBLIC_libwebdice_CPP_API

#else

#if !defined(LIB_libwebdice_CPP_API)
#if defined(LIB_libwebdice_C_API)
#define LIB_libwebdice_CPP_API LIB_libwebdice_C_API
#else
#define LIB_libwebdice_CPP_API /* empty! */ 
#endif
#endif

#endif

extern LIB_libwebdice_CPP_API void MW_CALL_CONV cell2csv(const mwArray& fileName, const mwArray& cellArray, const mwArray& separator, const mwArray& excelYear, const mwArray& decimal);

extern LIB_libwebdice_CPP_API void MW_CALL_CONV DICE2007Param(int nargout, mwArray& param);

extern LIB_libwebdice_CPP_API void MW_CALL_CONV DICE2007ParamExo(int nargout, mwArray& param, const mwArray& param_in1);

extern LIB_libwebdice_CPP_API void MW_CALL_CONV DICE2007Run(int nargout, mwArray& vars, const mwArray& vars_in1, const mwArray& param);

extern LIB_libwebdice_CPP_API void MW_CALL_CONV DICE2007Setup(int nargout, mwArray& vars, const mwArray& vars_in1, const mwArray& param);

extern LIB_libwebdice_CPP_API void MW_CALL_CONV DICE2007Step(int nargout, mwArray& vars, const mwArray& vars_in1, const mwArray& param, const mwArray& t);

extern LIB_libwebdice_CPP_API void MW_CALL_CONV diceDriver(int nargout, mwArray& v, mwArray& p, const mwArray& args);

extern LIB_libwebdice_CPP_API void MW_CALL_CONV OptimizeParam(int nargout, mwArray& param);

extern LIB_libwebdice_CPP_API void MW_CALL_CONV OptimizeParamExo(int nargout, mwArray& param, const mwArray& param_in1);

extern LIB_libwebdice_CPP_API void MW_CALL_CONV OptimizeRun(int nargout, mwArray& vars, const mwArray& vars_in1, const mwArray& param);

extern LIB_libwebdice_CPP_API void MW_CALL_CONV simDICE(int nargout, mwArray& vars, mwArray& param, const mwArray& options);

#endif
#endif
