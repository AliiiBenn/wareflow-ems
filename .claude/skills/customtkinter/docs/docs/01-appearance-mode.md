---
source: https://customtkinter.tomschimansky.com/documentation/appearancemode
extracted: 2026-01-20 10:43:21
---

# Appearance Mode

The appearance mode decides, which color will be picked from tuple colors, if the color is specified as a tuple color. You can set the appearance mode at any time with the following command:
    
    
    customtkinter.set_appearance_mode("system")  # default  
    customtkinter.set_appearance_mode("dark")  
    customtkinter.set_appearance_mode("light")  
    

If you set the appearance mode to `"system"`, the current mode is read from the operating system. It will also adapt if the appearance mode of the operating system changes during the runtime of the program. Note that on Linux it will be always in `"light"` mode if set to `"system"`, because the mode can't get read from the operating system at the moment, this will probably be implemented in the future.