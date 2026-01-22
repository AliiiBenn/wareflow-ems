---
name: customtkinter-docs
description: Access CustomTkinter documentation. Use when answering questions about CustomTkinter widgets, windows, themes, or when user asks about CTk, customtkinter library, or modern Python GUIs.
allowed-tools: Read, Glob, Grep
---

# CustomTkinter Documentation

You have access to the complete CustomTkinter documentation extracted from [customtkinter.tomschimansky.com](https://customtkinter.tomschimansky.com/documentation/).

## Available Documentation

The documentation is located in `./docs` and covers:

### Documentation (docs/)
- **Introduction**: Installation and upgrade
- **Appearance Mode**: Light/dark/system themes
- **Color and Themes**: Customizing colors with tuple colors
- **Scaling**: Widget scaling and dimensions
- **Packaging**: Packaging apps with CustomTkinter

### Widgets (widgets/)
All 16 widgets with complete arguments, methods, and examples:
- **CTkButton**: Button widget
- **CTkCheckBox**: Checkbox for boolean values
- **CTkComboBox**: Dropdown selection
- **CTkEntry**: Text input field
- **CTkFrame**: Container for widgets
- **CTkLabel**: Text label
- **CTkOptionMenu**: Option menu
- **CTkProgressBar**: Progress indicator
- **CTkRadioButton**: Radio button for choices
- **CTkScrollableFrame**: Scrollable container
- **CTkScrollbar**: Scrollbar widget
- **CTkSegmentedButton**: Segmented button control
- **CTkSlider**: Slider for numeric values
- **CTkSwitch**: Toggle switch
- **CTkTabview**: Tabbed interface
- **CTkTextbox**: Multi-line text input

### Windows (windows/)
- **CTk**: Main application window
- **CTkInputDialog**: Simple input dialog
- **CTkToplevel**: Additional windows

### Utility Classes (utility/)
- **CTkFont**: Font customization
- **CTkImage**: Image handling

### Tutorials (tutorial/)
- **Introduction**: Getting started
- **Grid System**: Layout management
- **Using Frames**: Organizing UI with frames

## How to Answer Questions

When answering CustomTkinter questions:

1. **Search the documentation** first using Grep to find relevant sections
2. **Read the specific widget/page** documentation
3. **Provide code examples** from the documentation
4. **Explain arguments and methods** for the specific widget
5. **Reference best practices** from tutorials

### Example Search Patterns

```bash
# Find information about a specific widget
grep -r "CTkButton" docs_perfect/widgets/

# Search for a specific feature
grep -r "configure\|cget" docs_perfect/widgets/CTkButton.md

# Find tutorials about a topic
grep -r "grid" docs_perfect/tutorial/
```

## Common Topics

### Installation
```bash
pip install customtkinter
```

### Basic App Structure
```python
import customtkinter

app = customtkinter.CTk()
app.geometry("400x150")
app.mainloop()
```

### Appearance Mode
```python
customtkinter.set_appearance_mode("dark")  # "light", "dark", "system"
```

### Theme Colors
Use tuple colors for light/dark mode:
```python
fg_color=("gray85", "gray25")  # (light, dark)
```

### Widget Arguments
All widgets support common arguments:
- `master`: Parent widget
- `width`, `height`: Size in pixels
- `fg_color`, `bg_color`: Colors
- `text_color`: Text color
- `corner_radius`: Rounded corners
- `font`: Font tuple (name, size)

### Methods
- `.configure(attribute=value)`: Change attributes
- `.cget("attribute")`: Get attribute value
- `.invoke()`: Trigger command (for buttons)

## When to Use This Skill

Activate this skill when:
- User asks about CustomTkinter widgets or features
- User needs help with CTk code
- User wants examples for specific widgets
- User asks about theming or styling
- User needs help with layout (grid system)
- User asks about packaging or deployment

Always cite the specific documentation file you're referencing when providing information.
