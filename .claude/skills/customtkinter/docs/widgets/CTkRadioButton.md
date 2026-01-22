---
source: https://customtkinter.tomschimansky.com/documentation/widgets/radiobutton
extracted: 2026-01-20 10:43:54
---

On this page

# CTkRadioButton

### Example Code[​](#example-code "Direct link to Example Code")
    
    
    def radiobutton_event():  
        print("radiobutton toggled, current value:", radio_var.get())  
      
    radio_var = tkinter.IntVar(value=0)  
    radiobutton_1 = customtkinter.CTkRadioButton(app, text="CTkRadioButton 1",  
                                                 command=radiobutton_event, variable= radio_var, value=1)  
    radiobutton_2 = customtkinter.CTkRadioButton(app, text="CTkRadioButton 2",  
                                                 command=radiobutton_event, variable= radio_var, value=2)  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, tkinter.Frame or CTkFrame  
width| width of complete widget in px  
height| height of complete widget in px  
radiobutton_width| width of radiobutton in px  
radiobutton_height| height of radiobutton in px  
corner_radius| corner radius in px  
border_width_unchecked| border width in unchecked state in px  
border_width_checked| border width in checked state in px  
fg_color| foreground (inside) color, tuple: (light_color, dark_color) or single color  
border_color| border color, tuple: (light_color, dark_color) or single color  
hover_color| hover color, tuple: (light_color, dark_color) or single color  
text_color| text color, tuple: (light_color, dark_color) or single color  
text_color_disabled| text color when disabled, tuple: (light_color, dark_color) or single color  
text| string  
textvariable| Tkinter StringVar to control the text  
font| button text font, tuple: (font_name, size)  
hover| enable/disable hover effect: True, False  
state| "normal" (standard) or "disabled" (not clickable, darker color)  
command| function will be called when the checkbox is clicked  
variable| Tkinter variable to control or read checkbox state  
value| string or int value for variable when RadioButton is clicked  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured and updated.
        
        radiobutton.configure(state="disabled")  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute, for example.
        
        state = radiobutton.cget("state")  
        

  * #### .select()[​](#select "Direct link to .select\(\)")

Select radio button (set value to 1), command will not be triggered.

  * #### .deselect()[​](#deselect "Direct link to .deselect\(\)")

Deselect radio button (set value to 0), command will not be triggered.

  * #### .invoke()[​](#invoke "Direct link to .invoke\(\)")

Same action as if user would click the radio button, command will be triggered.