//
//  EAGLView.m
//  Airstream
//
//  Created by Thomas Uram on 9/25/09.
//  Copyright Argonne National Laboratory 2009. All rights reserved.
//
// This simple example of GL was adopted to provide a development path forward.
// At present, it uses a rotating cube to show the touch position and indicate activity


#import <stdio.h>
#import <sys/socket.h>
#import <fcntl.h>
#import <arpa/inet.h>

#import <QuartzCore/QuartzCore.h>
#import <OpenGLES/EAGLDrawable.h>

#import "EAGLView.h"

#define CONNECT_PORT 11000
#define USE_DEPTH_BUFFER 0

Boolean started = NO;
int sock;
CGPoint pt,startPt;

// A class extension to declare private methods
@interface EAGLView ()

@property (nonatomic, retain) EAGLContext *context;
@property (nonatomic, assign) NSTimer *animationTimer;

- (BOOL) createFramebuffer;
- (void) destroyFramebuffer;

@end


@implementation EAGLView

@synthesize context;
@synthesize animationTimer;
@synthesize animationInterval;
@synthesize statusLabel;
@synthesize splashView;
@synthesize configureButton;
@synthesize configureView;


// You must implement this method
+ (Class)layerClass {
    return [CAEAGLLayer class];
}

- (BOOL) isMultipleTouchEnabled 
{
    return YES;
} 

- (BOOL) sendMessage:(CGPoint)pt
{
    char echoString[32];                /* String to send to echo server */
    unsigned int echoStringLen;      /* Length of string to echo */
    sprintf(echoString,"2,-1,1,%f,%f,1,0", pt.x/self.frame.size.width, pt.y/self.frame.size.height );
    //NSLog(@"sending: %s", echoString);
    echoStringLen = strlen(echoString);          /* Determine input length */

    unsigned char packed[2];
    packed[0] = echoStringLen >> 8;
    packed[1] = echoStringLen % 256;
    
    if (send(sock, packed, 2, 0) != 2)
    {
        NSLog(@"send() sent a different number of bytes than expected");
        return NO;
    }

    /* Send the string to the server */
    if (send(sock, echoString, echoStringLen, 0) != echoStringLen)
    {
        NSLog(@"send() sent a different number of bytes than expected");
        return NO;
    }
    
    return YES;
    
}

- (void) touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event 
{ 
    if( started )
    {
        pt = [[touches anyObject] locationInView:self];
        [self sendMessage:pt];
        startPt = pt;
    }
    
}

- (void) touchesMoved:(NSSet*)touches withEvent:(UIEvent*)event 
{ 
    if( started )
    {
        pt = [[touches anyObject] locationInView:self];
        [self sendMessage:pt];
    }
}

- (void) touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event 
{ 
    if( started )
    {
        pt = [[touches anyObject] locationInView:self];
        [self sendMessage:pt];
    }
}


//The GL view is stored in the nib file. When it's unarchived it's sent -initWithCoder:
- (id)initWithCoder:(NSCoder*)coder {
    
    if ((self = [super initWithCoder:coder])) {
        // Get the layer
        CAEAGLLayer *eaglLayer = (CAEAGLLayer *)self.layer;
        
        eaglLayer.opaque = YES;
        eaglLayer.drawableProperties = [NSDictionary dictionaryWithObjectsAndKeys:
                                        [NSNumber numberWithBool:NO], kEAGLDrawablePropertyRetainedBacking, kEAGLColorFormatRGBA8, kEAGLDrawablePropertyColorFormat, nil];
        
        context = [[EAGLContext alloc] initWithAPI:kEAGLRenderingAPIOpenGLES1];
        
        if (!context || ![EAGLContext setCurrentContext:context]) {
            [self release];
            return nil;
        }
        
        animationInterval = 1.0 / 60.0;
    }
    return self;
}

#define SQUARE_VERTEX 0.15f

- (void)drawView {
    
    // Replace the implementation of this method to do your own custom drawing
    
    const GLfloat squareVertices[] = {
        -SQUARE_VERTEX, -SQUARE_VERTEX,
        SQUARE_VERTEX,  -SQUARE_VERTEX,
        -SQUARE_VERTEX,  SQUARE_VERTEX,
        SQUARE_VERTEX,   SQUARE_VERTEX,
    };
    const GLubyte squareColors[] = {
        255, 255,   0, 255,
        0,   255, 255, 255,
        0,     0,   0,   0,
        255,   0, 255, 255,
    };
    
    if(!started)
        pt = CGPointMake(160,240);

    [EAGLContext setCurrentContext:context];
    
    glBindFramebufferOES(GL_FRAMEBUFFER_OES, viewFramebuffer);
    glViewport(0, 0, backingWidth, backingHeight);
    
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glTranslatef((pt.x-160)/160,(240-pt.y)/240,0);
    glOrthof(-1.0f, 1.0f, -1.5f, 1.5f, -1.0f, 1.0f);
    glMatrixMode(GL_MODELVIEW);
    glRotatef(3.0f, 0.0f, 0.0f, 1.0f);
    
    //glClearColor(0.5f, 0.5f, 0.5f, 1.0f);
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);
    
    glVertexPointer(2, GL_FLOAT, 0, squareVertices);
    glEnableClientState(GL_VERTEX_ARRAY);
    glColorPointer(4, GL_UNSIGNED_BYTE, 0, squareColors);
    glEnableClientState(GL_COLOR_ARRAY);
    
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
    glBindRenderbufferOES(GL_RENDERBUFFER_OES, viewRenderbuffer);
    [context presentRenderbuffer:GL_RENDERBUFFER_OES];
}


- (void)layoutSubviews {
    [EAGLContext setCurrentContext:context];
    [self destroyFramebuffer];
    [self createFramebuffer];
    [self drawView];
}


