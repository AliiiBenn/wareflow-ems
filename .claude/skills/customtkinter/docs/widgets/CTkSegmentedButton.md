---
source: https://customtkinter.tomschimansky.com/documentation/widgets/segmentedbutton
extracted: 2026-01-20 10:44:02
---

On this page

# CTkSegmentedButton

### Example Code[​](#example-code "Direct link to Example Code")

Without variable:
    
    
    def segmented_button_callback(value):  
        print("segmented button clicked:", value)  
      
    segemented_button = customtkinter.CTkSegmentedButton(app, values=["Value 1", "Value 2", "Value 3"],  
                                                         command=segmented_button_callback)  
    segemented_button.set("Value 1")  
    

With variable:
    
    
    def segmented_button_callback(value):  
        print("segmented button clicked:", value)  
      
    segemented_button_var = customtkinter.StringVar(value="Value 1")  
    segemented_button = customtkinter.CTkSegmentedButton(app, values=["Value 1", "Value 2", "Value 3"],  
                                                         command=segmented_button_callback,  
                                                         variable=segemented_button_var)  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, frame, top-level  
width| box width in px  
height| box height in px  
corner_radius| corner radius in px  
border_width| space in px between buttons and the edges of the widget  
fg_color| color around the buttons, tuple: (light_color, dark_color) or single color  
selected_color| color of the selected button, tuple: (light_color, dark_color) or single color  
selected_hover_color| hover color of selected button, tuple: (light_color, dark_color) or single color  
unselected_color| color of the unselected buttons, tuple: (light_color, dark_color) or single color or "transparent"  
unselected_hover_color| hover color of unselected buttons, tuple: (light_color, dark_color) or single color  
text_color| text color, tuple: (light_color, dark_color) or single color  
text_color_disabled| text color when disabled, tuple: (light_color, dark_color) or single color  
font| button text font, tuple: (font_name, size)  
values| list of string values for the buttons, can't be empty  
variable| StringVar to control the current selected value  
state| "normal" (standard) or "disabled" (not clickable, darker color)  
command| function will be called when the dropdown is clicked manually  
dynamic_resizing| enable/disable automatic resizing when text is too big to fit: True (standard), False  
  
### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured and updated, for example:
        
        segemented_button.configure(state="disabled")  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute. 

  * #### .set(value)[​](#setvalue "Direct link to .set\(value\)")

Set to specific value. If value is not in values list, no button will be selected.

  * #### .get()[​](#get "Direct link to .get\(\)")

Get current string value.

  * #### .insert(index, value)[​](#insertindex-value "Direct link to .insert\(index, value\)")

Insert new value at given index into segmented button. Value will be also inserted into the values list.

  * #### .move(new_index, value)[​](#movenew_index-value "Direct link to .move\(new_index, value\)")

Move existing value to new index position.

  * #### .delete(value)[​](#deletevalue "Direct link to .delete\(value\)")

Remove value from segmented button and values list. If value is currently selected, no button will be selected afterwards.