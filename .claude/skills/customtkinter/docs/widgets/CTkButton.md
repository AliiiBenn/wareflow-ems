---
source: https://customtkinter.tomschimansky.com/documentation/widgets/button
extracted: 2026-01-20 10:43:32
---

On this page

# CTkButton

Available since version 0.3.0. 

### Example Code[​](#example-code "Direct link to Example Code")
    
    
    def button_event():  
        print("button pressed")  
      
    button = customtkinter.CTkButton(app, text="CTkButton", command=button_event)  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, tkinter.Frame or CTkFrame  
width| button width in px  
height| button height in px  
corner_radius| corner radius in px  
border_width| button border width in px  
border_spacing| spacing between text and image and button border in px, default is 2  
fg_color| forground color, tuple: (light_color, dark_color) or single color or "transparent"  
hover_color| hover color, tuple: (light_color, dark_color) or single color  
border_color| border color, tuple: (light_color, dark_color) or single color  
text_color| text color, tuple: (light_color, dark_color) or single color  
text_color_disabled| text color when disabled, tuple: (light_color, dark_color) or single color  
text| string  
font| button text font, tuple: (font_name, size), (set negative size value for size in pixels)  
textvariable| tkinter.StringVar object to change text of button  
image| put an image on the button, removes the text, must be class PhotoImage  
state| "normal" (standard) or "disabled" (not clickable, darker color)  
hover| enable/disable hover effect: True, False  
command| callback function  
compound| set image orientation if image and text are given ("top", "left", "bottom", "right")  
anchor| alignment of text an image in button ("n", "ne", "e", "se", "s", "sw", "w", "nw", "center")  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured, for example:
        
        button.configure(text="new text")  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute, for example.
        
        text = button.cget("text")  
        

  * #### .invoke()[​](#invoke "Direct link to .invoke\(\)")

Calls command if button state is 'disabled'.