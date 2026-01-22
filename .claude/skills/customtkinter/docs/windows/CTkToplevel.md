---
source: https://customtkinter.tomschimansky.com/documentation/windows/toplevel
extracted: 2026-01-20 10:44:21
---

On this page

# CTkToplevel

The CTkToplevel class is used to create additional windows. For a CTkToplevel window, there is no call of `.mainloop()` needed, it opens right when it's created.

### Example Code[​](#example-code "Direct link to Example Code")
    
    
    toplevel = CTkToplevel(app)  # master argument is optional    
    

The following example shows how to create a toplevel window, which can be opened from the main app widnow. Before the toplevel window gets created, it is checked if the window already exists, to prevent opening the same window multiple times.
    
    
    class ToplevelWindow(customtkinter.CTkToplevel):  
        def __init__(self, *args, **kwargs):  
            super().__init__(*args, **kwargs)  
            self.geometry("400x300")  
      
            self.label = customtkinter.CTkLabel(self, text="ToplevelWindow")  
            self.label.pack(padx=20, pady=20)  
      
      
    class App(customtkinter.CTk):  
        def __init__(self, *args, **kwargs):  
            super().__init__(*args, **kwargs)  
            self.geometry("500x400")  
      
            self.button_1 = customtkinter.CTkButton(self, text="open toplevel", command=self.open_toplevel)  
            self.button_1.pack(side="top", padx=20, pady=20)  
      
            self.toplevel_window = None  
      
        def open_toplevel(self):  
            if self.toplevel_window is None or not self.toplevel_window.winfo_exists():  
                self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed  
            else:  
                self.toplevel_window.focus()  # if window exists focus it  
      
      
    app = App()  
    app.mainloop()  
    

The example code results in the following windows:

![CTkToplevel on Windows 11 example](/assets/images/toplevel-7b27ca69e448504aa58665d51e59ab82.png)

### Arguments:[​](#arguments "Direct link to Arguments:")

argument| value  
---|---  
fg_color| window background color, tuple: (light_color, dark_color) or single color  
  
### Methods:[​](#methods "Direct link to Methods:")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured and updated, for example:
        
        toplevel.configure(fg_color="red")  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute, for example:
        
        fg_color = toplevel.cget("fg_color")  
        

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