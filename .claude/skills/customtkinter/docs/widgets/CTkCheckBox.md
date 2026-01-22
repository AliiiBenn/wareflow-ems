---
source: https://customtkinter.tomschimansky.com/documentation/widgets/checkbox
extracted: 2026-01-20 10:43:35
---

On this page

# CTkCheckBox

### Example Code[​](#example-code "Direct link to Example Code")
    
    
    def checkbox_event():  
        print("checkbox toggled, current value:", check_var.get())  
      
    check_var = customtkinter.StringVar(value="on")  
    checkbox = customtkinter.CTkCheckBox(app, text="CTkCheckBox", command=checkbox_event,  
                                         variable=check_var, onvalue="on", offvalue="off")  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, tkinter.Frame or CTkFrame  
width| width of complete widget in px  
height| height of complete widget in px  
checkbox_width| width of checkbox in px  
checkbox_height| height of checkbox in px  
corner_radius| corner radius in px  
border_width| box border width in px  
fg_color| foreground (inside) color, tuple: (light_color, dark_color) or single color  
border_color| border color, tuple: (light_color, dark_color) or single color  
hover_color| hover color, tuple: (light_color, dark_color) or single color  
text_color| text color, tuple: (light_color, dark_color) or single color  
text_color_disabled| text color when disabled, tuple: (light_color, dark_color) or single color  
text| string  
textvariable| Tkinter StringVar to control the text  
font| button text font, tuple: (font_name, size)  
hover| enable/disable hover effect: True, False  
state| tkinter.NORMAL (standard) or tkinter.DISABLED (not clickable, darker color)  
command| function will be called when the checkbox is clicked  
variable| Tkinter variable to control or read checkbox state  
onvalue| string or int for variable in checked state  
offvalue| string or int for variable in unchecked state  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured, for example
        
        checkbox.configure(state="disabled")  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute, for example.
        
        text = checkbox.cget("text")  
        

  * #### .get()[​](#get "Direct link to .get\(\)")

Get current value, 1 or 0 (checked or not checked).

  * #### .select()[​](#select "Direct link to .select\(\)")

Turn on checkbox (set value to 1), command will not be triggered.

  * #### .deselect()[​](#deselect "Direct link to .deselect\(\)")

Turn off checkbox (set value to 0), command will not be triggered.

  * #### .toggle()[​](#toggle "Direct link to .toggle\(\)")

Flip current value, command will be triggered.