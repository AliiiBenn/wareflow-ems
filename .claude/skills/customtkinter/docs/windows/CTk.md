---
source: https://customtkinter.tomschimansky.com/documentation/windows/window
extracted: 2026-01-20 10:44:15
---

On this page

# CTk

The CTk class forms the basis of any CustomTkinter program, it creates the main app window. During the runtime of a program there should only be one instance of this class with a single call of the `.mainloop()` method, which starts the app. Additional windows are created using the CTkToplevel class.

### Example Code[​](#example-code "Direct link to Example Code")

Example without using classes:
    
    
    app = customtkinter.CTk()  
    app.geometry("600x500")  
    app.title("CTk example")  
      
    app.mainloop()  
    

Example with classes:
    
    
    class App(customtkinter.CTk):  
        def __init__(self):  
            super().__init__()  
            self.geometry("600x500")  
            self.title("CTk example")  
      
            # add widgets to app  
            self.button = customtkinter.CTkButton(self, command=self.button_click)  
            self.button.grid(row=0, column=0, padx=20, pady=10)  
      
        # add methods to app  
        def button_click(self):  
            print("button click")  
      
      
    app = App()  
    app.mainloop()  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
fg_color| window background color, tuple: (light_color, dark_color) or single color  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured and updated, for example:
        
        app.configure(fg_color=new_fg_color)  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute, for example:
        
        fg_color = app.cget("fg_color")  
        

  * #### .title(string)[​](#titlestring "Direct link to .title\(string\)")

Set title of window.

  * #### .geometry(geometry_string)[​](#geometrygeometry_string "Direct link to .geometry\(geometry_string\)")

Set geometry and positions of the window like this: `"<width>x<height>"` or `"<width>x<height>+<x_pos>+<y_pos>"`

  * #### .minsize(width, height)[​](#minsizewidth-height "Direct link to .minsize\(width, height\)")

Set minimal window size.

  * #### .maxsize(width, height)[​](#maxsizewidth-height "Direct link to .maxsize\(width, height\)")

Set max window size.

  * #### .resizable(width, height)[​](#resizablewidth-height "Direct link to .resizable\(width, height\)")

Define, if width and/or height should be resizablee with bool values.

  * #### .after(milliseconds, command)[​](#aftermilliseconds-command "Direct link to .after\(milliseconds, command\)")

Execute command after milliseconds without blocking the main loop.

  * #### .withdraw()[​](#withdraw "Direct link to .withdraw\(\)")

Hide window and icon. Restore it with .deiconify().

  * #### .iconify()[​](#iconify "Direct link to .iconify\(\)")

Iconifies the window. Restore it with .deiconify().

  * #### .deiconify()[​](#deiconify "Direct link to .deiconify\(\)")

Deiconify the window.

  * #### .state(new_state)[​](#statenew_state "Direct link to .state\(new_state\)")

Set the window state ('normal', 'iconic', 'withdrawn', 'zoomed'), returns current state if no argument is passed.