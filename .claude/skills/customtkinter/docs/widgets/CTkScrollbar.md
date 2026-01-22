---
source: https://customtkinter.tomschimansky.com/documentation/widgets/scrollbar
extracted: 2026-01-20 10:43:59
---

On this page

# CTkScrollbar

### Example Code[​](#example-code "Direct link to Example Code")

Create a CTkTextbox with external scrollbar:
    
    
    app = customtkinter.CTk()  
    app.grid_rowconfigure(0, weight=1)  
    app.grid_columnconfigure(0, weight=1)  
      
    # create scrollable textbox  
    tk_textbox = customtkinter.CTkTextbox(app, activate_scrollbars=False)  
    tk_textbox.grid(row=0, column=0, sticky="nsew")  
      
    # create CTk scrollbar  
    ctk_textbox_scrollbar = customtkinter.CTkScrollbar(app, command=tk_textbox.yview)  
    ctk_textbox_scrollbar.grid(row=0, column=1, sticky="ns")  
      
    # connect textbox scroll event to CTk scrollbar  
    tk_textbox.configure(yscrollcommand=ctk_textbox_scrollbar.set)  
      
    app.mainloop()  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, tkinter.Frame or CTkFrame  
command| function of scrollable widget to call when scrollbar is moved  
width| button width in px  
height| button height in px  
corner_radius| corner radius in px  
border_spacing| foreground space around the scrollbar in px (border)  
fg_color| forground color, tuple: (light_color, dark_color) or single color or "transparent"  
button_color| scrollbar color, tuple: (light_color, dark_color) or single color  
button_hover_color| scrollbar hover color, tuple: (light_color, dark_color) or single color  
minimum_pixel_length| minimum length of scrollbar in px  
orientation| "vertical" (standard), "horizontal"  
hover| hover effect (True/False)  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured.

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute. 

  * #### .get()[​](#get "Direct link to .get\(\)")

Get current start and end value.

  * #### .set(start_value, end_value)[​](#setstart_value-end_value "Direct link to .set\(start_value, end_value\)")

Set start and end value.