//
//  AirstreamAppDelegate.m
//  Airstream
//
//  Created by Thomas Uram on 9/25/09.
//  Copyright Argonne National Laboratory 2009. All rights reserved.
//

#import "AirstreamAppDelegate.h"
#import "EAGLView.h"

@implementation AirstreamAppDelegate

@synthesize window;
@synthesize glView;

- (void)applicationDidFinishLaunching:(UIApplication *)application {
    
	glView.animationInterval = 1.0 / 60.0;
	//[glView startAnimation];
}


- (void)applicationWillResignActive:(UIApplication *)application {
	glView.animationInterval = 1.0 / 5.0;
}


- (void)applicationDidBecomeActive:(UIApplication *)application {
	glView.animationInterval = 1.0 / 60.0;
}


- (void)dealloc {
	[window release];
	[glView release];
	[super dealloc];
}

@end
