---
source: https://customtkinter.tomschimansky.com/documentation/widgets/combobox
extracted: 2026-01-20 10:43:37
---

On this page

# CTkComboBox

### Example Code[​](#example-code "Direct link to Example Code")

Without variable:
    
    
    def combobox_callback(choice):  
        print("combobox dropdown clicked:", choice)  
      
    combobox = customtkinter.CTkComboBox(app, values=["option 1", "option 2"],  
                                         command=combobox_callback)  
    combobox.set("option 2")  
    

With variable:
    
    
    def combobox_callback(choice):  
        print("combobox dropdown clicked:", choice)  
      
    combobox_var = customtkinter.StringVar(value="option 2")  
    combobox = customtkinter.CTkComboBox(app, values=["option 1", "option 2"],  
                                         command=combobox_callback, variable=combobox_var)  
    combobox_var.set("option 2")  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, frame, top-level  
width| box width in px  
height| box height in px  
corner_radius| corner radius in px  
border_width| border width in px  
fg_color| foreground (inside) color, tuple: (light_color, dark_color) or single color  
border_color| border color, tuple: (light_color, dark_color) or single color  
button_color| right button color, tuple: (light_color, dark_color) or single color  
button_hover_color| hover color, tuple: (light_color, dark_color) or single color  
dropdown_fg_color| dropdown fg color, tuple: (light_color, dark_color) or single color  
dropdown_hover_color| dropdown button hover color, tuple: (light_color, dark_color) or single color  
dropdown_text_color| dropdown text color, tuple: (light_color, dark_color) or single color  
text_color| text color, tuple: (light_color, dark_color) or single color  
text_color_disabled| text color when disabled, tuple: (light_color, dark_color) or single color  
font| button text font, tuple: (font_name, size)  
dropdown_font| button text font, tuple: (font_name, size)  
values| list of strings with values that appear in the dropdown menu  
hover| enable/disable hover effect: True, False  
state| "normal" (standard), "disabled" (not clickable, darker color), "readonly"  
command| function will be called when the dropdown is clicked manually  
variable| StringVar to control or get the current text  
justify| "right", "left", "center", orientation of the text inside the entry, default is "left"  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured, for example:
        
        combobox.configure(values=["new value 1", "new value 2"])  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute, for example.
        
        state = combobox.cget("state")  
        

  * #### .set(value)[​](#setvalue "Direct link to .set\(value\)")

Set combobox to specific string value. Value don't has to be part of the values list.

  * #### .get()[​](#get "Direct link to .get\(\)")

Get current string value of combobox entry.