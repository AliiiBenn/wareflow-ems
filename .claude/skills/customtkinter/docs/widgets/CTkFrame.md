---
source: https://customtkinter.tomschimansky.com/documentation/widgets/frame
extracted: 2026-01-20 10:43:43
---

On this page

# CTkFrame

### Example Code[​](#example-code "Direct link to Example Code")
    
    
    frame = customtkinter.CTkFrame(master=root_tk, width=200, height=200)  
    

Frame structured into a class:
    
    
    class MyFrame(customtkinter.CTkFrame):  
        def __init__(self, master, **kwargs):  
            super().__init__(master, **kwargs)  
      
            # add widgets onto the frame, for example:  
            self.label = customtkinter.CTkLabel(self)  
            self.label.grid(row=0, column=0, padx=20)  
      
      
    class App(customtkinter.CTk):  
        def __init__(self):  
            super().__init__()  
            self.geometry("400x200")  
            self.grid_rowconfigure(0, weight=1)  # configure grid system  
            self.grid_columnconfigure(0, weight=1)  
      
            self.my_frame = MyFrame(master=self)  
            self.my_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")  
      
      
    app = App()  
    app.mainloop()  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, Frame or Toplevel  
width| width in px  
height| height in px  
border_width| width of border in px  
fg_color| foreground color, tuple: (light_color, dark_color) or single color or "transparent"  
border_color| border color, tuple: (light_color, dark_color) or single color  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured.

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute. 

  * #### .bind(sequence=None, command=None, add=None)[​](#bindsequencenone-commandnone-addnone "Direct link to .bind\(sequence=None, command=None, add=None\)")