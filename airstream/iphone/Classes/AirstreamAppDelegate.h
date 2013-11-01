//
//  AirstreamAppDelegate.h
//  Airstream
//
//  Created by Thomas Uram on 9/25/09.
//  Copyright Argonne National Laboratory 2009. All rights reserved.
//

#import <UIKit/UIKit.h>

@class EAGLView;

@interface AirstreamAppDelegate : NSObject <UIApplicationDelegate> {
    UIWindow *window;
    EAGLView *glView;
}

@property (nonatomic, retain) IBOutlet UIWindow *window;
@property (nonatomic, retain) IBOutlet EAGLView *glView;

@end

