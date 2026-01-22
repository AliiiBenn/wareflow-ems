---
source: https://customtkinter.tomschimansky.com/documentation/scaling/
extracted: 2026-01-20 10:43:27
---

On this page

# Scaling

### HighDPI support[​](#highdpi-support "Direct link to HighDPI support")

CustomTkinter supports HighDPI scaling on macOS and Windows by default. On macOS scaling works automatically for Tk windows. On Windows, the app is made DPI aware (`windll.shcore.SetProcessDpiAwareness(2)`) and the current scaling factor of the display is detected. Then every element and the window dimensions are scaled by this factor by CustomTkinter.

![Windows 10 scaling settings example](/assets/images/windows_scaling-f0d9cdb1afc7397dd8e7d2dfccd2a34b.png)

You can deactivate this automatic scaling like this:
    
    
    customtkinter.deactivate_automatic_dpi_awareness()  
    

Then the window will be blurry on Windows with a scaling value of more than 100%.

### Custom scaling[​](#custom-scaling "Direct link to Custom scaling")

In addition to the automatically detected scaling factor, you can also set your own scaling factors for the application like the following:
    
    
    customtkinter.set_widget_scaling(float_value)  # widget dimensions and text size  
    customtkinter.set_window_scaling(float_value)  # window geometry dimensions