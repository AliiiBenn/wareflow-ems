---
source: https://customtkinter.tomschimansky.com/documentation/utility-classes/image
extracted: 2026-01-20 10:44:26
---

On this page

# CTkImage

The CTkImage is not a widget itself, but a container for up to two PIL Image objects for light and dark mode. There's also a size tuple which describes the width and height of the image independent of scaling. Therefore it's important that the PIL Image's are in a higher resolution than the given size tuple, so that the image is not blurry if rendered on a 4K monitor with 2x scaling. So that the image is displayed in sharp resolution on a 2x scaled monitor, the given OIL Image's must have at least double the resolution than the requested size.

Create a CTkImage object:
    
    
    from PIL import Image  
      
    my_image = customtkinter.CTkImage(light_image=Image.open("<path to light mode image>"),  
                                      dark_image=Image.open("<path to dark mode image>"),  
                                      size=(30, 30))  
      
    image_label = customtkinter.CTkLabel(app, image=my_image, text="")  # display image with a CTkLabel  
    

### Arguments[​](#arguments "Direct link to Arguments")

argument| value  
---|---  
light_image| PIL Image object for light mode  
dark_image| PIL Image object for dark mode  
size| tuple (width in px, height in px) for rendering size independent of scaling  
  
If only `light_image` or only `dark_image` is given, the existing one will be used for both light and dark mode.

### Methods[​](#methods "Direct link to Methods")

  * #### .configure(attribute=value, ...)[​](#configureattributevalue- "Direct link to .configure\(attribute=value, ...\)")

All attributes can be configured and updated.

  * #### .cget(attribute_name)[​](#cgetattribute_name "Direct link to .cget\(attribute_name\)")

Pass attribute name as string and get current value of attribute.