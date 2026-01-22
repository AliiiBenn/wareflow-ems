---
source: https://customtkinter.tomschimansky.com/documentation/widgets/entry
extracted: 2026-01-20 10:43:40
---

On this page

# CTkEntry

### Example Code[​](#example-code "Direct link to Example Code")
    
    
    entry = customtkinter.CTkEntry(app, placeholder_text="CTkEntry")  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
master| root, tkinter.Frame or CTkFrame  
textvariable| tkinter.StringVar object  
width| entry width in px  
height| entry height in px  
corner_radius| corner radius in px  
fg_color| foreground color, tuple: (light_color, dark_color) or single color or "transparent"  
text_color| entry text color, tuple: (light_color, dark_color) or single color  
placeholder_text_color| tuple: (light_color, dark_color) or single color  
placeholder_text| hint on the entry input (disappears when selected), default is None, don't works in combination with a textvariable  
font| entry text font, tuple: (font_name, size)  
state| "normal" (standard) or "disabled" (not clickable)  
  
and the following arguments of the tkinter.Entry class:

`"exportselection", "insertborderwidth", "insertofftime", "insertontime", "insertwidth", "justify", "selectborderwidth", "show", "takefocus", "validate", "validatecommand", "xscrollcommand"`

### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured, for example:
        
        entry.configure(state="disabled")  
        

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute, for example:
        
        state = entry.cget("state")  
        

  * #### .bind(sequence=None, command=None, add=None)[​](#bindsequencenone-commandnone-addnone "Direct link to .bind\(sequence=None, command=None, add=None\)")

Bind command function to event specified by sequence.

  * #### .delete(first_index, last_index=None)[​](#deletefirst_index-last_indexnone "Direct link to .delete\(first_index, last_index=None\)")

Deletes characters from the widget, starting with the one at [index](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/entry.html#entry-index) first_index, up to but not including the character at position last_index. If the second argument is omitted, only the single character at position first is deleted.

  * #### .insert(index, string)[​](#insertindex-string "Direct link to .insert\(index, string\)")

Inserts string before the character at the given [index](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/entry.html#entry-index).

  * #### .get()[​](#get "Direct link to .get\(\)")

Returns current string in the entry.

  * #### .focus()[​](#focus "Direct link to .focus\(\)")

  * #### .focus_force()[​](#focus_force "Direct link to .focus_force\(\)")

  * #### .index(index)[​](#indexindex "Direct link to .index\(index\)")

  * #### .icursor(index)[​](#icursorindex "Direct link to .icursor\(index\)")

  * #### .select_adjust(index)[​](#select_adjustindex "Direct link to .select_adjust\(index\)")

  * #### .select_from(index)[​](#select_fromindex "Direct link to .select_from\(index\)")

  * #### .select_clear()[​](#select_clear "Direct link to .select_clear\(\)")

  * #### .select_present()[​](#select_present "Direct link to .select_present\(\)")

  * #### .select_range(start_index, end_index)[​](#select_rangestart_index-end_index "Direct link to .select_range\(start_index, end_index\)")

  * #### .select_to(index)[​](#select_toindex "Direct link to .select_to\(index\)")

  * #### .xview(index)[​](#xviewindex "Direct link to .xview\(index\)")

  * #### .xview_moveto(f)[​](#xview_movetof "Direct link to .xview_moveto\(f\)")

  * #### .xview_scroll(number, what)[​](#xview_scrollnumber-what "Direct link to .xview_scroll\(number, what\)")