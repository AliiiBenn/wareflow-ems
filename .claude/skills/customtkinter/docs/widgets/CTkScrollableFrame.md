---
source: https://customtkinter.tomschimansky.com/documentation/widgets/scrollableframe
extracted: 2026-01-20 10:43:56
---

On this page

# CTkScrollableFrame

### Example Code[​](#example-code "Direct link to Example Code")
    
    
    scrollable_frame = customtkinter.CTkScrollableFrame(app, width=200, height=200)  
    

Structured into a class:
    
    
    class MyFrame(customtkinter.CTkScrollableFrame):  
        def __init__(self, master, **kwargs):  
            super().__init__(master, **kwargs)  
      
            # add widgets onto the frame...  
            self.label = customtkinter.CTkLabel(self)  
            self.label.grid(row=0, column=0, padx=20)  
      
      
    class App(customtkinter.CTk):  
        def __init__(self):  
            super().__init__()  
      
            self.my_frame = MyFrame(master=self, width=300, height=200)  
            self.my_frame.grid(row=0, column=0, padx=20, pady=20)  
      
      
    app = App()  
    app.mainloop()  
    

The above example can be slightly modified, so that the scrollable frame completely fills the app window:
    
    
    class MyFrame(customtkinter.CTkScrollableFrame):  
        def __init__(self, master, **kwargs):  
            super().__init__(master, **kwargs)  
      
            # add widgets onto the frame...  
            self.label = customtkinter.CTkLabel(self)  
            self.label.grid(row=0, column=0, padx=20)  
      
      
    class App(customtkinter.CTk):  
        def __init__(self):  
            super().__init__()  
            self.grid_rowconfigure(0, weight=1)  
            self.grid_columnconfigure(0, weight=1)  
      
            self.my_frame = MyFrame(master=self, width=300, height=200, corner_radius=0, fg_color="transparent")  
            self.my_frame.grid(row=0, column=0, sticky="nsew")  
      
      
    app = App()  
    app.mainloop()  
    

More examples can be found here: <https://github.com/TomSchimansky/CustomTkinter/blob/master/examples/scrollable_frame_example.py>

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, Frame or Toplevel  
width| width in px (inner frame dimensions)  
height| height in px (inner frame dimensions)  
corner_radius| corner radius in px  
border_width| border width in px  
fg_color| foreground color, tuple: (light_color, dark_color) or single color or "transparent"  
border_color| border color, tuple: (light_color, dark_color) or single color  
scrollbar_fg_color| scrollbar foreground color, tuple: (light_color, dark_color) or single color  
scrollbar_button_color| scrollbar button color, tuple: (light_color, dark_color) or single color  
scrollbar_button_hover_color| scrollbar button hover color, tuple: (light_color, dark_color) or single color  
label_fg_color| label foreground color color, tuple: (light_color, dark_color) or single color  
label_text_color| label text color, tuple: (light_color, dark_color) or single color  
label_text| label text for label (title for frame)  
label_font| font for label, tupel font or CTkFont  
label_anchor| anchor for label, orientation of text, ("n", "ne", "e", "se", "s", "sw", "w", "nw", "center")  
orientation| scrolling direction, "vertical" (default), "horizontal"  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured.

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute.