WEBROOT=/var/www
MCRINSTALLROOT=/tmp/mcr
MATLABROOT=/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716
X86MCRURL=http://www.mathworks.com/supportfiles/MCR_Runtime/R2012a/MCR_R2012a_glnx86_installer.zip
X86_64MCRURL=http://www.mathworks.com/supportfiles/MCR_Runtime/R2012a/MCR_R2012a_glnxa64_installer.zip
GIT_URL=git://github.com/RDCEP/chicagowebdice.git
LD_LIBRARY_PATH=$(WEBROOT)/lib:$(MATLABROOT)/runtime/glnx86:$(MATLABROOT)/sys/os/glnx86:$(MATLABROOT)/sys/java/jre/glnx86/jre/lib/i386/native_threads:$(MATLABROOT)/sys/java/jre/glnx86/jre/lib/i386/server:$(MATLABROOT)/sys/java/jre/glnx86/jre/lib/i386:$LD_LIBRARY_PATH
XAPPRLRESDIR=$(MATLABROOT)/X11/app-defaults
MATLAB_FILES=src/DICE2007Param.m src/DICE2007ParamExo.m src/DICE2007Run.m src/DICE2007Setup.m src/DICE2007Step.m src/OptimizeParam.m src/OptimizeParamExo.m src/OptimizeRun.m src/simDICE.m
MCC_OPTS=-T link:lib -nodisplay -d lib/ -v
CPP_FILES=src/libwebdice.cpp

unexport DISPLAY

compile: bin/diceDriver

lib/libwebdice32.so:
	mcc -W cpplib:libwebdice32 -b32 $(MCC_OPTS) $(MATLAB_FILES)

lib/libwebdice64.so:
	mcc -W cpplib:libwebdice64 -b64 $(MCC_OPTS) $(MATLAB_FILES)

bin/diceDriver32: lib/libwebdice32.so
	mbuild $(CPP_FILES) -glnx86 -Llib/ -Isrc/ -llib/libwebdice32.so

bin/diceDriver64: lib/libwebdice64.so
	mbuild $(CPP_FILES) -glnxa64 -Llib/ -Isrc/ -llib/libwebdice64.so

bin/diceDriver: bin/diceDriver32
	ln -s `pwd`/bin/diceDriver32 bin/diceDriver

setup:
	apt-get install lamp-server git unzip ia32-libs
	mkdir -p $(MCRINSTALLROOT)
	## Comment the following and uncomment the next line if running a 64-bit
	## build of bin/diceDriver. It's unlikely that this is the case.
	wget $(X86MCRURL) -o $(MCRINSTALLROOT)/MCRInstaller.zip
	# wget $(X86_64MCRURL) -o $(MCRINSTALLROOT)/MCRInstaller.zip
	unzip $(MCRINSTALLROOT)/MCRInstaller.zip
	$(MCRINSTALLROOT)/install -mode silent
	mkdir -p $(WEBROOT)/development
	git clone -b production $(GIT_URL) $(WEBROOT)
	## Uncomment if you also want a development install.
	# git clone -b master $(GIT_URL) $(WEBROOT)/development

test:
	$(WEBROOT)/bin/diceDriver run DICE2007Run step DICE2007Step

clean:
	rm -rf lib/*.so bin/diceDriver32 bin/diceDriver64 bin/diceDriver