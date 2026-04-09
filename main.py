import os

from flet import (
    Event,
    Page,
    FilePicker,
    Button,
    ProgressBar,
    Row,
    Icons,
    Text,
    Column,
    MainAxisAlignment,
    TextAlign,
    Theme,
    Colors,
    AlertDialog,
    Alignment,
    run
)

from log import logger
from core import SheetBuilder


async def main_app(page: Page):
    page.title = "Подготовка файла к печати"
    page.theme = Theme(color_scheme_seed=Colors.TEAL, use_material3=True)
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.window.width = 600
    page.window.height = 800
    page.window.resizable = True
    await page.window.center()
    page.update()
    sheet_builder = SheetBuilder()

    error_dialog = AlertDialog(
        title=Text("Ошибка", color=Colors.ERROR),
        alignment=Alignment.CENTER,
        bgcolor=Colors.ERROR_CONTAINER,
    )

    ok_dialog = AlertDialog(
        title=Text("Готово", color=Colors.PRIMARY),
        alignment=Alignment.CENTER,
        bgcolor=Colors.PRIMARY_CONTAINER,
    )

    def show_progress(text: str | None = None, value: float | None = None) -> None:
        progress_bar.value = value
        progress_bar.visible = True
        progress_text.visible = text is not None
        progress_text.value = text
        page.update()

    def hide_progress(text: str | None = None) -> None:
        progress_bar.value = None
        progress_bar.visible = False
        progress_text.visible = text is not None
        progress_text.value = text
        page.update()

    def update_progress(current: int, total: int) -> None:
        progress_bar.value = current / total
        progress_bar.update()
        page.update()

    async def handle_pick_files(e: Event[Button]):
        files = await FilePicker().pick_files(allow_multiple=False)
        if files:
            show_progress("Чтение файла", 0)
            selected_files.value = files[0].name
            await sheet_builder.read(files[0].path, update_progress)
            selected_files.update()
            hide_progress("Файл прочитан")
        else:
            hide_progress()


    async def handle_save_file(e: Event[Button]):
        if not selected_files.value:
            error_dialog.content = Text(
                "Сначала выберите файл для обработки!", color=Colors.ERROR
            )
            page.show_dialog(error_dialog)

            return

        path = await FilePicker().save_file()
        if path is None:
            return

        show_progress("Подготовка к сохранению")
        sheet_builder.write(path)
        hide_progress("Сохранено")

    def pick_file_result(e):
        if e.files is None:
            return

        try:
            sheet_builder.read(e.files[0].path)
            selected_files.value = e.files[0].name
            selected_files.update()
        except Exception:
            error_dialog.content = Text("Ошибка чтения файла!", color=Colors.ERROR)
            page.show_dialog(error_dialog)
            logger.warning(f"File {e.files[0].path} has wrong formatting.")

    def save_file_result(e):
        if e.path is None:
            return

        if selected_files.value is None:
            error_dialog.content = Text(
                "Сначала выберите файл для обработки!", color=Colors.ERROR
            )
            page.show_dialog(error_dialog)
        else:
            sheet_builder.write(e.path)
            page.show_dialog(ok_dialog)

    selected_files = Text(width=300, text_align=TextAlign.CENTER, visible=False)
    progress_bar = ProgressBar(width=300, visible=False)
    progress_text = Text(width=300, text_align=TextAlign.CENTER, visible=False)

    page.add(
        Row(
            alignment=MainAxisAlignment.CENTER,
            controls=[
                Column(
                    height=page.window.height,
                    alignment=MainAxisAlignment.CENTER,
                    spacing=30,
                    controls=[
                        Button(
                            "Открыть",
                            width=300,
                            height=70,
                            icon=Icons.UPLOAD_FILE,
                            on_click=handle_pick_files,
                        ),
                        Button(
                            "Сохранить",
                            width=300,
                            height=70,
                            icon=Icons.SAVE,
                            on_click=handle_save_file,
                        ),
                        selected_files,
                        Column(
                            controls = [progress_bar, progress_text]
                        )
                    ],
                )
            ],
        )
    )
    page.update()


def main_test() -> None:
    sheet_builder = SheetBuilder()
    sheet_builder.read(f"{os.path.dirname(__file__)}/Print_OKI/payslips_random.txt")
    # sheet_builder.read(f"{os.path.dirname(__file__)}/Print_OKI/raschet_2.txt")
    sheet_builder.write(f"{os.path.dirname(__file__)}/1.txt")


if __name__ == "__main__":
    run(main_app)
    # main_test()
