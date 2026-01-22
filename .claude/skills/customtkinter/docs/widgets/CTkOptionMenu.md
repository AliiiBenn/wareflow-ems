---
source: https://customtkinter.tomschimansky.com/documentation/widgets/optionmenu
extracted: 2026-01-20 10:43:48
---

On this page

# CTkOptionMenu

### Example Code[​](#example-code "Direct link to Example Code")

Without variable:
    
    
    def optionmenu_callback(choice):  
        print("optionmenu dropdown clicked:", choice)  
      
    optionmenu = customtkinter.CTkOptionMenu(app, values=["option 1", "option 2"],  
                                             command=optionmenu_callback)  
    optionmenu.set("option 2")  
    

With variable:
    
    
    def optionmenu_callback(choice):  
        print("optionmenu dropdown clicked:", choice)  
      
    optionmenu_var = customtkinter.StringVar(value="option 2")  
    optionmenu = customtkinter.CTkOptionMenu(app,values=["option 1", "option 2"],  
                                             command=optionmenu_callback,  
                                             variable=optionmenu_var)  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, frame, top-level  
width| box width in px  
height| box height in px  
corner_radius| corner radius in px  
fg_color| foreground (inside) color, tuple: (light_color, dark_color) or single color  
button_color| right button color, tuple: (light_color, dark_color) or single color  
button_hover_color| hover color, tuple: (light_color, dark_color) or single color  
dropdown_fg_color| dropdown fg color, tuple: (light_color, dark_color) or single color  
dropdown_hover_color| dropdown button hover color, tuple: (light_color, dark_color) or single color  
dropdown_text_color| dropdown text color, tuple: (light_color, dark_color) or single color  
text_color| text color, tuple: (light_color, dark_color) or single color  
text_color_disabled| text color when disabled, tuple: (light_color, dark_color) or single color  
font| button text font, tuple: (font_name, size)  
dropdown_font| button text font, tuple: (font_name, size)  
hover| enable/disable hover effect: True, False  
state| "normal" (standard) or "disabled" (not clickable, darker color)  
command| function will be called when the dropdown is clicked manually  
variable| StringVar to control or get the current text  
values| list of strings with values that appear in the option menu dropdown  
dynamic_resizing| enable/disable automatic resizing of optionmenu when text is too big to fit: True (standard), False  
anchor| "n", "s", "e", "w", "center", orientation of the text inside the optionmenu, default is "w"  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured and updated.
        
        optionmenu.configure(values=["new value 1", "new value 2"])  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute, for example.
        
        state = optionmenu.cget("state")  
        

  * #### .set(value)[​](#setvalue "Direct link to .set\(value\)")

Set optionmenu to specific string value. Value don't has to be part of the values list.

  * #### .get()[​](#get "Direct link to .get\(\)")

Get current string value of optionmenu.