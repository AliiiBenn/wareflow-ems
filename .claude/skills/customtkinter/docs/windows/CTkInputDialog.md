---
source: https://customtkinter.tomschimansky.com/documentation/windows/inputdialog
extracted: 2026-01-20 10:44:18
---

On this page

# CTkInputDialog

This is a simple dialog to input a string or number.

### Example Code[​](#example-code "Direct link to Example Code")
    
    
    dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="Test")  
    text = dialog.get_input()  # waits for input  
    

Example inside a program:
    
    
    app = customtkinter.CTk()  
    app.geometry("400x300")  
      
      
    def button_click_event():  
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="Test")  
        print("Number:", dialog.get_input())  
      
      
    button = customtkinter.CTkButton(app, text="Open Dialog", command=button_click_event)  
    button.pack(padx=20, pady=20)  
      
    app.mainloop()  
    

This example results in the following window and dialog:

![CTkInputDialog on Windows 11 example](/assets/images/inputdialog-1925f806bfa7f521efe412e9af8efd2f.png)

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
title| string for the dialog title  
text| text for the dialog itself  
fg_color| window color, tuple: (light_color, dark_color) or single color  
button_fg_color| color of buttons, tuple: (light_color, dark_color) or single color  
button_hover_color| hover color of buttons, tuple: (light_color, dark_color) or single color  
button_text_color| text color of buttons, tuple: (light_color, dark_color) or single color  
entry_fg_color| color of entry, tuple: (light_color, dark_color) or single color  
entry_border_color| border color of entry, tuple: (light_color, dark_color) or single color  
entry_text_color| text color of entry, tuple: (light_color, dark_color) or single color  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .get_input()[​](#get_input "Direct link to .get_input\(\)")

Retuns input, waits for 'Ok' or 'Cancel' button to be pressed.