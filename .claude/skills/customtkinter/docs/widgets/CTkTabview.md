---
source: https://customtkinter.tomschimansky.com/documentation/widgets/tabview
extracted: 2026-01-20 10:44:10
---

On this page

# CTkTabview

The CTkTabview creates a tabview, similar to a notebook in tkinter. The tabs, which are created with `.add("<tab-name>")` are CTkFrames and can be used like CTkFrames. Any widgets can be placed on them.

### Example Code[​](#example-code "Direct link to Example Code")

Example without using classes:
    
    
    tabview = customtkinter.CTkTabview(master=app)  
    tabview.pack(padx=20, pady=20)  
      
    tabview.add("tab 1")  # add tab at the end  
    tabview.add("tab 2")  # add tab at the end  
    tabview.set("tab 2")  # set currently visible tab  
      
    button = customtkinter.CTkButton(master=tabview.tab("tab 1"))  
    button.pack(padx=20, pady=20)  
    

It's also possible to save tabs in extra variables:
    
    
    tab_1 = tabview.add("tab 1")  
    tab_2 = tabview.add("tab 2")  
      
    button = customtkinter.CTkButton(tab_1)  
    

Example with classes:
    
    
    class MyTabView(customtkinter.CTkTabview):  
        def __init__(self, master, **kwargs):  
            super().__init__(master, **kwargs)  
      
            # create tabs  
            self.add("tab 1")  
            self.add("tab 2")  
      
            # add widgets on tabs  
            self.label = customtkinter.CTkLabel(master=self.tab("tab 1"))  
            self.label.grid(row=0, column=0, padx=20, pady=10)  
      
      
    class App(customtkinter.CTk):  
        def __init__(self):  
            super().__init__()  
      
            self.tab_view = MyTabView(master=self)  
            self.tab_view.grid(row=0, column=0, padx=20, pady=20)  
      
      
    app = App()  
    app.mainloop()  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, frame, top-level  
width| width in px, tabs will be slightly smaller  
height| height in px, tabs will be slightly smaller  
corner_radius| corner radius in px  
border_width| border width in px  
fg_color| foreground color of the tabview itself and the tabs, tuple: (light_color, dark_color) or single color  
border_color| border color, tuple: (light_color, dark_color) or single color  
segmented_button_fg_color| foreground color of segmented button, tuple: (light_color, dark_color) or single color  
segmented_button_selected_color| selected color of segmented button, tuple: (light_color, dark_color) or single color  
segmented_button_selected_hover_color| selected hover color of segmented button, tuple: (light_color, dark_color) or single color  
segmented_button_unselected_color| unselected color of segmented button, tuple: (light_color, dark_color) or single color  
segmented_button_unselected_hover_color| unselected hover color of segmented button, tuple: (light_color, dark_color) or single color  
text_color| text color of segmented button, tuple: (light_color, dark_color) or single color  
text_color_disabled| text color of segmented buttons when widget is disabled, tuple: (light_color, dark_color) or single color  
command| function will be called when segmented button is clicked  
anchor| position of the segmneted button, default is "n", values are "nw", "n", "ne", "sw", "s", "se"  
state| "normal" or "disabled"  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured and updated.

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Get values of all attributes specified as string.

  * #### .tab(name)[​](#tabname "Direct link to .tab\(name\)")

Returns reference to tab with given name. Can be used like a frame like this:
        
        button = customtkinter.CTkButton(master=tabview.tab("tab name"))  
        

  * #### .insert(index, name)[​](#insertindex-name "Direct link to .insert\(index, name\)")

Insert tab with name at position of index, name must be unique.

  * #### .add(name)[​](#addname "Direct link to .add\(name\)")

Add tab with name at the end, name must be unique.

  * #### .index(name)[​](#indexname "Direct link to .index\(name\)")

Get index of tab with given name.

  * #### .move(new_index, name)[​](#movenew_index-name "Direct link to .move\(new_index, name\)")

Move tab with name to given index. 

  * #### .rename(old_name, new_name)[​](#renameold_name-new_name "Direct link to .rename\(old_name, new_name\)")

Rename tab.

  * #### .delete(name)[​](#deletename "Direct link to .delete\(name\)")

Delete tab with name.

  * #### .set(name)[​](#setname "Direct link to .set\(name\)")

Set tab with name to be visible.

  * #### .get()[​](#get "Direct link to .get\(\)")

Get name of tab that's currently visible.