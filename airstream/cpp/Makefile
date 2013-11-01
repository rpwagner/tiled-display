CC=gcc
CPP=g++

CFLAGS += -fPIC

LIBEXT=so

INC=
LIB=

all: libTestDataSrc.${LIBEXT}

libTestDataSrc.o: libTestDataSrc.cpp
	$(CPP) $(CFLAGS) $(INC) -c $<

libTestDataSrc.${LIBEXT}: libTestDataSrc.o
	${CPP} -shared libTestDataSrc.o ${LIB} -o libTestDataSrc.${LIBEXT}


