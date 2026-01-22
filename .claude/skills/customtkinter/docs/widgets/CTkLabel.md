---
source: https://customtkinter.tomschimansky.com/documentation/widgets/label
extracted: 2026-01-20 10:43:46
---

On this page

# CTkLabel

### Example Code[​](#example-code "Direct link to Example Code")
    
    
    label = customtkinter.CTkLabel(app, text="CTkLabel", fg_color="transparent")  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, tkinter.Frame or CTkFrame  
textvariable| tkinter.StringVar object  
text| string  
width| label width in px  
height| label height in px  
corner_radius| corner radius in px  
fg_color| foreground color, tuple: (light_color, dark_color) or single color or "transparent"  
text_color| label text color, tuple: (light_color, dark_color) or single color  
font| label text font, tuple: (font_name, size)  
anchor| controls where the text is positioned if the widget has more space than the text needs, default is "center"  
compound| control the postion of image relative to text, default is "center, other are: "top", "bottom", "left", "right"  
justify| specifies how multiple lines of text will be aligned with respect to each other: "left" for flush left, "center" for centered (the default), or "right" for right-justified  
padx| extra space added left and right of the text, default is 1  
pady| extra space added above and below the text, default is 1  
  
and other arguments of `tkinter.Label`

### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured, for example:
        
        label.configure(text="new text")  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute, for example:
        
        text = label.cget("text")  
        

  * #### .bind(sequence=None, command=None, add=None)[​](#bindsequencenone-commandnone-addnone "Direct link to .bind\(sequence=None, command=None, add=None\)")

Bind events to the label.