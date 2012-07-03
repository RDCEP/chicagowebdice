/*=====================================================================
 * DICEDRIVER.CPP
 * Calls C++ shared library of DICE model
 * Takes input from command line args, computes model, writes to stdout
 *====================================================================*/

#include "libwebdice.h"

int run_main(int argc, char **argv)
{
  // call application and library initialization
  if (!mclInitializeApplication(NULL,0))
    {
      std::cerr << "could not initialize application properly"
		<< std::endl;
      return -1;
    }
  if (!libwebdiceInitialize())
    {
      std::cerr << "could not initialize library properly"
		<< std::endl;
      return -1;
    }
  else
    {
      try
	{
	  // Parse arguments (will be packaged and passed to MATLAB

	  // set up string matrix
	  char* str[20];

	  for (int i = 0; i < argc - 1; i++)
	    {
	      str[i] = argv[i+1];
	    }

	  // cast to const
	  const char** str2 = (const char**) str;

	  // Create character array
	  const mwArray arg(argc - 1, str2);

	  // create output array
	  mwArray out1;
	  mwArray out2;
	  
	  // Call diceDriver library function
	  diceDriver(2,out1,out2,arg);

	  // Display success
	  std::cout << "Success." << std::endl;
	}
      catch (const mwException& e)
	{
	  std::cerr << e.what() << std::endl;
	  return -2;
	}
      catch (...)
	{
	  std::cerr << "Unexpected error thrown" << std::endl;
	  return -3;
	}
      // Call application and library termination routine
      libwebdiceTerminate();
    }
  mclTerminateApplication();
  return 0;
}

int main(int argc, char **argv)
{
  mclmcrInitialize();
  const char** constargv = (const char**)argv;
  return mclRunMain((mclMainFcnType)run_main,argc,constargv);
}
