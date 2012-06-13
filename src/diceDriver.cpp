/*=====================================================
 * DICEDRIVER.CPP
 * Calls C++ shared library of DICE model
 * Takes csv file, computes model, writes to csv file
 *=====================================================*/

#include "libdice.h"

int run_main(int argc, char **argv)
{
  // call application and library initialization
  if (!mclInitializeApplication(NULL,0))
    {
      std::cerr << "could not initialize application properly"
		<< std::endl;
      return -1;
    }
  if (!libdiceInitialize())
    {
      std::cerr << "could not initialize library properly"
		<< std::endl;
      return -1;
    }
  else
    {
      try
	{
	  // Parse arguments

	  // first arg is original csv file
	  mwArray source(argv[1]);
	  // second arg is target csv file
	  mwArray target(argv[2]);

	  // create output array
	  mwArray out1;
	  mwArray out2;

	  // Call diceDriver library function
	  diceDriver(2,out1,out2,source,target);

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
      libdiceTerminate();
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
