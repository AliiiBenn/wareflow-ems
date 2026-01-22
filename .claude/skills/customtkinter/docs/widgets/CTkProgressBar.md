---
source: https://customtkinter.tomschimansky.com/documentation/widgets/progressbar
extracted: 2026-01-20 10:43:51
---

On this page

# CTkProgressBar

### Example Code[​](#example-code "Direct link to Example Code")
    
    
    progressbar = customtkinter.CTkProgressBar(app, orientation="horizontal")  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, tkinter.Frame or CTkFrame  
width| slider width in px  
height| slider height in px  
border_width| border width in px  
corner_radius| corner_radius in px  
fg_color| foreground color, tuple: (light_color, dark_color) or single color  
border_color| slider border color, tuple: (light_color, dark_color) or single color  
progress_color| progress color, tuple: (light_color, dark_color) or single color  
orientation| "horizontal" (default) or "vertical"  
mode| "determinate" for linear progress (default), "indeterminate" for unknown progress  
determinate_speed| speed for automatic progress in determinate mode started by .start(), default is 1  
indeterminate_speed| speed for automatic progress in indeterminate mode started by .start(), default is 1  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured and updated, for example:
        
        progressbar.configure(mode="indeterminate")  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute, for example.
        
        mode = progressbar.cget("mode")  
        

  * #### .set(value)[​](#setvalue "Direct link to .set\(value\)")

Set progress bar to specific value (range 0 to 1).

  * #### .get()[​](#get "Direct link to .get\(\)")

Get current value of progress bar.
        
        value = ctk_progressbar.get()  
        

  * #### .start()[​](#start "Direct link to .start\(\)")

Start automatic progress. Speed is set by `indeterminate_speed` and `determinate_speed` attributes, default is 1. If mode is set to "indeterminate", the progress bar will oscillate, otherwise it will fill up and then repeat.

  * #### .stop()[​](#stop "Direct link to .stop\(\)")

Stop automatic progress.

  * #### .step()[​](#step "Direct link to .step\(\)")

Do single step manually otherwise done by .start() and .stop() automatic loop. Step size is set by determinate_speed and indeterminate_speed attributes.