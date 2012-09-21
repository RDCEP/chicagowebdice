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

#include <stdio.h>
#define EXPORTING_libwebdice 1
#include "libwebdice.h"

static HMCRINSTANCE _mcr_inst = NULL;


#ifdef __cplusplus
extern "C" {
#endif

static int mclDefaultPrintHandler(const char *s)
{
  return mclWrite(1 /* stdout */, s, sizeof(char)*strlen(s));
}

#ifdef __cplusplus
} /* End extern "C" block */
#endif

#ifdef __cplusplus
extern "C" {
#endif

static int mclDefaultErrorHandler(const char *s)
{
  int written = 0;
  size_t len = 0;
  len = strlen(s);
  written = mclWrite(2 /* stderr */, s, sizeof(char)*len);
  if (len > 0 && s[ len-1 ] != '\n')
    written += mclWrite(2 /* stderr */, "\n", sizeof(char));
  return written;
}

#ifdef __cplusplus
} /* End extern "C" block */
#endif

/* This symbol is defined in shared libraries. Define it here
 * (to nothing) in case this isn't a shared library. 
 */
#ifndef LIB_libwebdice_C_API
#define LIB_libwebdice_C_API /* No special import/export declaration */
#endif

LIB_libwebdice_C_API 
bool MW_CALL_CONV libwebdiceInitializeWithHandlers(
    mclOutputHandlerFcn error_handler,
    mclOutputHandlerFcn print_handler)
{
    int bResult = 0;
  if (_mcr_inst != NULL)
    return true;
  if (!mclmcrInitialize())
    return false;
    {
        mclCtfStream ctfStream = 
            mclGetEmbeddedCtfStream((void *)(libwebdiceInitializeWithHandlers));
        if (ctfStream) {
            bResult = mclInitializeComponentInstanceEmbedded(   &_mcr_inst,
                                                                error_handler, 
                                                                print_handler,
                                                                ctfStream);
            mclDestroyStream(ctfStream);
        } else {
            bResult = 0;
        }
    }  
    if (!bResult)
    return false;
  return true;
}

LIB_libwebdice_C_API 
bool MW_CALL_CONV libwebdiceInitialize(void)
{
  return libwebdiceInitializeWithHandlers(mclDefaultErrorHandler, mclDefaultPrintHandler);
}

LIB_libwebdice_C_API 
void MW_CALL_CONV libwebdiceTerminate(void)
{
  if (_mcr_inst != NULL)
    mclTerminateInstance(&_mcr_inst);
}

LIB_libwebdice_C_API 
void MW_CALL_CONV libwebdicePrintStackTrace(void) 
{
  char** stackTrace;
  int stackDepth = mclGetStackTrace(&stackTrace);
  int i;
  for(i=0; i<stackDepth; i++)
  {
    mclWrite(2 /* stderr */, stackTrace[i], sizeof(char)*strlen(stackTrace[i]));
    mclWrite(2 /* stderr */, "\n", sizeof(char)*strlen("\n"));
  }
  mclFreeStackTrace(&stackTrace, stackDepth);
}


LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxCell2csv(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[])
{
  return mclFeval(_mcr_inst, "cell2csv", nlhs, plhs, nrhs, prhs);
}

LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDICE2007Param(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[])
{
  return mclFeval(_mcr_inst, "DICE2007Param", nlhs, plhs, nrhs, prhs);
}

LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDICE2007ParamExo(int nlhs, mxArray *plhs[], int nrhs, mxArray 
                                      *prhs[])
{
  return mclFeval(_mcr_inst, "DICE2007ParamExo", nlhs, plhs, nrhs, prhs);
}

LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDICE2007Run(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[])
{
  return mclFeval(_mcr_inst, "DICE2007Run", nlhs, plhs, nrhs, prhs);
}

LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDICE2007Setup(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[])
{
  return mclFeval(_mcr_inst, "DICE2007Setup", nlhs, plhs, nrhs, prhs);
}

LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDICE2007Step(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[])
{
  return mclFeval(_mcr_inst, "DICE2007Step", nlhs, plhs, nrhs, prhs);
}

LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxDiceDriver(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[])
{
  return mclFeval(_mcr_inst, "diceDriver", nlhs, plhs, nrhs, prhs);
}

LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxOptimizeParam(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[])
{
  return mclFeval(_mcr_inst, "OptimizeParam", nlhs, plhs, nrhs, prhs);
}

LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxOptimizeParamExo(int nlhs, mxArray *plhs[], int nrhs, mxArray 
                                      *prhs[])
{
  return mclFeval(_mcr_inst, "OptimizeParamExo", nlhs, plhs, nrhs, prhs);
}

LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxOptimizeRun(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[])
{
  return mclFeval(_mcr_inst, "OptimizeRun", nlhs, plhs, nrhs, prhs);
}

LIB_libwebdice_C_API 
bool MW_CALL_CONV mlxSimDICE(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[])
{
  return mclFeval(_mcr_inst, "simDICE", nlhs, plhs, nrhs, prhs);
}

LIB_libwebdice_CPP_API 
void MW_CALL_CONV cell2csv(const mwArray& fileName, const mwArray& cellArray, const 
                           mwArray& separator, const mwArray& excelYear, const mwArray& 
                           decimal)
{
  mclcppMlfFeval(_mcr_inst, "cell2csv", 0, 0, 5, &fileName, &cellArray, &separator, &excelYear, &decimal);
}

LIB_libwebdice_CPP_API 
void MW_CALL_CONV DICE2007Param(int nargout, mwArray& param)
{
  mclcppMlfFeval(_mcr_inst, "DICE2007Param", nargout, 1, 0, &param);
}

LIB_libwebdice_CPP_API 
void MW_CALL_CONV DICE2007ParamExo(int nargout, mwArray& param, const mwArray& param_in1)
{
  mclcppMlfFeval(_mcr_inst, "DICE2007ParamExo", nargout, 1, 1, &param, &param_in1);
}

LIB_libwebdice_CPP_API 
void MW_CALL_CONV DICE2007Run(int nargout, mwArray& vars, const mwArray& vars_in1, const 
                              mwArray& param)
{
  mclcppMlfFeval(_mcr_inst, "DICE2007Run", nargout, 1, 2, &vars, &vars_in1, &param);
}

LIB_libwebdice_CPP_API 
void MW_CALL_CONV DICE2007Setup(int nargout, mwArray& vars, const mwArray& vars_in1, 
                                const mwArray& param)
{
  mclcppMlfFeval(_mcr_inst, "DICE2007Setup", nargout, 1, 2, &vars, &vars_in1, &param);
}

LIB_libwebdice_CPP_API 
void MW_CALL_CONV DICE2007Step(int nargout, mwArray& vars, const mwArray& vars_in1, const 
                               mwArray& param, const mwArray& t)
{
  mclcppMlfFeval(_mcr_inst, "DICE2007Step", nargout, 1, 3, &vars, &vars_in1, &param, &t);
}

LIB_libwebdice_CPP_API 
void MW_CALL_CONV diceDriver(int nargout, mwArray& v, mwArray& p, const mwArray& args)
{
  mclcppMlfFeval(_mcr_inst, "diceDriver", nargout, 2, 1, &v, &p, &args);
}

LIB_libwebdice_CPP_API 
void MW_CALL_CONV OptimizeParam(int nargout, mwArray& param)
{
  mclcppMlfFeval(_mcr_inst, "OptimizeParam", nargout, 1, 0, &param);
}

LIB_libwebdice_CPP_API 
void MW_CALL_CONV OptimizeParamExo(int nargout, mwArray& param, const mwArray& param_in1)
{
  mclcppMlfFeval(_mcr_inst, "OptimizeParamExo", nargout, 1, 1, &param, &param_in1);
}

LIB_libwebdice_CPP_API 
void MW_CALL_CONV OptimizeRun(int nargout, mwArray& vars, const mwArray& vars_in1, const 
                              mwArray& param)
{
  mclcppMlfFeval(_mcr_inst, "OptimizeRun", nargout, 1, 2, &vars, &vars_in1, &param);
}

LIB_libwebdice_CPP_API 
void MW_CALL_CONV simDICE(int nargout, mwArray& vars, mwArray& param, const mwArray& 
                          options)
{
  mclcppMlfFeval(_mcr_inst, "simDICE", nargout, 2, 1, &vars, &param, &options);
}

