let StickStatus =
{
    xPosition: 0,
    yPosition: 0,
    x: 0,
    y: 0,
    cardinalDirection: "C"
};

/**
 * @desc Principal object that draw a joystick, you only need to initialize the object and suggest the HTML container
 * @costructor
 * @param container {String} - HTML object that contains the Joystick
 * @param parameters (optional) - object with following keys:
 *  title {String} (optional) - The ID of canvas (Default value is 'joystick')
 *  width {Int} (optional) - The width of canvas, if not specified is setted at width of container object (Default value is the width of container object)
 *  height {Int} (optional) - The height of canvas, if not specified is setted at height of container object (Default value is the height of container object)
 *  internalFillColor {String} (optional) - Internal color of Stick (Default value is '#00AA00')
 *  internalLineWidth {Int} (optional) - Border width of Stick (Default value is 2)
 *  internalStrokeColor {String}(optional) - Border color of Stick (Default value is '#003300')
 *  externalLineWidth {Int} (optional) - External reference circonference width (Default value is 2)
 *  externalStrokeColor {String} (optional) - External reference circonference color (Default value is '#008000')
 *  autoReturnToCenter {Bool} (optional) - Sets the behavior of the stick, whether or not, it should return to zero position when released (Default value is True and return to zero)
 * @param callback {StickStatus} - 
 */
