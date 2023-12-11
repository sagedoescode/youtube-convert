import flet as ft # pip install pyshorteners
import pytube
from moviepy.editor import *


class DownloadRow(ft.Row):
    def __init__(self, video_url, output_format=".mp4"):
        super().__init__()
        self.video_url = video_url
        self.output_format = output_format
        self.alignment = "center"
        self.controls = [
            ft.Text(value=video_url, size=16, selectable=True, italic=True),
            ft.IconButton(
                icon=ft.icons.DOWNLOAD,
                on_click=lambda e: self.download_video(),
                bgcolor=ft.colors.GREEN_700,
                tooltip="download"
            )
        ]

    def download_video(self):
        try:
            
            yt = pytube.YouTube(self.video_url)
            video_title = yt.title

            # Download video stream
            if self.output_format == ".3gp":
                # Filter for compatible video and audio codecs
                video_stream = yt.streams.filter(
                    progressive=True,
                    mime_type="video/3gp",
                ).order_by('resolution').desc().first()
                # Check if audio stream is available
                audio_stream = yt.streams.filter(
                    mime_type="audio/3gpp",
                ).order_by('abr').desc().first()

                if not audio_stream:
                    self.page.show_snack_bar(ft.SnackBar(ft.Text("Audio stream not available for .3gp download.")))
                    return
            else:
                video_stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()

                output_filename = video_title + self.output_format

                # Download the video stream
                video_stream.download(filename=output_filename)

            # Combine video and audio for .3gp format
            if self.output_format == ".3gp":
                # Use ffmpeg to combine video and audio streams
                os.system(f"ffmpeg -i {video_title}.3gp -i {audio_stream.url} -map 0:v -map 1:a -c copy {output_filename}")
                os.remove(video_title + ".3gp")

            # Inform the user
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Video downloaded successfully!")))
        except Exception as e:
            print(e)
            self.page.show_snack_bar(ft.SnackBar(ft.Text("An error occurred. Please try again.")))


def main(page: ft.Page):
    page.title = "You 2 Convert"
    page.theme_mode = "dark"
    page.splash = ft.ProgressBar(visible=False)
    page.horizontal_alignment = "center"
    page.window_width = 600
    page.window_height = 700
    page.scroll = "hidden"

    page.fonts = {
        "sf-simple": "/fonts/San-Francisco/SFUIDisplay-Light.ttf",
        "sf-bold": "/fonts/San-Francisco/SFUIDisplay-Bold.ttf"
    }
    page.theme = ft.Theme(font_family="sf-simple")

    def change_theme(e):
        """
        Changes the app's theme_mode, from dark to light or light to dark. A splash(progress bar) is also shown.

        :param e: The event that triggered the function
        :type e: ControlEvent
        """
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"  # changes the page's theme_mode
        theme_icon_button.selected = not theme_icon_button.selected  # changes the icon
        page.update()
    def download_youtube_video(e: ft.ControlEvent):
        user_url = url_field.value
        output_format = format_dropdown.value.lower()

        if user_url:
            page.splash.visible = True
            page.update()
            try:
                page.add(DownloadRow(user_url, output_format))
            except Exception as exception:
                print(exception)
                page.show_snack_bar(ft.SnackBar(ft.Text("An error occurred. Please try again.")))
            finally:
                page.splash.visible = False
                page.update()
        else:
            page.show_snack_bar(ft.SnackBar(ft.Text("Please enter a YouTube video URL!")))
    theme_icon_button = ft.IconButton(
        ft.icons.DARK_MODE,
        selected=False,
        selected_icon=ft.icons.LIGHT_MODE,
        icon_size=35,
        tooltip="change theme",
        on_click=change_theme,
        style=ft.ButtonStyle(color={"": ft.colors.BLACK, "selected": ft.colors.WHITE}),
    )
    page.appbar = ft.AppBar(
        title=ft.Text("YouTube Video Convert", color="white"),
        center_title=True,
        bgcolor="#FF0000",
        actions=[theme_icon_button]
    )
    # Add a dropdown for selecting the output format
    format_dropdown = ft.Dropdown(
        label="Media Format",
        hint_text="Choose the desired format",
        options=[
            
            ft.dropdown.Option(".mp4"),
            ft.dropdown.Option(".wav"),
            ft.dropdown.Option(".mp3"),
            ft.dropdown.Option(".3gp"),
            ft.dropdown.Option(".mkv")],
        width=800,
        tooltip="Select output format"
    )

    page.add(
        url_field := ft.TextField(
            hint_text="paste YouTube video URL here",
            value='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            label="YouTube Video URL",
            max_length=200,
            width=800,
            keyboard_type=ft.KeyboardType.URL,
            suffix=ft.FilledButton("Download!", on_click=download_youtube_video),
            on_submit=download_youtube_video
        ),
        format_dropdown,
        ft.Text("Downloaded Videos:", weight=ft.FontWeight.BOLD, size=23, font_family="sf-bold")
    )

ft.app(target=main)