- (BOOL)createFramebuffer {
    
    glGenFramebuffersOES(1, &viewFramebuffer);
    glGenRenderbuffersOES(1, &viewRenderbuffer);
    
    glBindFramebufferOES(GL_FRAMEBUFFER_OES, viewFramebuffer);
    glBindRenderbufferOES(GL_RENDERBUFFER_OES, viewRenderbuffer);
    [context renderbufferStorage:GL_RENDERBUFFER_OES fromDrawable:(CAEAGLLayer*)self.layer];
    glFramebufferRenderbufferOES(GL_FRAMEBUFFER_OES, GL_COLOR_ATTACHMENT0_OES, GL_RENDERBUFFER_OES, viewRenderbuffer);
    
    glGetRenderbufferParameterivOES(GL_RENDERBUFFER_OES, GL_RENDERBUFFER_WIDTH_OES, &backingWidth);
    glGetRenderbufferParameterivOES(GL_RENDERBUFFER_OES, GL_RENDERBUFFER_HEIGHT_OES, &backingHeight);
    
    if (USE_DEPTH_BUFFER) {
        glGenRenderbuffersOES(1, &depthRenderbuffer);
        glBindRenderbufferOES(GL_RENDERBUFFER_OES, depthRenderbuffer);
        glRenderbufferStorageOES(GL_RENDERBUFFER_OES, GL_DEPTH_COMPONENT16_OES, backingWidth, backingHeight);
        glFramebufferRenderbufferOES(GL_FRAMEBUFFER_OES, GL_DEPTH_ATTACHMENT_OES, GL_RENDERBUFFER_OES, depthRenderbuffer);
    }
    
    if(glCheckFramebufferStatusOES(GL_FRAMEBUFFER_OES) != GL_FRAMEBUFFER_COMPLETE_OES) {
        NSLog(@"failed to make complete framebuffer object %x", glCheckFramebufferStatusOES(GL_FRAMEBUFFER_OES));
        return NO;
    }
    
    return YES;
}


- (void)destroyFramebuffer {
    
    glDeleteFramebuffersOES(1, &viewFramebuffer);
    viewFramebuffer = 0;
    glDeleteRenderbuffersOES(1, &viewRenderbuffer);
    viewRenderbuffer = 0;
    
    if(depthRenderbuffer) {
        glDeleteRenderbuffersOES(1, &depthRenderbuffer);
        depthRenderbuffer = 0;
    }
}

- (void)startAnimation {
    self.animationTimer = [NSTimer scheduledTimerWithTimeInterval:animationInterval target:self selector:@selector(drawView) userInfo:nil repeats:YES];
}


- (void)stopAnimation {
    self.animationTimer = nil;
}


- (void)setAnimationTimer:(NSTimer *)newTimer {
    [animationTimer invalidate];
    animationTimer = newTimer;
}

- (void)setAnimationInterval:(NSTimeInterval)interval {
    
    animationInterval = interval;
    if (animationTimer) {
        [self stopAnimation];
        [self startAnimation];
    }
}

/* Callback for configure (gear) button */
- (IBAction)onConfigure
{
    [UIView beginAnimations:nil context:nil];
    configureView.center = CGPointMake(160,19);
    configureButton.alpha = 0.0;
    [UIView commitAnimations];
}

/* Callback for Connect button */
- (IBAction)onGo
{
    [addrField resignFirstResponder];
    [portField resignFirstResponder];
    
    struct sockaddr_in echoServAddr; /* Echo server address */
    unsigned short echoServPort;     /* Echo server port */
    const char *servIP;              /* Server IP address (dotted quad) */

    servIP = [addrField.text cStringUsingEncoding:NSASCIIStringEncoding];  
    //echoServPort = [portField.text cStringUsingEncoding:NSASCIIStringEncoding]; 
    echoServPort = CONNECT_PORT;
    
    /* Create a reliable, stream socket using TCP */
    if ((sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
    {
        NSLog(@"socket() failed");
        return;
    }
    
    /* Construct the server address structure */
    memset(&echoServAddr, 0, sizeof(echoServAddr));     /* Zero out structure */
    echoServAddr.sin_family      = AF_INET;             /* Internet address family */
    echoServAddr.sin_addr.s_addr = inet_addr(servIP);   /* Server IP address */
    echoServAddr.sin_port        = htons(echoServPort); /* Server port */
    
    /* Establish the connection to the echo server */
    if (connect(sock, (struct sockaddr *) &echoServAddr, sizeof(echoServAddr)) < 0)
    {
        // note: the socket currently blocks, which in many cases will prevent us from ever notifying the user here
        statusLabel.text = @"Not connected";
        UIAlertView *alertView = [[UIAlertView alloc]
                                  initWithTitle:@"Connection Failure" 
                                  message:[NSString stringWithFormat:@"Failed to connect to server at %s",servIP]
                                  delegate:self cancelButtonTitle:nil
                                  otherButtonTitles:@"Ok", nil];
        [alertView show];
        
    }
    else {
        started = YES;
        statusLabel.text = @"Connected";
        splashView.hidden = YES;
        [self startAnimation];
    }
    //configureView.hidden = YES;
    [UIView beginAnimations:nil context:nil];
    configureView.center = CGPointMake(160,-50);
    configureButton.alpha = 1.0;
    [UIView commitAnimations];
  
}


- (void)dealloc {
    
    [self stopAnimation];
    
    if ([EAGLContext currentContext] == context) {
        [EAGLContext setCurrentContext:nil];
    }
    
    [context release];  
    [super dealloc];
}


// text field delegate implementation
- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
    [self onGo];
    return YES;
}
// end text field delegate implementation


@end
