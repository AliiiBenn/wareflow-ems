---
source: https://customtkinter.tomschimansky.com/documentation/widgets/textbox
extracted: 2026-01-20 10:44:12
---

On this page

# CTkTextbox

The CTkTextbox class creates a textbox, which is scrollable in vertical and horizontal direction (with `wrap='none'`). The `insert`, `get` and `delete` methods are based on tkinter indices, which are explained here: <https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/text-index.html>

### Example Code[​](#example-code "Direct link to Example Code")

Example without using classes:
    
    
    textbox = customtkinter.CTkTextbox(app)  
      
    textbox.insert("0.0", "new text to insert")  # insert at line 0 character 0  
    text = textbox.get("0.0", "end")  # get text from line 0 character 0 till the end  
    textbox.delete("0.0", "end")  # delete all text  
    textbox.configure(state="disabled")  # configure textbox to be read-only  
    

Example with classes, where the textbox completely fills the window: 
    
    
    class App(customtkinter.CTk):  
        def __init__(self):  
            super().__init__()  
            self.grid_rowconfigure(0, weight=1)  # configure grid system  
            self.grid_columnconfigure(0, weight=1)  
      
            self.textbox = customtkinter.CTkTextbox(master=self, width=400, corner_radius=0)  
            self.textbox.grid(row=0, column=0, sticky="nsew")  
            self.textbox.insert("0.0", "Some example text!\n" * 50)  
      
      
    app = App()  
    app.mainloop()  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, frame, top-level  
width| box width in px  
height| box height in px  
corner_radius| corner radius in px  
border_width| border width in px  
border_spacing| minimum space between text and widget border, default is 3. Set to 0 for the text to touch the widget border (if corner_radius=0)  
fg_color| main widget color, tuple: (light_color, dark_color) or single color or "transparent"  
border_color| border color, tuple: (light_color, dark_color) or single color  
text_color| text color, tuple: (light_color, dark_color) or single color  
scrollbar_button_color| main color of scrollbar, tuple: (light_color, dark_color) or single color  
scrollbar_button_hover_color| hover color of scrollbar, tuple: (light_color, dark_color) or single color  
font| text font, tuple: (font_name, size)  
activate_scrollbars| default is True, set to False to prevent scrollbars from appearing  
state| "normal" (standard) or "disabled" (not clickable, read-only)  
wrap| how to wrap text at end of line, default is 'char', other options are 'word' or 'none' for no wrapping at all and horizontal scrolling  
  
and the following arguments of the tkinter.Text class:

`"autoseparators", "cursor", "exportselection", "insertborderwidth", "insertofftime", "insertontime", "insertwidth", "maxundo", "padx", "pady", "selectborderwidth", "spacing1", "spacing2", "spacing3", "state", "tabs", "takefocus", "undo", "xscrollcommand", "yscrollcommand"`

### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured and updated.
        
        textbox.configure(state=..., text_color=..., ...)  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Get values of all attributes specified as string.

  * #### .bind(sequence=None, command=None, add=None)[​](#bindsequencenone-commandnone-addnone "Direct link to .bind\(sequence=None, command=None, add=None\)")

Bind commands to events specified by sequence string.

  * #### .unbind(sequence, funcid=None)[​](#unbindsequence-funcidnone "Direct link to .unbind\(sequence, funcid=None\)")

Unbind command from sequence specified by funcid, which is returned by .bind().

  * #### .insert(index, text, tags=None)[​](#insertindex-text-tagsnone "Direct link to .insert\(index, text, tags=None\)")

Insert text at given index. Index for the tkinter.Text class is specified by 'line.character', 'end', 'insert' or other keywords described here: <https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/text-index.html>

  * #### .delete(self, index1, index2=None)[​](#deleteself-index1-index2none "Direct link to .delete\(self, index1, index2=None\)")

Delete the characters between index1 and index2 (not included).

  * #### .get(index1, index2=None)[​](#getindex1-index2none "Direct link to .get\(index1, index2=None\)")

Return the text from INDEX1 to INDEX2 (not included).

  * #### .focus_set()[​](#focus_set "Direct link to .focus_set\(\)")

Set focus to the text widget.

and nearly all other methods of tkinter.Text described here: <https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/text-methods.html>