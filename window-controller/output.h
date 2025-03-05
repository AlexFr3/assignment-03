#ifndef OUTPUT_H
#define OUTPUT_H
#include "Arduino.h"

/*
initializes the output device
*/
void outputInit();

/*
writes the message on output device
*/
void writeMessage(String message);

/*
sets the cursor on the third line
*/
void setNextLine();

/*
sets the cursor to the start position
*/
void resetCursor();

/*
clears the output device
*/
void clearOutput();
#endif
