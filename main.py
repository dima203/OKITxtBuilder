import os

from flet import Page, app, FilePicker, FilePickerResultEvent, ElevatedButton, Row, Icons, Text, Column, MainAxisAlignment, TextAlign, Theme, Colors, AlertDialog, alignment

from log import logger
from core import SheetBuilder


def main_app(page: Page):
    page.title = "Подготовка файла к печати"
    page.theme = Theme(color_scheme_seed=Colors.TEAL)
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.window.width = 500
    page.window.height = 500
    page.window.resizable = False
    page.window.center()
    page.update()
    sheet_builder = SheetBuilder()

    error_dialog = AlertDialog(
        title=Text("Ошибка", color=Colors.ERROR, text_align=TextAlign.CENTER),
        alignment=alignment.center,
        bgcolor=Colors.ERROR_CONTAINER,
    )

    ok_dialog = AlertDialog(
        title=Text("Готово", color=Colors.PRIMARY, text_align=TextAlign.CENTER),
        alignment=alignment.center,
        bgcolor=Colors.PRIMARY_CONTAINER,
    )

    def pick_file_result(e: FilePickerResultEvent):
        if e.files is None:
            return

        try:
            sheet_builder.read(e.files[0].path)
            selected_files.value = e.files[0].name
            selected_files.update()
        except Exception as exception:
            error_dialog.content = Text("Ошибка чтения файла!", color=Colors.ERROR)
            page.open(error_dialog)
            logger.warning(f'File {e.files[0].path} has wrong formatting.')

    def save_file_result(e: FilePickerResultEvent):
        if e.path is None:
            return

        if selected_files.value is None:
            error_dialog.content = Text("Сначала выберите файл для обработки!", color=Colors.ERROR)
            page.open(error_dialog)
        else:
            sheet_builder.write(e.path)
            page.open(ok_dialog)

    pick_file_dialog = FilePicker(on_result=pick_file_result)
    save_file_dialog = FilePicker(on_result=save_file_result)
    selected_files = Text(width=300, text_align=TextAlign.CENTER)

    page.overlay.append(pick_file_dialog)
    page.overlay.append(save_file_dialog)

    page.add(
        Row(
            alignment=MainAxisAlignment.CENTER,
            controls=[
                Column(
                    height=page.window.height,
                    alignment=MainAxisAlignment.CENTER,
                    spacing=30,
                    controls=[
                        ElevatedButton(
                            "Файл",
                            width=300,
                            height=70,
                            icon=Icons.UPLOAD_FILE,
                            on_click=lambda _: pick_file_dialog.pick_files(allow_multiple=False),
                        ),
                        selected_files,
                        ElevatedButton(
                            "Сохранить",
                            width=300,
                            height=70,
                            icon=Icons.SAVE,
                            on_click=lambda _: save_file_dialog.save_file(),
                        ),
                    ]
                )
            ]
        )
    )


def main_test() -> None:
    sheet_builder = SheetBuilder()
    sheet_builder.read(f'{os.path.dirname(__file__)}/Print_OKI/raschet_2.txt')
    sheet_builder.write(f'{os.path.dirname(__file__)}/1.txt')


if __name__ == '__main__':
    app(main_app)
    # main_test()
