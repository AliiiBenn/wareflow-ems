---
source: https://customtkinter.tomschimansky.com/documentation/widgets/slider
extracted: 2026-01-20 10:44:04
---

On this page

# CTkSlider

### Example Code[​](#example-code "Direct link to Example Code")
    
    
    def slider_event(value):  
        print(value)  
      
    slider = customtkinter.CTkSlider(app, from_=0, to=100, command=slider_event)  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, tkinter.Frame or CTkFrame  
command| callback function, receives slider value as argument  
variable| tkinter.IntVar or tkinter.DoubleVar object  
width| slider width in px  
height| slider height in px  
border_width| space around the slider rail in px  
from_| lower slider value  
to| upper slider value  
number_of_steps| number of steps in which the slider can be positioned  
fg_color| foreground color, tuple: (light_color, dark_color) or single color  
progress_color| tuple: (light_color, dark_color) or single color or "transparent", color of the slider line before the button  
border_color| slider border color, tuple: (light_color, dark_color) or single color or "transparent", default is "transparent"  
button_color| color of the slider button, tuple: (light_color, dark_color) or single color  
button_hover_color| hover color, tuple: (light_color, dark_color) or single color  
orientation| "horizontal" (standard) or "vertical"  
state| "normal" or "disabled" (not clickable)  
hover| bool, enable/disable hover effect, default is True  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured and updated, for example:
        
        slider.configure(number_of_steps=25)  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute. 

  * #### .set(value)[​](#setvalue "Direct link to .set\(value\)")

Set slider to specific value.

  * #### .get()[​](#get "Direct link to .get\(\)")

Get current value of slider.
        
        value = slider.get()