var JoyStick = (function(container, parameters, callback)
{
    parameters = parameters || {};
    var title = (typeof parameters.title === "undefined" ? "joystick" : parameters.title),
        width = (typeof parameters.width === "undefined" ? 0 : parameters.width),
        height = (typeof parameters.height === "undefined" ? 0 : parameters.height),
        internalFillColor = (typeof parameters.internalFillColor === "undefined" ? "#00AA00" : parameters.internalFillColor),
        internalLineWidth = (typeof parameters.internalLineWidth === "undefined" ? 2 : parameters.internalLineWidth),
        internalStrokeColor = (typeof parameters.internalStrokeColor === "undefined" ? "#003300" : parameters.internalStrokeColor),
        externalLineWidth = (typeof parameters.externalLineWidth === "undefined" ? 2 : parameters.externalLineWidth),
        externalStrokeColor = (typeof parameters.externalStrokeColor ===  "undefined" ? "#008000" : parameters.externalStrokeColor),
        autoReturnToCenter = (typeof parameters.autoReturnToCenter === "undefined" ? true : parameters.autoReturnToCenter);

    callback = callback || function(StickStatus) {};

    // Create Canvas element and add it in the Container object
    var objContainer = document.getElementById(container);
    
    // Fixing Unable to preventDefault inside passive event listener due to target being treated as passive in Chrome [Thanks to https://github.com/artisticfox8 for this suggestion]
    objContainer.style.touchAction = "none";

    var canvas = document.createElement("canvas");
    canvas.id = title;
    if(width === 0) { width = objContainer.clientWidth; }
    if(height === 0) { height = objContainer.clientHeight; }
    canvas.width = width;
    canvas.height = height;
    objContainer.appendChild(canvas);
    var context=canvas.getContext("2d");

    var pressed = 0; // Bool - 1=Yes - 0=No
    var circumference = 2 * Math.PI;
    var internalRadius = (canvas.width-((canvas.width/2)+10))/2;
    var maxMoveStick = internalRadius + 5;
    var externalRadius = internalRadius + 30;
    var centerX = canvas.width / 2;
    var centerY = canvas.height / 2;
    var directionHorizontalLimitPos = canvas.width / 10;
    var directionHorizontalLimitNeg = directionHorizontalLimitPos * -1;
    var directionVerticalLimitPos = canvas.height / 10;
    var directionVerticalLimitNeg = directionVerticalLimitPos * -1;
    // Used to save current position of stick
    var movedX=centerX;
    var movedY=centerY;

    // Check if the device support the touch or not
    if("ontouchstart" in document.documentElement)
    {
        canvas.addEventListener("touchstart", onTouchStart, false);
        document.addEventListener("touchmove", onTouchMove, false);
        document.addEventListener("touchend", onTouchEnd, false);
    }
    else
    {
        canvas.addEventListener("mousedown", onMouseDown, false);
        document.addEventListener("mousemove", onMouseMove, false);
        document.addEventListener("mouseup", onMouseUp, false);
    }
    // Draw the object
    drawExternal();
    drawInternal();

    /******************************************************
     * Private methods
     *****************************************************/

    /**
     * @desc Draw the external circle used as reference position
     */
    function drawExternal()
    {
        context.beginPath();
        context.arc(centerX, centerY, externalRadius, 0, circumference, false);
        context.lineWidth = externalLineWidth;
        context.strokeStyle = externalStrokeColor;
        context.stroke();
    }

    /**
     * @desc Draw the internal stick in the current position the user have moved it
     */
    function drawInternal()
    {
        context.beginPath();
        if(movedX<internalRadius) { movedX=maxMoveStick; }
        if((movedX+internalRadius) > canvas.width) { movedX = canvas.width-(maxMoveStick); }
        if(movedY<internalRadius) { movedY=maxMoveStick; }
        if((movedY+internalRadius) > canvas.height) { movedY = canvas.height-(maxMoveStick); }
        context.arc(movedX, movedY, internalRadius, 0, circumference, false);
        // create radial gradient
        var grd = context.createRadialGradient(centerX, centerY, 5, centerX, centerY, 200);
        // Light color
        grd.addColorStop(0, internalFillColor);
        // Dark color
        grd.addColorStop(1, internalStrokeColor);
        context.fillStyle = grd;
        context.fill();
        context.lineWidth = internalLineWidth;
        context.strokeStyle = internalStrokeColor;
        context.stroke();
    }

    /**
     * @desc Events for manage touch
     */
    function onTouchStart(event) 
    {
        pressed = 1;
    }

    function onTouchMove(event)
    {
        if(pressed === 1 && event.targetTouches[0].target === canvas)
        {
            movedX = event.targetTouches[0].pageX;
            movedY = event.targetTouches[0].pageY;
            // Manage offset
            if(canvas.offsetParent.tagName.toUpperCase() === "BODY")
            {
                movedX -= canvas.offsetLeft;
                movedY -= canvas.offsetTop;
            }
            else
            {
                movedX -= canvas.offsetParent.offsetLeft;
                movedY -= canvas.offsetParent.offsetTop;
            }
            // Delete canvas
            context.clearRect(0, 0, canvas.width, canvas.height);
            // Redraw object
            drawExternal();
            drawInternal();

            // Set attribute of callback
            StickStatus.xPosition = movedX;
            StickStatus.yPosition = movedY;
            StickStatus.x = (100*((movedX - centerX)/maxMoveStick)).toFixed();
            StickStatus.y = ((100*((movedY - centerY)/maxMoveStick))*-1).toFixed();
            StickStatus.cardinalDirection = getCardinalDirection();
            callback(StickStatus);
        }
    } 

    function onTouchEnd(event) 
    {
        pressed = 0;
        // If required reset position store variable
        if(autoReturnToCenter)
        {
            movedX = centerX;
            movedY = centerY;
        }
        // Delete canvas
        context.clearRect(0, 0, canvas.width, canvas.height);
        // Redraw object
        drawExternal();
        drawInternal();

        // Set attribute of callback
        StickStatus.xPosition = movedX;
        StickStatus.yPosition = movedY;
        StickStatus.x = (100*((movedX - centerX)/maxMoveStick)).toFixed();
        StickStatus.y = ((100*((movedY - centerY)/maxMoveStick))*-1).toFixed();
        StickStatus.cardinalDirection = getCardinalDirection();
        callback(StickStatus);
    }

    /**
     * @desc Events for manage mouse
     */
    function onMouseDown(event) 
    {
        pressed = 1;
    }

    function onMouseMove(event) 
    {
        if(pressed === 1)
        {
            movedX = event.pageX;
            movedY = event.pageY;
            // Manage offset
            if(canvas.offsetParent.tagName.toUpperCase() === "BODY")
            {
                movedX -= canvas.offsetLeft;
                movedY -= canvas.offsetTop;
            }
            else
            {
                movedX -= canvas.offsetParent.offsetLeft;
                movedY -= canvas.offsetParent.offsetTop;
            }
            // Delete canvas
            context.clearRect(0, 0, canvas.width, canvas.height);
            // Redraw object
            drawExternal();
            drawInternal();

            // Set attribute of callback
            StickStatus.xPosition = movedX;
            StickStatus.yPosition = movedY;
            StickStatus.x = (100*((movedX - centerX)/maxMoveStick)).toFixed();
            StickStatus.y = ((100*((movedY - centerY)/maxMoveStick))*-1).toFixed();
            StickStatus.cardinalDirection = getCardinalDirection();
            callback(StickStatus);
        }
    }

    function onMouseUp(event) 
    {
        pressed = 0;
        // If required reset position store variable
        if(autoReturnToCenter)
        {
            movedX = centerX;
            movedY = centerY;
        }
        // Delete canvas
        context.clearRect(0, 0, canvas.width, canvas.height);
        // Redraw object
        drawExternal();
        drawInternal();

        // Set attribute of callback
        StickStatus.xPosition = movedX;
        StickStatus.yPosition = movedY;
        StickStatus.x = (100*((movedX - centerX)/maxMoveStick)).toFixed();
        StickStatus.y = ((100*((movedY - centerY)/maxMoveStick))*-1).toFixed();
        StickStatus.cardinalDirection = getCardinalDirection();
        callback(StickStatus);
    }

    function getCardinalDirection()
    {
        let result = "";
        let orizontal = movedX - centerX;
        let vertical = movedY - centerY;
        
        if(vertical >= directionVerticalLimitNeg && vertical <= directionVerticalLimitPos)
        {
            result = "C";
        }
        if(vertical < directionVerticalLimitNeg)
        {
            result = "N";
        }
        if(vertical > directionVerticalLimitPos)
        {
            result = "S";
        }
        
        if(orizontal < directionHorizontalLimitNeg)
        {
            if(result === "C")
            { 
                result = "W";
            }
            else
            {
                result += "W";
            }
        }
        if(orizontal > directionHorizontalLimitPos)
        {
            if(result === "C")
            { 
                result = "E";
            }
            else
            {
                result += "E";
            }
        }
        
        return result;
    }

    // let controllerIndex = null;

    // window.addEventListener("gamepadconnected", (event) => {
    // handleConnectDisconnect(event, true);
    // });

    // window.addEventListener("gamepaddisconnected", (event) => {
    // handleConnectDisconnect(event, false);
    // });

    // function handleConnectDisconnect(event, connected) {
    // const controllerAreaNotConnected = document.getElementById(
    //     "controller-not-connected-area"
    // );
    // const controllerAreaConnected = document.getElementById(
    //     "controller-connected-area"
    // );

    // const gamepad = event.gamepad;
    // console.log(gamepad);

    // if (connected) {
    //     controllerIndex = gamepad.index;
    //     controllerAreaNotConnected.style.display = "none";
    //     controllerAreaConnected.style.display = "block";
    //     createButtonLayout(gamepad.buttons);
    //     createAxesLayout(gamepad.axes);
    // } else {
    //     controllerIndex = null;
    //     controllerAreaNotConnected.style.display = "block";
    //     controllerAreaConnected.style.display = "none";
    // }
    // }

    // function createAxesLayout(axes) {
    //     const buttonsArea = document.getElementById("buttons");
    //     for (let i = 0; i < axes.length; i++) {
    //         buttonsArea.innerHTML += `<div id=axis-${i} class='axis'>
    //                                     <div class='axis-name'>AXIS ${i}</div>
    //                                     <div class='axis-value'>${axes[i].toFixed(
    //                                         4
    //                                     )}</div>
    //                                 </div> `;
    //     }
    // }

    // function createButtonLayout(buttons) {
    //     const buttonArea = document.getElementById("buttons");
    //     buttonArea.innerHTML = "";
    //     for (let i = 0; i < buttons.length; i++) {
    //     buttonArea.innerHTML += createButtonHtml(i, 0);
    //     }
    // }
    
    // function createButtonHtml(index, value) {
    //     return `<div class="button" id="button-${index}">
    //                 <svg width="10px" height="50px">
    //                     <rect width="10px" height="50px" fill="grey"></rect>
    //                     <rect
    //                         class="button-meter"
    //                         width="10px"
    //                         x="0"
    //                         y="50"
    //                         data-original-y-position="50"
    //                         height="50px"
    //                         fill="rgb(60, 61, 60)"
    //                     ></rect>
    //                 </svg>
    //                 <div class='button-text-area'>
    //                     <div class="button-name">B${index}</div>
    //                     <div class="button-value">${value.toFixed(2)}</div>
    //                 </div>
    //             </div>`;
    // }

    // function updateButtonOnGrid(index, value) {
    //     const buttonArea = document.getElementById(`button-${index}`);
    //     const buttonValue = buttonArea.querySelector(".button-value");
    //     buttonValue.innerHTML = value.toFixed(2);
    
    //     const buttonMeter = buttonArea.querySelector(".button-meter");
    //     const meterHeight = Number(buttonMeter.dataset.originalYPosition);
    //     const meterPosition = meterHeight - (meterHeight / 100) * (value * 100);
    //     buttonMeter.setAttribute("y", meterPosition);
    // }
    
    // function updateControllerButton(index, value) {
    //     const button = document.getElementById(`controller-b${index}`);
    //     const selectedButtonClass = "selected-button";
    //     1;
    //     if (button) {
    //         if (value > 0) {
    //         button.classList.add(selectedButtonClass);
    //         button.style.filter = `contrast(${value * 200}%)`;
    //         } else {
    //         button.classList.remove(selectedButtonClass);
    //         button.style.filter = `contrast(100%)`;
    //         }
    //     }
    // }

    // function handleButtons(buttons) {
    //     for (let i = 0; i < buttons.length; i++) {
    //         const buttonValue = buttons[i].value;
    //         updateButtonOnGrid(i, buttonValue);
    //         updateControllerButton(i, buttonValue);
    //     }
    // }

    // function handleSticks(axes) {
    //     updateAxesGrid(axes);
    //     updateStick("controller-b10", axes[0], axes[1]);
    //     updateStick("controller-b11", axes[2], axes[3]);
    // }

    // function updateAxesGrid(axes) {
    //     for (let i = 0; i < axes.length; i++) {
    //         const axis = document.querySelector(`#axis-${i} .axis-value`);
    //         const value = axes[i];
    //         // if (value > 0.06 || value < -0.06) {
    //         axis.innerHTML = value.toFixed(4);
    //         // }
    //     }
    // }

    // function updateStick(elementId, leftRightAxis, upDownAxis) {
    //     const multiplier = 25;
    //     const stickLeftRight = leftRightAxis * multiplier;
    //     const stickUpDown = upDownAxis * multiplier;

    //     const stick = document.getElementById(elementId);
    //     const x = Number(stick.dataset.originalXPosition);
    //     const y = Number(stick.dataset.originalYPosition);

    //     stick.setAttribute("cx", x + stickLeftRight);
    //     stick.setAttribute("cy", y + stickUpDown);

    // }

    // function handleRumble(gamepad) {
    //     const rumbleOnButtonPress = document.getElementById("rumble-on-button-press");

    //     if (rumbleOnButtonPress.checked) {
    //         if (gamepad.buttons.some((button) => button.value > 0)) {
    //         gamepad.vibrationActuator.playEffect("dual-rumble", {
    //             startDelay: 0,
    //             duration: 25,
    //             weakMagnitude: 1.0,
    //             strongMagnitude: 1.0,
    //         });
    //         }
    //     }
    // }

    // // function controllerInput() {
    // //     if (controllerIndex !== null){
    // //         const gamepad = navigator.getGamepads()[controllerIndex];
            
    // //         const buggy_left_right = gamepad.axes[0];
    // //         sendDataToServerNewLeftLeftRight();
    // //         const buggy_up_down = gamepad.axes[1];
    // //         sendDataToServerNewLeftUpDown();
    // //         const camera_left_right = gamepad.axes[2];
    // //         sendDataToServerNewRightLeftRight();
    // //         const camera_up_down = gamepad.axes[3];
    // //         sendDataToServerNewRightUpDown();

    // //     }
    // // }

    // function gameLoop() {
    //     if (controllerIndex !== null) {
    //         const gamepad = navigator.getGamepads()[controllerIndex];
    //         handleButtons(gamepad.buttons);
    //         handleSticks(gamepad.axes);
    //         handleRumble(gamepad);
    //         // controllerInput();
            
    //         const buggy_left_right = gamepad.axes[0];
    //         // sendDataToServerNewLeftLeftRight();
    //         const buggy_up_down = gamepad.axes[1];
    //         // sendDataToServerNewLeftUpDown();
    //         const camera_left_right = gamepad.axes[2];
    //         // sendDataToServerNewRightLeftRight();
    //         const camera_up_down = gamepad.axes[3];
    //         // sendDataToServerNewRightUpDown();
    //         // console.log("buggy left right: ", buggy_left_right);

    //         console.log(buggy_left_right);
    //         console.log(buggy_up_down);
    //         console.log(camera_left_right);
    //         console.log(camera_up_down);
                

    //     }
    //     requestAnimationFrame(gameLoop);
    // }

    // // setTimeout(gameLoop(),2000);
    // window.requestAnimationFrame(gameLoop)


    /******************************************************
     * Public methods
     *****************************************************/

    /**
     * @desc The width of canvas
     * @return Number of pixel width 
     */
    this.GetWidth = function () 
    {
        return canvas.width;
    };

    /**
     * @desc The height of canvas
     * @return Number of pixel height
     */
    this.GetHeight = function () 
    {
        return canvas.height;
    };

    /**
     * @desc The X position of the cursor relative to the canvas that contains it and to its dimensions
     * @return Number that indicate relative position
     */
    this.GetPosX = function ()
    {
        return movedX;
    };

    /**
     * @desc The Y position of the cursor relative to the canvas that contains it and to its dimensions
     * @return Number that indicate relative position
     */
    this.GetPosY = function ()
    {
        return movedY;
    };

    /**
     * @desc Normalizzed value of X move of stick
     * @return Integer from -100 to +100
     */
    this.GetX = function ()
    {
        return (100*((movedX - centerX)/maxMoveStick)).toFixed();
    };

    /**
     * @desc Normalizzed value of Y move of stick
     * @return Integer from -100 to +100
     */
    this.GetY = function ()
    {
        return ((100*((movedY - centerY)/maxMoveStick))*-1).toFixed();
    };

    /**
     * @desc Get the direction of the cursor as a string that indicates the cardinal points where this is oriented
     * @return String of cardinal point N, NE, E, SE, S, SW, W, NW and C when it is placed in the center
     */
    this.GetDir = function()
    {
        return getCardinalDirection();
    };
});
  
