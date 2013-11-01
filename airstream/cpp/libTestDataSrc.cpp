#include <stdlib.h>

float randf(){
  return  (float)rand()/(float)RAND_MAX;
}


// for newDataXY
typedef void* (*allocatorxy_t)(float, float);
typedef void* (*allocatorbutton_t)(int btnId, float x, float y );


allocatorxy_t newDataXYCallback=0;
allocatorbutton_t buttonDownCallback=0;
allocatorbutton_t buttonUpCallback=0;

bool callbacksInitialized=false;

extern "C" {
    //Foo* Foo_new(){ return new Foo(); }
    //void Foo_bar(Foo* foo){ foo->bar(); }
 
  void setCallbacks(allocatorxy_t pyfuncxy, allocatorbutton_t pyfuncbuttondown, allocatorbutton_t pyfuncbuttonup){
    newDataXYCallback = pyfuncxy;
    buttonDownCallback = pyfuncbuttondown;
    buttonUpCallback = pyfuncbuttonup;
    callbacksInitialized=true;
  }

  void
  newDataXY(float &num1, float &num2)
  {
      num1 = randf();
      num2 = randf();
  }

  void update();
}


void update(){
  newDataXYCallback(randf(), randf());
  buttonDownCallback(1, randf(), randf());
  buttonUpCallback(1, randf(), randf());
}

