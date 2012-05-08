MATLAB Compiler

1. Prerequisites for Deployment 

. Verify the MATLAB Compiler Runtime (MCR) is installed and ensure you    
  have installed version 7.16.   

. If the MCR is not installed, launch MCRInstaller, located in:

  <matlabroot>*/toolbox/compiler/deploy/glnx86/MCRInstaller.zip

For more information about the MCR and the MCR Installer, see 
“Working With the MCR” in the MATLAB Compiler User’s Guide.    



2. Files to Deploy and Package

Files to package for Shared Libraries
=====================================
-libdice.so
-libdice.h
-MCRInstaller.zip 
   - include when building component by clicking "Add MCR" link
     in deploytool
-This readme file

3. Definitions

For information on deployment terminology, go to 
http://www.mathworks.com/help. Select your product and see 
the Glossary in the User’s Guide.


* NOTE: <matlabroot> is the directory where MATLAB is installed on the target machine.


4. Appendix 

A. Linux systems:
   On the target machine, add the MCR directory to the environment variable 
   LD_LIBRARY_PATH by issuing the following commands:

        NOTE: <mcr_root> is the directory where MCR is installed
              on the target machine.         

            setenv LD_LIBRARY_PATH
                $LD_LIBRARY_PATH:
                <mcr_root>/v716/runtime/glnx86:
                <mcr_root>/v716/bin/glnx86:
                <mcr_root>/v716/sys/os/glnx86:
                <mcr_root>/v716/sys/java/jre/glnx86/jre/lib/i386/native_threads:
                <mcr_root>/v716/sys/java/jre/glnx86/jre/lib/i386/server:
                <mcr_root>/v716/sys/java/jre/glnx86/jre/lib/i386
            setenv XAPPLRESDIR <mcr_root>/v716/X11/app-defaults


     
        NOTE: To make these changes persistent after logout on Linux 
              or Mac machines, modify the .cshrc file to include this  
              setenv command.
        NOTE: The environment variable syntax utilizes forward 
              slashes (/), delimited by colons (:).  



