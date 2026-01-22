---
source: https://customtkinter.tomschimansky.com/documentation/utility-classes/font
extracted: 2026-01-20 10:44:23
---

On this page

# CTkFont

There are two methods in CustomTkinter to set a font. The first one is by creating a tuple of the form:
    
    
    button = customtkinter.CTkButton(app, font=("<family name>", <size in px>, "<optional keywords>"))  
    

This font can not be configured afterwards. The optional keywords can be normal/bold, roman/italic, underline and overstrike.

The better way is to create a CTkFont object, which can be modified afterwards and can be used for multiple widgets:
    
    
    button = customtkinter.CTkButton(app, font=customtkinter.CTkFont(family="<family name>", size=<size in px>, <optional keyword arguments>))  
      
    button.cget("font").configure(size=new_size)  # configure font afterwards  
    

All widgets get a CTkFont object by default, so configuring the font of a widget is possible by default.

A font object can also be applied to multiple widgets, and if it gets configured, the changes get passed to all widgets using this font:
    
    
    my_font = customtkinter.CTkFont(family="<family name>", size=<size in px>, <optional keyword arguments>)  
      
    button_1 = customtkinter.CTkButton(app, font=my_font)  
    button_2 = customtkinter.CTkButton(app, font=my_font)  
      
    my_font.configure(family="new name")  # changes apply to button_1 and button_2  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
family| The font family name as a string.  
size| The font height as an integer in pixel.  
weight| 'bold' for boldface, 'normal' for regular weight.  
slant| 'italic' for italic, 'roman' for unslanted.  
underline| True for underlined text, False for normal.  
overstrike| True for overstruck text, False for normal.  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured and get updated.

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute. 

  * #### .measure(text)[​](#measuretext "Direct link to .measure\(text\)")

Pass this method a string, and it will return the number of pixels of width that string will take in the font.

  * #### .metrics(option)[​](#metricsoption "Direct link to .metrics\(option\)")

If you call this method with no arguments, it returns a dictionary of all the font metrics. You can retrieve the value of just one metric by passing its name as an argument. Metrics include:

ascent: Number of pixels of height between the baseline and the top of the highest ascender.

descent: Number of pixels of height between the baseline and the bottom of the lowest ascender.

fixed: This value is 0 for a variable-width font and 1 for a monospaced font.

linespace: Number of pixels of height total. This is the leading of type set solid in the given font.