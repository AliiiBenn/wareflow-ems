"""Test simple Flet pour diagnostiquer le problème."""

import flet as ft


def main(page: ft.Page):
    page.title = "Test Flet"
    page.add(ft.Text(value="Hello, world!"))
    page.add(ft.Text(value="Si tu vois ça, Flet marche!"))
    page.add(ft.Button("Click me"))


if __name__ == "__main__":
    ft.run(main)
