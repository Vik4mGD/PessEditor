import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import (
    Qt, QLocale, Signal, QUrl, QProcess, QSignalBlocker, QPointF, QRect, QRectF, QSettings
)
from PySide6.QtGui import (
    QDragEnterEvent, QDropEvent, QFont, QImage, QPixmap,
    QPainter, QPen, QColor, QIcon
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QFrame, QMessageBox,
    QStackedWidget, QDoubleSpinBox, QFormLayout, QSizePolicy,
    QGridLayout, QSlider, QScrollArea, QComboBox, QSpinBox, QProgressDialog,
    QLineEdit, QDialogButtonBox
)

APP_NAME = "Pess Editor"
APP_VERSION = "0.8.3"

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv",
    ".wmv", ".m4v", ".mpg", ".mpeg", ".ts", ".mts",
    ".m2ts", ".3gp"
}

STRINGS = {
    "en": {
        "subtitle": "A simple video editor for Windows",
        "step_import": "1  Select video",
        "step_edit": "2  Edit",
        "step_export": "3  Export",
        "drop_title": "Choose a video to get started",
        "drop_hint": "Drag and drop a video into this area, or browse your files.",
        "browse": "Browse videos",
        "supported": "Supported formats: MP4, MKV, MOV, AVI, WebM, MPEG-TS and more.",
        "workflow_title": "A simple workflow",
        "workflow_1_title": "Select a video",
        "workflow_1_text": "Open a video from your computer or drag it into the window.",
        "workflow_2_title": "Review its details",
        "workflow_2_text": "Check the resolution, frame rate, codecs and original bitrate.",
        "workflow_3_title": "Prepare your export",
        "workflow_3_text": "Adjust the available output settings before exporting.",
        "editor": "Video editor",
        "editor_subtitle": "Review your video and prepare its output settings.",
        "change": "Choose another video",
        "export": "Export video",
        "bitrate": "Video bitrate",
        "bitrate_help": "Original video-stream bitrate detected by FFprobe. If the container only provides a total bitrate, the video value is estimated after subtracting known audio bitrates.",
        "bitrate_estimated": "Estimated from the container bitrate and known audio streams.",
        "bitrate_unavailable": "Unavailable",
        "ffprobe_missing": "FFprobe was not found. Install FFmpeg and add its bin folder to PATH.",
        "settings": "Output settings",
        "back": "Back to start",
        "file_details": "Video information",
        "preview": "Preview",
        "file_name": "File name",
        "location": "Location",
        "duration": "Duration",
        "resolution": "Resolution",
        "fps": "Frame rate",
        "video_codec": "Video codec",
        "audio_codec": "Audio codec",
        "file_size": "File size",
        "sample_rate": "Audio sample rate",
        "channels": "Audio channels",
        "no_audio": "No audio stream",
        "export_disabled": "The export engine has not been implemented yet.",
        "play_error": "Could not play this video:",
        "coming": "Choose a video to preview it here.",
        "unsupported": "This file is not a supported video or FFprobe could not read a video stream.",
        "invalid_path": "The selected path is not a valid file.",
        "metadata_error": "Could not read this video's information. The file may be damaged or use an unsupported codec.",
        "estimated": "Approx.",
        "timeline_hint": "Drag the blue handles to set the trim start and end. Drag the white marker to seek.",
        "trim": "Trim range",
        "trim_start": "Start (seconds)",
        "trim_end": "End (seconds)",
        "trim_hint": "Playback will stop at the selected end point.",
        "crop": "Crop area",
        "crop_hint": "Drag on the preview to create a crop; drag inside to move and handles to resize.",
        "select_crop": "Select area",
        "reset_crop": "Reset crop",
        "crop_x": "X",
        "crop_y": "Y",
        "crop_width": "Width",
        "crop_height": "Height",
        "output_resolution": "Output resolution",
        "original": "Original",
        "custom": "Custom",
        "output_width": "Width (px)",
        "output_height": "Height (px)",
        "output_fps": "Output frame rate",
    },
    "es": {
        "subtitle": "Un editor de video sencillo para Windows",
        "step_import": "1  Seleccionar video",
        "step_edit": "2  Editar",
        "step_export": "3  Exportar",
        "drop_title": "Selecciona un video para comenzar",
        "drop_hint": "Arrastra un video a esta área o examina tus archivos.",
        "browse": "Examinar videos",
        "supported": "Formatos compatibles: MP4, MKV, MOV, AVI, WebM, MPEG-TS y más.",
        "workflow_title": "Un flujo de trabajo sencillo",
        "workflow_1_title": "Selecciona un video",
        "workflow_1_text": "Abre un video de tu computadora o arrástralo a la ventana.",
        "workflow_2_title": "Revisa sus detalles",
        "workflow_2_text": "Consulta la resolución, los FPS, los códecs y el bitrate original.",
        "workflow_3_title": "Prepara la exportación",
        "workflow_3_text": "Ajusta las opciones disponibles antes de exportar.",
        "editor": "Editor de video",
        "editor_subtitle": "Revisa tu video y prepara sus opciones de salida.",
        "change": "Elegir otro video",
        "export": "Exportar video",
        "bitrate": "Bitrate del video",
        "bitrate_help": "Bitrate de la pista de video detectado por FFprobe. Si el contenedor solo proporciona el bitrate total, se estima restando los bitrates de audio conocidos.",
        "bitrate_estimated": "Estimado a partir del bitrate del contenedor y las pistas de audio conocidas.",
        "bitrate_unavailable": "No disponible",
        "ffprobe_missing": "No se encontró FFprobe. Instala FFmpeg y añade su carpeta bin al PATH.",
        "settings": "Configuración de salida",
        "back": "Volver al inicio",
        "file_details": "Información del video",
        "preview": "Vista previa",
        "file_name": "Nombre del archivo",
        "location": "Ubicación",
        "duration": "Duración",
        "resolution": "Resolución",
        "fps": "Fotogramas por segundo",
        "video_codec": "Códec de video",
        "audio_codec": "Códec de audio",
        "file_size": "Tamaño del archivo",
        "sample_rate": "Frecuencia de audio",
        "channels": "Canales de audio",
        "no_audio": "Sin pista de audio",
        "export_disabled": "El motor de exportación todavía no está implementado.",
        "play_error": "No se pudo reproducir este video:",
        "coming": "Selecciona un video para reproducirlo aquí.",
        "unsupported": "El archivo no es un video compatible o FFprobe no pudo leer una pista de video.",
        "invalid_path": "La ruta seleccionada no corresponde a un archivo válido.",
        "metadata_error": "No se pudo leer la información del video. El archivo podría estar dañado o usar un códec no compatible.",
        "estimated": "Aprox.",
        "timeline_hint": "Arrastra los controles azules para elegir inicio y final. Arrastra el marcador blanco para avanzar.",
        "trim": "Duración del fragmento",
        "trim_start": "Inicio (segundos)",
        "trim_end": "Final (segundos)",
        "trim_hint": "La reproducción se detendrá en el punto final seleccionado.",
        "crop": "Área de recorte",
        "crop_hint": "Arrastra sobre el video para recortar; arrastra dentro para mover y usa los puntos para ajustar.",
        "select_crop": "Seleccionar área",
        "reset_crop": "Restablecer recorte",
        "crop_x": "X",
        "crop_y": "Y",
        "crop_width": "Ancho",
        "crop_height": "Alto",
        "output_resolution": "Resolución de salida",
        "original": "Original",
        "custom": "Personalizada",
        "output_width": "Ancho (px)",
        "output_height": "Alto (px)",
        "output_fps": "Fotogramas por segundo de salida",
    },
    "ru": {
        "subtitle": "Простой видеоредактор для Windows",
        "step_import": "1  Выбрать видео",
        "step_edit": "2  Изменить",
        "step_export": "3  Экспорт",
        "drop_title": "Выберите видео, чтобы начать",
        "drop_hint": "Перетащите видео в эту область или выберите файл.",
        "browse": "Выбрать видео",
        "supported": "Поддерживаемые форматы: MP4, MKV, MOV, AVI, WebM, MPEG-TS и другие.",
        "workflow_title": "Простой рабочий процесс",
        "workflow_1_title": "Выберите видео",
        "workflow_1_text": "Откройте видео на компьютере или перетащите его в окно.",
        "workflow_2_title": "Проверьте сведения",
        "workflow_2_text": "Посмотрите разрешение, частоту кадров, кодеки и исходный битрейт.",
        "workflow_3_title": "Подготовьте экспорт",
        "workflow_3_text": "Настройте доступные параметры перед экспортом.",
        "editor": "Видеоредактор",
        "editor_subtitle": "Просмотрите видео и подготовьте параметры вывода.",
        "change": "Выбрать другое видео",
        "export": "Экспортировать видео",
        "bitrate": "Битрейт видео",
        "bitrate_help": "Битрейт видеопотока, определённый FFprobe. Если контейнер содержит только общий битрейт, значение оценивается за вычетом известных битрейтов аудио.",
        "bitrate_estimated": "Оценка по общему битрейту контейнера и известным аудиопотокам.",
        "bitrate_unavailable": "Недоступно",
        "ffprobe_missing": "FFprobe не найден. Установите FFmpeg и добавьте папку bin в PATH.",
        "settings": "Настройки вывода",
        "back": "На главную",
        "file_details": "Информация о видео",
        "preview": "Предпросмотр",
        "file_name": "Имя файла",
        "location": "Расположение",
        "duration": "Длительность",
        "resolution": "Разрешение",
        "fps": "Частота кадров",
        "video_codec": "Видеокодек",
        "audio_codec": "Аудиокодек",
        "file_size": "Размер файла",
        "sample_rate": "Частота аудио",
        "channels": "Аудиоканалы",
        "no_audio": "Нет аудиопотока",
        "export_disabled": "Модуль экспорта ещё не реализован.",
        "play_error": "Не удалось воспроизвести видео:",
        "coming": "Выберите видео для предварительного просмотра.",
        "unsupported": "Файл не является поддерживаемым видео или FFprobe не смог прочитать видеопоток.",
        "invalid_path": "Выбранный путь не является допустимым файлом.",
        "metadata_error": "Не удалось прочитать сведения о видео. Файл может быть повреждён или использовать неподдерживаемый кодек.",
        "estimated": "Прибл.",
        "timeline_hint": "Перетаскивайте синие маркеры, чтобы выбрать начало и конец. Белый маркер перемещает позицию.",
        "trim": "Обрезка по времени",
        "trim_start": "Начало (секунды)",
        "trim_end": "Конец (секунды)",
        "trim_hint": "Воспроизведение остановится в выбранной конечной точке.",
        "crop": "Обрезка кадра",
        "crop_hint": "Перетащите мышью по видео; перемещайте область внутри и меняйте размер за маркеры.",
        "select_crop": "Выбрать область",
        "reset_crop": "Сбросить обрезку",
        "crop_x": "X",
        "crop_y": "Y",
        "crop_width": "Ширина",
        "crop_height": "Высота",
        "output_resolution": "Разрешение вывода",
        "original": "Исходное",
        "custom": "Пользовательское",
        "output_width": "Ширина (px)",
        "output_height": "Высота (px)",
        "output_fps": "Частота кадров на выходе",
    },
}


def windows_theme():
    if sys.platform == "win32":
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "light" if value else "dark"
        except OSError:
            pass

    return "dark" if QApplication.palette().window().color().lightness() < 128 else "light"


def windows_language():
    locale_name = QLocale.system().name().lower()

    if locale_name.startswith("es"):
        return "es"

    if locale_name.startswith("ru"):
        return "ru"

    return "en"

def stylesheet(theme):
    if theme == "dark":
        bg = "#202020"
        panel = "#252525"
        card = "#2d2d2d"
        text = "#f5f5f5"
        muted = "#b8b8b8"
        border = "#3d3d3d"
        hover = "#383838"
    else:
        bg = "#f3f3f3"
        panel = "#ffffff"
        card = "#ffffff"
        text = "#202020"
        muted = "#666666"
        border = "#e5e5e5"
        hover = "#eeeeee"

    return f"""
    QWidget {{
        background: {bg};
        color: {text};
        font-family: "Segoe UI Variable", "Segoe UI";
        font-size: 10pt;
    }}

    QMainWindow {{
        background: {bg};
    }}

    QLabel {{
        background: transparent;
        border: none;
    }}

    QLabel#Title {{
        background: transparent;
        font-size: 22pt;
        font-weight: 600;
    }}

    QLabel#Subtitle {{
        background: transparent;
        color: {muted};
        font-size: 10.5pt;
    }}

    QLabel#Muted {{
        background: transparent;
        color: {muted};
    }}

    QLabel#InfoValue {{
        background: transparent;
        font-size: 10pt;
        font-weight: 600;
    }}

    QLabel#SectionTitle {{
        background: transparent;
        font-size: 12pt;
        font-weight: 650;
    }}

    QLabel#StepActive {{
        background: #0067c0;
        color: white;
        border-radius: 8px;
        padding: 9px 14px;
        font-weight: 600;
    }}

    QLabel#StepInactive {{
        background: {panel};
        color: {muted};
        border: 1px solid {border};
        border-radius: 8px;
        padding: 9px 14px;
    }}

    QFrame#Card {{
        background: {card};
        border: 1px solid {border};
        border-radius: 12px;
    }}

    QFrame#DropZone {{
        background: {panel};
        border: 2px dashed {border};
        border-radius: 16px;
    }}

    QFrame#WorkflowCard {{
        background: {panel};
        border: 1px solid {border};
        border-radius: 10px;
    }}

    QPushButton {{
        background: {card};
        border: 1px solid {border};
        border-radius: 7px;
        padding: 10px 16px;
    }}

    QPushButton:hover {{
        background: {hover};
    }}

    QPushButton#Primary {{
        background: #0067c0;
        color: white;
        border: 1px solid #0067c0;
        font-weight: 600;
    }}

    QPushButton#Primary:hover {{
        background: #1976c9;
    }}

    QPushButton:disabled {{
        color: {muted};
    }}

    QDoubleSpinBox {{
        background: {panel};
        border: 1px solid {border};
        border-radius: 6px;
        padding: 7px;
        min-width: 130px;
    }}

    QSlider::groove:horizontal {{
        height: 5px;
        background: #777777;
        border-radius: 2px;
    }}

    QSlider::sub-page:horizontal {{
        background: #0078d4;
        border-radius: 2px;
    }}

    QSlider::handle:horizontal {{
        background: white;
        border: 1px solid #0078d4;
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }}

    QScrollArea {{
        background: transparent;
        border: none;
    }}

    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}

    QStatusBar {{
        background: {bg};
        color: {muted};
    }}
    """

def format_duration(seconds):
    try:
        seconds = int(float(seconds))
    except (ValueError, TypeError):
        return "—"

    if seconds < 0:
        return "—"

    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    return f"{hours:02}:{minutes:02}:{secs:02}" if hours else f"{minutes:02}:{secs:02}"


def format_size(size):
    try:
        size = float(size)
    except (ValueError, TypeError):
        return "—"

    if size < 0:
        return "—"

    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024

    return "—"


def parse_rate(value):
    if not value:
        return None

    try:
        if isinstance(value, str) and "/" in value:
            numerator, denominator = value.split("/", 1)
            denominator = float(denominator)
            result = float(numerator) / denominator if denominator else 0
        else:
            result = float(value)

        return result if result > 0 else None

    except (ValueError, TypeError, ZeroDivisionError):
        return None


def format_fps(value):
    result = parse_rate(value)
    return f"{result:.2f} FPS" if result is not None else "—"


def bitrate_mbps(value):
    try:
        parsed = float(value)
    except (ValueError, TypeError):
        return None

    return parsed / 1_000_000 if parsed > 0 else None


class DropZone(QFrame):
    file_dropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()

            if path:
                self.file_dropped.emit(path)
                event.acceptProposedAction()
                return

        event.ignore()



class TimelineRangeSlider(QWidget):
    """Single timeline with playback thumb and draggable trim boundaries."""

    positionRequested = Signal(int)
    trimRangeChanged = Signal(int, int)
    seekStarted = Signal()
    seekFinished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.duration_ms = 0
        self.position_ms = 0
        self.trim_start_ms = 0
        self.trim_end_ms = 0
        self._drag_mode = None
        self._minimum_gap_ms = 100
        self.setMinimumHeight(32)
        self.setMinimumWidth(180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Drag the blue handles to trim; drag the playhead to seek.")

    def _track_bounds(self):
        left = 10.0
        right = max(left + 1.0, float(self.width()) - 10.0)
        return left, right

    def _x_for_time(self, value):
        left, right = self._track_bounds()
        if self.duration_ms <= 0:
            return left
        ratio = max(0.0, min(1.0, value / self.duration_ms))
        return left + (right - left) * ratio

    def _time_for_x(self, x):
        left, right = self._track_bounds()
        if self.duration_ms <= 0 or right <= left:
            return 0
        ratio = max(0.0, min(1.0, (x - left) / (right - left)))
        return int(round(ratio * self.duration_ms))

    def set_duration(self, duration_ms):
        self.duration_ms = max(0, int(duration_ms))
        if self.duration_ms <= 0:
            self.trim_start_ms = 0
            self.trim_end_ms = 0
            self.position_ms = 0
        else:
            self.trim_start_ms = min(self.trim_start_ms, max(0, self.duration_ms - self._minimum_gap_ms))
            if self.trim_end_ms <= 0 or self.trim_end_ms > self.duration_ms:
                self.trim_end_ms = self.duration_ms
            self.trim_end_ms = max(self.trim_start_ms + min(self._minimum_gap_ms, self.duration_ms), self.trim_end_ms)
            self.trim_end_ms = min(self.trim_end_ms, self.duration_ms)
            self.position_ms = min(self.position_ms, self.duration_ms)
        self.update()

    def set_trim_range(self, start_ms, end_ms):
        if self.duration_ms <= 0:
            self.trim_start_ms = 0
            self.trim_end_ms = 0
            self.update()
            return
        minimum_gap = min(self._minimum_gap_ms, self.duration_ms)
        start_ms = max(0, min(int(start_ms), self.duration_ms - minimum_gap))
        end_ms = max(start_ms + minimum_gap, min(int(end_ms), self.duration_ms))
        self.trim_start_ms = start_ms
        self.trim_end_ms = end_ms
        self.position_ms = max(start_ms, min(self.position_ms, end_ms))
        self.update()

    def set_position(self, position_ms):
        self.position_ms = max(0, min(int(position_ms), self.duration_ms))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        left, right = self._track_bounds()
        center_y = self.height() / 2.0
        track_height = 6.0
        start_x = self._x_for_time(self.trim_start_ms)
        end_x = self._x_for_time(self.trim_end_ms)
        playhead_x = self._x_for_time(self.position_ms)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(125, 135, 150, 105))
        painter.drawRoundedRect(
            QRectF(left, center_y - track_height / 2, right - left, track_height),
            3, 3
        )

        if self.duration_ms > 0:
            painter.setBrush(QColor(0, 120, 212, 225))
            painter.drawRoundedRect(
                QRectF(start_x, center_y - track_height / 2,
                       max(1.0, end_x - start_x), track_height),
                3, 3
            )

            # Trim boundary handles. The tall grips are distinct from the playhead.
            handle_color = QColor(0, 103, 192)
            painter.setBrush(handle_color)
            painter.drawRoundedRect(
                QRectF(start_x - 4, center_y - 10, 8, 20), 3, 3
            )
            painter.drawRoundedRect(
                QRectF(end_x - 4, center_y - 10, 8, 20), 3, 3
            )

            # Playback position marker.
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawLine(
                int(playhead_x), int(center_y - 11),
                int(playhead_x), int(center_y + 11)
            )
            painter.setPen(QPen(QColor(0, 103, 192), 1.5))
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(QRectF(playhead_x - 4.5, center_y - 4.5, 9, 9))

        painter.end()

    def mousePressEvent(self, event):
        if not self.isEnabled() or self.duration_ms <= 0 or event.button() != Qt.LeftButton:
            event.ignore()
            return

        x = event.position().x()
        start_x = self._x_for_time(self.trim_start_ms)
        end_x = self._x_for_time(self.trim_end_ms)

        # Prefer trim handles when the click is close to one; everywhere else seeks.
        if abs(x - start_x) <= 10:
            self._drag_mode = "trim_start"
        elif abs(x - end_x) <= 10:
            self._drag_mode = "trim_end"
        else:
            self._drag_mode = "playhead"
            self.seekStarted.emit()
            self._request_seek(x)

        event.accept()

    def mouseMoveEvent(self, event):
        if not self._drag_mode:
            event.ignore()
            return

        x = event.position().x()
        value = self._time_for_x(x)

        if self._drag_mode == "trim_start":
            maximum = max(0, self.trim_end_ms - min(self._minimum_gap_ms, self.duration_ms))
            new_start = min(value, maximum)
            if new_start != self.trim_start_ms:
                self.trim_start_ms = new_start
                self.position_ms = max(self.position_ms, self.trim_start_ms)
                self.trimRangeChanged.emit(self.trim_start_ms, self.trim_end_ms)
                self.update()
        elif self._drag_mode == "trim_end":
            minimum = self.trim_start_ms + min(self._minimum_gap_ms, self.duration_ms)
            new_end = max(value, minimum)
            new_end = min(new_end, self.duration_ms)
            if new_end != self.trim_end_ms:
                self.trim_end_ms = new_end
                self.position_ms = min(self.position_ms, self.trim_end_ms)
                self.trimRangeChanged.emit(self.trim_start_ms, self.trim_end_ms)
                self.update()
        else:
            self._request_seek(x)

        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._drag_mode:
            was_seeking = self._drag_mode == "playhead"
            self._drag_mode = None
            if was_seeking:
                self.seekFinished.emit()
            event.accept()
        else:
            event.ignore()

    def _request_seek(self, x):
        value = self._time_for_x(x)
        value = max(self.trim_start_ms, min(value, self.trim_end_ms))
        self.position_ms = value
        self.positionRequested.emit(value)
        self.update()



class CropSelectionOverlay(QWidget):
    crop_changed = Signal(int, int, int, int)

    HANDLE_SIZE = 9.0
    MIN_SELECTION_SIZE = 16.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_width = 0
        self.source_height = 0
        self.crop_rect_source = None
        self.selection_enabled = False
        self._drag_mode = None
        self._drag_origin = None
        self._initial_rect = None
        self._working_rect = None
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent; border: none;")
        self.setMouseTracking(True)
        self.hide()

    def set_source_size(self, width, height):
        self.source_width = max(0, int(width or 0))
        self.source_height = max(0, int(height or 0))
        self.update()

    def set_crop_rect(self, x=None, y=None, width=None, height=None):
        if None in (x, y, width, height):
            self.crop_rect_source = None
        else:
            self.crop_rect_source = (
                int(x), int(y), int(width), int(height)
            )
        self.update()

    def set_selection_enabled(self, enabled):
        self.selection_enabled = bool(enabled)
        self.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            not self.selection_enabled
        )
        self.setCursor(
            Qt.CrossCursor if self.selection_enabled else Qt.ArrowCursor
        )
        self.setVisible(self.selection_enabled)
        if self.selection_enabled:
            self.raise_()
        self.update()

    def _content_rect(self):
        if self.source_width <= 0 or self.source_height <= 0:
            return QRectF(self.rect())
        bounds = QRectF(self.rect())
        scale = min(
            bounds.width() / self.source_width,
            bounds.height() / self.source_height
        )
        width = self.source_width * scale
        height = self.source_height * scale
        return QRectF(
            (bounds.width() - width) / 2,
            (bounds.height() - height) / 2,
            width,
            height
        )

    def _source_rect_to_widget(self, crop):
        if not crop or not self.source_width or not self.source_height:
            return QRectF()
        x, y, width, height = crop
        content = self._content_rect()
        return QRectF(
            content.left() + x / self.source_width * content.width(),
            content.top() + y / self.source_height * content.height(),
            width / self.source_width * content.width(),
            height / self.source_height * content.height()
        )

    def _widget_rect_to_source(self, rect):
        content = self._content_rect()
        rect = rect.normalized().intersected(content)
        if rect.isEmpty() or content.isEmpty():
            return None

        sw, sh = self.source_width, self.source_height
        x = int(round((rect.left() - content.left()) / content.width() * sw))
        y = int(round((rect.top() - content.top()) / content.height() * sh))
        width = int(round(rect.width() / content.width() * sw))
        height = int(round(rect.height() / content.height() * sh))

        # Even coordinates and dimensions are compatible with common 4:2:0 codecs.
        x = max(0, x - (x % 2))
        y = max(0, y - (y % 2))
        width = max(0, width - (width % 2))
        height = max(0, height - (height % 2))
        width = min(width, (sw - x) - ((sw - x) % 2))
        height = min(height, (sh - y) - ((sh - y) % 2))

        if width < 16 or height < 16:
            return None
        return x, y, width, height

    def _handle_points(self, rect):
        cx = rect.center().x()
        cy = rect.center().y()
        return {
            "nw": rect.topLeft(), "n": QPointF(cx, rect.top()),
            "ne": rect.topRight(), "e": QPointF(rect.right(), cy),
            "se": rect.bottomRight(), "s": QPointF(cx, rect.bottom()),
            "sw": rect.bottomLeft(), "w": QPointF(rect.left(), cy),
        }

    def _hit_handle(self, point, rect):
        limit = 11.0
        for name, handle_point in self._handle_points(rect).items():
            dx = point.x() - handle_point.x()
            dy = point.y() - handle_point.y()
            if dx * dx + dy * dy <= limit * limit:
                return name
        return None

    def _clamp_rect(self, rect, content):
        rect = QRectF(rect)
        if rect.width() > content.width():
            rect.setWidth(content.width())
        if rect.height() > content.height():
            rect.setHeight(content.height())
        if rect.left() < content.left():
            rect.moveLeft(content.left())
        if rect.top() < content.top():
            rect.moveTop(content.top())
        if rect.right() > content.right():
            rect.moveRight(content.right())
        if rect.bottom() > content.bottom():
            rect.moveBottom(content.bottom())
        return rect

    def paintEvent(self, event):
        if not self.selection_enabled or self.source_width <= 0 or self.source_height <= 0:
            return

        content = self._content_rect()
        if content.isEmpty():
            return

        current_rect = self._working_rect
        if current_rect is None and self.crop_rect_source:
            current_rect = self._source_rect_to_widget(self.crop_rect_source)
        if current_rect is None or current_rect.isEmpty():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        shade = QColor(0, 0, 0, 115)
        painter.fillRect(QRectF(content.left(), content.top(), content.width(), max(0, current_rect.top() - content.top())), shade)
        painter.fillRect(QRectF(content.left(), current_rect.bottom(), content.width(), max(0, content.bottom() - current_rect.bottom())), shade)
        painter.fillRect(QRectF(content.left(), current_rect.top(), max(0, current_rect.left() - content.left()), current_rect.height()), shade)
        painter.fillRect(QRectF(current_rect.right(), current_rect.top(), max(0, content.right() - current_rect.right()), current_rect.height()), shade)

        painter.setPen(QPen(QColor(255, 255, 255, 230), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(current_rect)

        handle_color = QColor(30, 145, 235)
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setBrush(handle_color)
        half = self.HANDLE_SIZE / 2
        for point in self._handle_points(current_rect).values():
            painter.drawRoundedRect(
                QRectF(point.x() - half, point.y() - half,
                       self.HANDLE_SIZE, self.HANDLE_SIZE),
                2, 2
            )
        painter.end()

    def mousePressEvent(self, event):
        if not self.selection_enabled or event.button() != Qt.LeftButton:
            event.ignore()
            return

        point = event.position()
        content = self._content_rect()
        if not content.contains(point):
            event.ignore()
            return

        current = self._source_rect_to_widget(self.crop_rect_source) if self.crop_rect_source else None
        self._drag_origin = point
        self._initial_rect = QRectF(current) if current and not current.isEmpty() else None

        if self._initial_rect is not None:
            handle = self._hit_handle(point, self._initial_rect)
            if handle:
                self._drag_mode = handle
            elif self._initial_rect.contains(point):
                self._drag_mode = "move"
            else:
                self._drag_mode = "new"
        else:
            self._drag_mode = "new"

        if self._drag_mode == "new":
            self._working_rect = QRectF(point, point)
        else:
            self._working_rect = QRectF(self._initial_rect)

        self.update()
        event.accept()

    def mouseMoveEvent(self, event):
        if not self.selection_enabled or self._drag_mode is None:
            event.ignore()
            return

        point = event.position()
        content = self._content_rect()
        mode = self._drag_mode

        if mode == "new":
            self._working_rect = QRectF(self._drag_origin, point).normalized().intersected(content)
        elif mode == "move":
            dx = point.x() - self._drag_origin.x()
            dy = point.y() - self._drag_origin.y()
            moved = QRectF(self._initial_rect)
            moved.translate(dx, dy)
            self._working_rect = self._clamp_rect(moved, content)
        else:
            rect = QRectF(self._initial_rect)
            left, top = rect.left(), rect.top()
            right, bottom = rect.right(), rect.bottom()
            minimum = self.MIN_SELECTION_SIZE

            if "w" in mode:
                left = max(content.left(), min(point.x(), right - minimum))
            if "e" in mode:
                right = min(content.right(), max(point.x(), left + minimum))
            if "n" in mode:
                top = max(content.top(), min(point.y(), bottom - minimum))
            if "s" in mode:
                bottom = min(content.bottom(), max(point.y(), top + minimum))

            self._working_rect = QRectF(left, top, right - left, bottom - top)

        self.update()
        event.accept()

    def mouseReleaseEvent(self, event):
        if not self.selection_enabled or event.button() != Qt.LeftButton or self._drag_mode is None:
            event.ignore()
            return

        selected = self._widget_rect_to_source(self._working_rect) if self._working_rect else None
        self._drag_mode = None
        self._drag_origin = None
        self._initial_rect = None
        self._working_rect = None

        if selected:
            self.crop_rect_source = selected
            self.crop_changed.emit(*selected)
        self.update()
        event.accept()


class VideoPreviewWidget(QVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._preview_pixmap = None
        # Kept as a sibling of QVideoWidget by AspectRatioContainer.
        # Child widgets over native video surfaces can cause black artifacts.
        self.overlay = QLabel()
        self.overlay.setAlignment(Qt.AlignCenter)
        self.overlay.setStyleSheet(
            "background: transparent; border: none;"
        )
        self.overlay.setAttribute(
            Qt.WA_TransparentForMouseEvents, True
        )
        self.overlay.hide()


    def show_preview_image(self, image):
        if image.isNull():
            return

        self._preview_pixmap = QPixmap.fromImage(image)
        self._update_preview_overlay()
        self.overlay.show()
        self.overlay.raise_()

    def clear_preview_image(self):
        self._preview_pixmap = None
        self.overlay.clear()
        self.overlay.hide()

    def _update_preview_overlay(self):
        if self._preview_pixmap is None:
            return

        scaled = self._preview_pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.overlay.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_preview_overlay()


class AspectRatioContainer(QWidget):
    """Centers a video widget inside a fixed 16:9 preview canvas."""

    def __init__(self, video_widget, parent=None):
        super().__init__(parent)

        self.video_widget = video_widget
        self.video_widget.setParent(self)

        # Put preview and crop layers beside (not inside) QVideoWidget.
        # QVideoWidget uses a native rendering surface on some systems;
        # child overlays can leave black rectangles/artifacts.
        self.preview_overlay = self.video_widget.overlay
        self.preview_overlay.setParent(self)

        self.setMinimumSize(480, 270)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)

        area = self.contentsRect()
        available_width = area.width()
        available_height = area.height()

        if available_width <= 0 or available_height <= 0:
            return

        # Fit a 16:9 canvas inside the available space.
        canvas_width = available_width
        canvas_height = round(canvas_width * 9 / 16)

        if canvas_height > available_height:
            canvas_height = available_height
            canvas_width = round(canvas_height * 16 / 9)

        x = area.x() + (available_width - canvas_width) // 2
        y = area.y() + (available_height - canvas_height) // 2

        video_rect = QRect(x, y, canvas_width, canvas_height)
        self.video_widget.setGeometry(video_rect)
        self.preview_overlay.setGeometry(video_rect)

        if self.preview_overlay.isVisible():
            self.preview_overlay.raise_()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.language = windows_language()
        self.t = STRINGS[self.language]
        self.theme = windows_theme()
        self.current_file = None
        self.last_directory = str(Path.home())
        self.video_metadata = {}
        self.source_width = 0
        self.source_height = 0
        self.source_duration_ms = 0
        self.trim_end_tracks_source = True
        self.seeking = False
        self.export_process = None
        self.export_progress = None
        self.export_output_path = None
        self.export_duration_seconds = 0.0
        self.export_stdout_buffer = ""
        self.export_stderr_buffer = ""

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1080, 720)

        # Restore the last window size and position, including maximized/fullscreen mode.
        self.window_settings = QSettings("Shink", "VideoEditor")
        saved_geometry = self.window_settings.value("window/geometry")
        if saved_geometry and not self.restoreGeometry(saved_geometry):
            self.resize(1440, 900)
        elif not saved_geometry:
            self.resize(1440, 900)
        self._saved_window_mode = self.window_settings.value(
            "window/mode", "normal", type=str
        )
        self.setAcceptDrops(True)
        self.setStyleSheet(stylesheet(self.theme))

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.stack.addWidget(self.build_import_page())
        self.stack.addWidget(self.build_editor_page())

        self.statusBar().showMessage(
            f"{self.theme.title()} theme  •  {self.language.upper()}  •  v{APP_VERSION}"
        )


    def show_saved_window_mode(self):
        if self._saved_window_mode == "fullscreen":
            self.showFullScreen()
        elif self._saved_window_mode == "maximized":
            self.showMaximized()
        else:
            self.showNormal()

    def closeEvent(self, event):
        if self.export_process and self.export_process.state() != QProcess.ProcessState.NotRunning:
            self.export_process.kill()
            self.export_process.waitForFinished(1500)
        # saveGeometry stores the normal window geometry even when maximized.
        self.window_settings.setValue("window/geometry", self.saveGeometry())
        if self.isFullScreen():
            mode = "fullscreen"
        elif self.isMaximized():
            mode = "maximized"
        else:
            mode = "normal"
        self.window_settings.setValue("window/mode", mode)
        self.window_settings.sync()
        super().closeEvent(event)

    def build_import_page(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(42, 34, 42, 30)
        outer.setSpacing(18)
        heading = QVBoxLayout()
        heading.setSpacing(4)

        title = QLabel(APP_NAME)
        title.setObjectName("Title")

        subtitle = QLabel(self.t["subtitle"])
        subtitle.setObjectName("Subtitle")

        heading.addWidget(title)
        heading.addWidget(subtitle)
        outer.addLayout(heading)

        zone = DropZone()
        zone.file_dropped.connect(self.import_file)

        zlayout = QVBoxLayout(zone)
        zlayout.setContentsMargins(48, 34, 48, 34)
        zlayout.setSpacing(12)
        zlayout.addStretch(1)

        glyph = QLabel("＋")
        glyph.setAlignment(Qt.AlignCenter)
        glyph.setStyleSheet(
            "font-size: 48pt; color: #1683d8; background: transparent;"
        )
        zlayout.addWidget(glyph)

        drop_title = QLabel(self.t["drop_title"])
        drop_title.setAlignment(Qt.AlignCenter)
        drop_title.setStyleSheet(
            "font-size: 21pt; font-weight: 650; background: transparent;"
        )
        zlayout.addWidget(drop_title)

        hint = QLabel(self.t["drop_hint"])
        hint.setObjectName("Muted")
        hint.setAlignment(Qt.AlignCenter)
        zlayout.addWidget(hint)

        zlayout.addSpacing(8)

        browse = QPushButton(self.t["browse"])
        browse.setObjectName("Primary")
        browse.setCursor(Qt.PointingHandCursor)
        browse.setMinimumWidth(190)
        browse.clicked.connect(self.browse_file)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(browse)
        button_row.addStretch(1)
        zlayout.addLayout(button_row)
        zlayout.addStretch(1)

        outer.addWidget(zone, 5)

        supported = QLabel(self.t["supported"])
        supported.setObjectName("Muted")
        outer.addWidget(supported)

        return page

    def build_editor_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(34, 22, 34, 24)
        layout.setSpacing(14)
        header = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(3)

        title = QLabel(self.t["editor"])
        title.setObjectName("Title")

        subtitle = QLabel(self.t["editor_subtitle"])
        subtitle.setObjectName("Subtitle")

        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header.addLayout(header_text, 1)

        change = QPushButton(self.t["change"])
        change.clicked.connect(self.browse_file)
        header.addWidget(change, 0, Qt.AlignVCenter)
        layout.addLayout(header)

        # File identity card
        identity_card = QFrame()
        identity_card.setObjectName("Card")

        identity_layout = QHBoxLayout(identity_card)
        identity_layout.setContentsMargins(18, 12, 18, 12)
        identity_layout.setSpacing(28)

        name_col = QVBoxLayout()
        name_col.setSpacing(4)

        name_label = QLabel(self.t["file_name"])
        name_label.setObjectName("Muted")

        self.file_name = QLabel("—")
        self.file_name.setObjectName("InfoValue")
        self.file_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.file_name.setWordWrap(True)

        name_col.addWidget(name_label)
        name_col.addWidget(self.file_name)
        identity_layout.addLayout(name_col, 1)

        path_col = QVBoxLayout()
        path_col.setSpacing(4)

        path_label = QLabel(self.t["location"])
        path_label.setObjectName("Muted")

        self.file_path = QLabel("—")
        self.file_path.setObjectName("InfoValue")
        self.file_path.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.file_path.setWordWrap(True)
        self.file_path.setToolTip("")

        path_col.addWidget(path_label)
        path_col.addWidget(self.file_path)
        identity_layout.addLayout(path_col, 2)

        layout.addWidget(identity_card)

        # Metadata card: multiple columns use the desktop width.
        metadata_card = QFrame()
        metadata_card.setObjectName("Card")

        metadata_layout = QVBoxLayout(metadata_card)
        metadata_layout.setContentsMargins(18, 12, 18, 14)
        metadata_layout.setSpacing(10)

        metadata_title = QLabel(self.t["file_details"])
        metadata_title.setObjectName("SectionTitle")
        metadata_layout.addWidget(metadata_title)

        self.metadata_labels = {}

        metadata_grid = QGridLayout()
        metadata_grid.setHorizontalSpacing(28)
        metadata_grid.setVerticalSpacing(12)

        metadata_items = [
            "duration", "resolution", "fps", "video_codec", "audio_codec",
            "bitrate", "file_size", "sample_rate", "channels"
        ]

        for index, key in enumerate(metadata_items):
            row, column = divmod(index, 5)

            cell = QVBoxLayout()
            cell.setSpacing(4)

            label = QLabel(self.t[key])
            label.setObjectName("Muted")
            label.setWordWrap(True)

            value = QLabel("—")
            value.setObjectName("InfoValue")
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            value.setWordWrap(True)

            cell.addWidget(label)
            cell.addWidget(value)
            metadata_grid.addLayout(cell, row, column)
            self.metadata_labels[key] = value

        for column in range(5):
            metadata_grid.setColumnStretch(column, 1)

        metadata_layout.addLayout(metadata_grid)
        layout.addWidget(metadata_card)

        # Main workspace: wide preview at left, settings at right.
        workspace = QHBoxLayout()
        workspace.setSpacing(14)

        preview_card = QFrame()
        preview_card.setObjectName("Card")
        preview_card.setMinimumWidth(0)

        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(14, 12, 14, 12)
        preview_layout.setSpacing(10)

        preview_title = QLabel(self.t["preview"])
        preview_title.setObjectName("SectionTitle")
        preview_layout.addWidget(preview_title)

        self.video_widget = VideoPreviewWidget()
        self.video_widget.setMinimumSize(0, 0)
        self.video_widget.setSizePolicy(
            QSizePolicy.Ignored,
            QSizePolicy.Ignored
        )
        self.video_widget.setStyleSheet(
            "background-color: #080808; border-radius: 8px;"
        )

        self.preview_canvas = AspectRatioContainer(
            self.video_widget
        )
        preview_layout.addWidget(self.preview_canvas, 1)

        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(44, 38)
        self.play_button.setEnabled(False)
        self.play_button.setToolTip("Play / Pause")
        self.play_button.clicked.connect(self.toggle_playback)

        self.position_slider = TimelineRangeSlider()
        self.position_slider.setToolTip(self.t["timeline_hint"])
        self.position_slider.setEnabled(False)
        self.position_slider.positionRequested.connect(self.seek_to_position)
        self.position_slider.trimRangeChanged.connect(self.on_trim_range_changed)
        self.position_slider.seekStarted.connect(self.begin_seek)
        self.position_slider.seekFinished.connect(self.finish_seek)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setObjectName("Muted")
        self.time_label.setMinimumWidth(112)
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        controls.addWidget(self.play_button)
        controls.addWidget(self.position_slider, 1)
        controls.addWidget(self.time_label)
        preview_layout.addLayout(controls)

        workspace.addWidget(preview_card, 7)

        settings_card = QFrame()
        settings_card.setObjectName("Card")
        settings_card.setMinimumWidth(300)
        settings_card.setMaximumWidth(420)

        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(18, 16, 18, 16)
        settings_layout.setSpacing(12)

        settings_title = QLabel(self.t["settings"])
        settings_title.setObjectName("SectionTitle")
        settings_layout.addWidget(settings_title)

        # Trim values are kept internally; the user edits them with the
        # two handles on the playback timeline below the preview.
        self.trim_start_input = QDoubleSpinBox(self)
        self.trim_start_input.setRange(0.0, 86400.0)
        self.trim_start_input.setDecimals(2)
        self.trim_start_input.setSingleStep(0.1)
        self.trim_start_input.setSuffix(" s")
        self.trim_start_input.hide()

        self.trim_end_input = QDoubleSpinBox(self)
        self.trim_end_input.setRange(0.1, 86400.0)
        self.trim_end_input.setDecimals(2)
        self.trim_end_input.setSingleStep(0.1)
        self.trim_end_input.setSuffix(" s")
        self.trim_end_input.hide()

        self.trim_start_input.valueChanged.connect(self.on_trim_start_changed)
        self.trim_end_input.valueChanged.connect(self.on_trim_end_changed)

        # Output resolution controls
        resolution_title_row = QHBoxLayout()
        resolution_title = QLabel(self.t["output_resolution"])
        resolution_title.setObjectName("SectionTitle")
        resolution_title_row.addWidget(resolution_title)
        resolution_title_row.addStretch(1)
        self.reset_resolution_button = self.make_reset_button(
            "Restablecer la resolución original" if self.language == "es" else
            "Reset to original resolution"
        )
        self.reset_resolution_button.clicked.connect(self.reset_resolution_to_source)
        resolution_title_row.addWidget(self.reset_resolution_button)
        settings_layout.addLayout(resolution_title_row)

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItem(self.t["original"], "original")
        for resolution in (
            "3840x2160", "2560x1440", "1920x1080",
            "1280x720", "854x480"
        ):
            self.resolution_combo.addItem(
                resolution.replace("x", " × "), resolution
            )
        self.resolution_combo.addItem(self.t["custom"], "custom")
        settings_layout.addWidget(self.resolution_combo)

        self.source_resolution_label = QLabel("—")
        self.source_resolution_label.setObjectName("Muted")
        self.source_resolution_label.setWordWrap(True)
        settings_layout.addWidget(self.source_resolution_label)

        output_dimensions = QGridLayout()
        output_dimensions.setHorizontalSpacing(8)
        self.output_width_input = QSpinBox()
        self.output_height_input = QSpinBox()
        for field in (self.output_width_input, self.output_height_input):
            field.setRange(16, 16384)
            field.setSingleStep(2)
            field.setKeyboardTracking(False)
        output_dimensions.addWidget(
            QLabel(self.t["output_width"]), 0, 0
        )
        output_dimensions.addWidget(self.output_width_input, 0, 1)
        output_dimensions.addWidget(
            QLabel(self.t["output_height"]), 1, 0
        )
        output_dimensions.addWidget(self.output_height_input, 1, 1)
        settings_layout.addLayout(output_dimensions)
        self.resolution_combo.currentIndexChanged.connect(
            self.on_resolution_preset_changed
        )
        self.output_width_input.valueChanged.connect(
            self.on_output_width_changed
        )
        self.output_height_input.valueChanged.connect(
            self.on_output_height_changed
        )

        # Output frame rate
        fps_title_row = QHBoxLayout()
        fps_title = QLabel(self.t["output_fps"])
        fps_title.setObjectName("SectionTitle")
        fps_title_row.addWidget(fps_title)
        fps_title_row.addStretch(1)
        self.reset_fps_button = self.make_reset_button(
            "Restablecer los FPS originales" if self.language == "es" else
            "Reset to original frame rate"
        )
        self.reset_fps_button.clicked.connect(self.reset_fps_to_source)
        fps_title_row.addWidget(self.reset_fps_button)
        settings_layout.addLayout(fps_title_row)

        self.fps_combo = QComboBox()
        self.fps_combo.addItem(self.t["original"], None)
        for fps_value in ("23.976", "24", "25", "30", "50", "59.94", "60", "120"):
            self.fps_combo.addItem(f"{fps_value} FPS", float(fps_value))
        settings_layout.addWidget(self.fps_combo)

        # Output bitrate
        bitrate_title_row = QHBoxLayout()
        bitrate_title = QLabel(self.t["bitrate"])
        bitrate_title.setObjectName("SectionTitle")
        bitrate_title_row.addWidget(bitrate_title)
        bitrate_title_row.addStretch(1)
        self.reset_bitrate_button = self.make_reset_button(
            "Restablecer el bitrate original" if self.language == "es" else
            "Reset to original bitrate"
        )
        self.reset_bitrate_button.clicked.connect(self.reset_bitrate_to_source)
        bitrate_title_row.addWidget(self.reset_bitrate_button)
        settings_layout.addLayout(bitrate_title_row)

        self.bitrate_input = QDoubleSpinBox()
        self.bitrate_input.setRange(0.0, 500.0)
        self.bitrate_input.setDecimals(2)
        self.bitrate_input.setSingleStep(0.25)
        self.bitrate_input.setSuffix(" Mbps")
        self.bitrate_input.setMinimumWidth(140)
        self.bitrate_input.setSpecialValueText(
            self.t["bitrate_unavailable"]
        )
        settings_layout.addWidget(self.bitrate_input)

        self.bitrate_note = QLabel(self.t["bitrate_help"])
        self.bitrate_note.setObjectName("Muted")
        self.bitrate_note.setWordWrap(True)
        settings_layout.addWidget(self.bitrate_note)

        # Output audio volume (0% mutes; 100% keeps original level).
        volume_title_row = QHBoxLayout()
        volume_title = QLabel("Audio volume" if self.language == "en" else "Volumen del audio" if self.language == "es" else "Громкость аудио")
        volume_title.setObjectName("SectionTitle")
        volume_title_row.addWidget(volume_title)
        volume_title_row.addStretch(1)
        self.reset_volume_button = self.make_reset_button(
            "Restablecer el volumen original" if self.language == "es" else
            "Reset to original volume"
        )
        self.reset_volume_button.clicked.connect(self.reset_volume_to_source)
        volume_title_row.addWidget(self.reset_volume_button)
        settings_layout.addLayout(volume_title_row)
        volume_row = QHBoxLayout()
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 200)
        self.volume_slider.setValue(100)
        self.volume_value_label = QLabel("100%")
        self.volume_value_label.setMinimumWidth(48)
        self.volume_slider.valueChanged.connect(
            lambda value: self.volume_value_label.setText(f"{value}%")
        )
        volume_row.addWidget(self.volume_slider, 1)
        volume_row.addWidget(self.volume_value_label)
        settings_layout.addLayout(volume_row)
        volume_hint = QLabel(
            "0% silences audio · 100% keeps original · 200% doubles it (boost applied on export)"
            if self.language == "en" else
            "0% silencia · 100% mantiene el volumen original · 200% lo duplica (la amplificación se aplica al exportar)"
            if self.language == "es" else
            "0% — без звука · 100% — исходная громкость · 200% — вдвое громче"
        )
        volume_hint.setObjectName("Muted")
        volume_hint.setWordWrap(True)
        settings_layout.addWidget(volume_hint)

        settings_layout.addStretch(1)

        workspace.addWidget(settings_card, 3)
        layout.addLayout(workspace, 1)

        # Multimedia player
        self.audio_output = QAudioOutput(self)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)
        self.volume_slider.valueChanged.connect(self.update_preview_volume)
        self.update_preview_volume(self.volume_slider.value())

        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.playbackStateChanged.connect(self.update_play_button)
        self.player.errorOccurred.connect(self.handle_player_error)

        self.preview_process = QProcess(self)
        self.preview_process.finished.connect(
            self.on_preview_frame_finished
        )
        self.preview_request_path = None

        bottom = QHBoxLayout()

        back = QPushButton("←  " + self.t["back"])
        back.clicked.connect(self.return_to_import)
        bottom.addWidget(back)
        bottom.addStretch(1)

        self.export_button = QPushButton(self.t["export"])
        self.export_button.setObjectName("Primary")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.start_export)
        bottom.addWidget(self.export_button)

        layout.addLayout(bottom)

        scroll.setWidget(page)
        return scroll

    # Editing controls: these values are prepared for the FFmpeg export stage.
    def on_trim_start_changed(self, value):
        duration = max(0.1, self.source_duration_ms / 1000.0)
        minimum_end = min(duration, value + 0.1)
        self.trim_end_input.setMinimum(minimum_end)
        if self.trim_end_input.value() < minimum_end:
            blocker = QSignalBlocker(self.trim_end_input)
            self.trim_end_input.setValue(minimum_end)
            del blocker
            self.trim_end_tracks_source = False
        self.apply_trim_range()

    def on_trim_end_changed(self, value):
        maximum_start = max(0.0, value - 0.1)
        self.trim_start_input.setMaximum(maximum_start)
        if self.trim_start_input.value() > maximum_start:
            blocker = QSignalBlocker(self.trim_start_input)
            self.trim_start_input.setValue(maximum_start)
            del blocker
        self.trim_end_tracks_source = False
        self.apply_trim_range()

    def on_trim_range_changed(self, start_ms, end_ms):
        duration_ms = max(0, self.source_duration_ms)
        minimum_gap = min(100, duration_ms)
        start_ms = max(0, min(int(start_ms), max(0, duration_ms - minimum_gap)))
        end_ms = max(start_ms + minimum_gap, min(int(end_ms), duration_ms))

        start_blocker = QSignalBlocker(self.trim_start_input)
        end_blocker = QSignalBlocker(self.trim_end_input)
        self.trim_start_input.setValue(start_ms / 1000.0)
        self.trim_end_input.setValue(end_ms / 1000.0)
        del start_blocker, end_blocker

        self.trim_end_tracks_source = end_ms >= duration_ms
        self.apply_trim_range(seek_if_needed=True)

    def seek_to_position(self, position_ms):
        if self.current_file is None:
            return
        start_ms = int(self.trim_start_input.value() * 1000)
        end_ms = int(self.trim_end_input.value() * 1000)
        target = max(start_ms, min(int(position_ms), end_ms))
        self.player.setPosition(target)
        self.position_slider.set_position(target)

    def apply_trim_range(self, seek_if_needed=True):
        if not hasattr(self, "trim_start_input"):
            return
        start_ms = max(0, int(self.trim_start_input.value() * 1000))
        end_ms = max(start_ms + 100, int(self.trim_end_input.value() * 1000))
        if self.source_duration_ms > 0:
            end_ms = min(end_ms, self.source_duration_ms)
            start_ms = min(start_ms, max(0, end_ms - 100))

        self.position_slider.set_duration(self.source_duration_ms)
        self.position_slider.set_trim_range(start_ms, max(start_ms, end_ms))

        if seek_if_needed and self.current_file is not None:
            position = self.player.position()
            if position < start_ms or position > end_ms:
                self.player.setPosition(start_ms)
                self.position_slider.set_position(start_ms)

    def make_reset_button(self, tooltip):
        button = QPushButton("↺")
        button.setFixedSize(24, 24)
        button.setToolTip(tooltip)
        button.setAccessibleName(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(
            "QPushButton { padding: 0; min-width: 24px; max-width: 24px; "
            "min-height: 24px; max-height: 24px; border-radius: 12px; "
            "font-size: 16px; font-weight: 600; }"
        )
        return button

    def update_preview_volume(self, value):
        # Qt's QAudioOutput volume is normalized to 0.0–1.0. Values above
        # 100% are applied by FFmpeg during export, not amplified in preview.
        self.audio_output.setVolume(max(0.0, min(1.0, value / 100.0)))

    def reset_resolution_to_source(self):
        self.resolution_combo.setCurrentIndex(0)
        self.on_resolution_preset_changed(0)

    def reset_fps_to_source(self):
        self.fps_combo.setCurrentIndex(0)

    def reset_bitrate_to_source(self):
        value = self.video_metadata.get("bitrate_value")
        self.bitrate_input.setValue(float(value) if value is not None else 0.0)
        if self.video_metadata.get("bitrate_estimated"):
            self.bitrate_note.setText(self.t["bitrate_estimated"])
        else:
            self.bitrate_note.setText(self.t["bitrate_help"])

    def reset_volume_to_source(self):
        self.volume_slider.setValue(100)

    def on_resolution_preset_changed(self, index):
        mode = self.resolution_combo.currentData()
        custom = mode == "custom"
        self.output_width_input.setEnabled(custom)
        self.output_height_input.setEnabled(custom)

        if mode == "original":
            width, height = self.source_width, self.source_height
        elif mode == "custom":
            return
        else:
            try:
                width_text, height_text = str(mode).split("x", 1)
                width, height = int(width_text), int(height_text)
            except (ValueError, TypeError):
                return

        if width > 0 and height > 0:
            width_blocker = QSignalBlocker(self.output_width_input)
            height_blocker = QSignalBlocker(self.output_height_input)
            self.output_width_input.setValue(width)
            self.output_height_input.setValue(height)
            del width_blocker, height_blocker

    def source_aspect_ratio(self):
        if self.source_width > 0 and self.source_height > 0:
            return self.source_width / self.source_height
        return 16 / 9

    def update_custom_resolution(self, changed_field):
        if self.resolution_combo.currentData() != "custom":
            return
        ratio = self.source_aspect_ratio()
        if changed_field == "width":
            width = max(16, self.output_width_input.value())
            height = max(16, round(width / ratio))
            blocker = QSignalBlocker(self.output_height_input)
            self.output_height_input.setValue(height)
            del blocker
        else:
            height = max(16, self.output_height_input.value())
            width = max(16, round(height * ratio))
            blocker = QSignalBlocker(self.output_width_input)
            self.output_width_input.setValue(width)
            del blocker

    def on_output_width_changed(self, value):
        self.update_custom_resolution("width")

    def on_output_height_changed(self, value):
        self.update_custom_resolution("height")

    def reset_controls_for_video(self, metadata):
        self.source_width = int(metadata.get("width") or 0)
        self.source_height = int(metadata.get("height") or 0)
        self.source_duration_ms = int(
            (metadata.get("duration_seconds") or 0) * 1000
        )
        self.trim_end_tracks_source = True

        if self.source_width > 0 and self.source_height > 0:
            from math import gcd
            divisor = gcd(self.source_width, self.source_height)
            ratio_text = f"{self.source_width // divisor}:{self.source_height // divisor}"
            source_text = f"{self.source_width} × {self.source_height} ({ratio_text})"
        else:
            source_text = "—"
        prefix = {"es": "Resolución del video original:", "ru": "Исходное разрешение:", "en": "Source video resolution:"}.get(self.language, "Source video resolution:")
        self.source_resolution_label.setText(f"{prefix} {source_text}")

        duration = max(0.1, self.source_duration_ms / 1000.0)
        start_blocker = QSignalBlocker(self.trim_start_input)
        end_blocker = QSignalBlocker(self.trim_end_input)
        self.trim_start_input.setRange(0.0, max(0.0, duration - 0.1))
        self.trim_start_input.setValue(0.0)
        self.trim_end_input.setRange(0.1, duration)
        self.trim_end_input.setValue(duration)
        del start_blocker, end_blocker

        self.resolution_combo.setCurrentIndex(0)
        self.fps_combo.setCurrentIndex(0)
        self.on_resolution_preset_changed(0)
        self.apply_trim_range(seek_if_needed=False)

    # First-frame preview, kept entirely in memory.
    def start_preview_frame(self, path):
        self.video_widget.clear_preview_image()
        self.preview_request_path = None

        if self.preview_process.state() != QProcess.ProcessState.NotRunning:
            self.preview_process.kill()
            self.preview_process.waitForFinished(1500)

        # Do not read the process device before it has started; QProcess
        # reports "device not open" in that situation.
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            return

        path = Path(path).resolve()
        self.preview_request_path = str(path)

        arguments = [
            "-nostdin",
            "-hide_banner",
            "-loglevel", "error",
            "-i", str(path),
            "-map", "0:v:0",
            "-frames:v", "1",
            "-f", "image2pipe",
            "-vcodec", "png",
            "pipe:1"
        ]

        self.preview_process.setProgram(ffmpeg)
        self.preview_process.setArguments(arguments)
        self.preview_process.start()

    def on_preview_frame_finished(self, exit_code, exit_status):
        requested_path = self.preview_request_path
        image_data = bytes(
            self.preview_process.readAllStandardOutput()
        )

        self.preview_request_path = None

        if not requested_path or exit_code != 0:
            return

        if self.current_file is None:
            return

        if str(self.current_file) != requested_path:
            return

        if self.player.playbackState() == (
            QMediaPlayer.PlaybackState.PlayingState
        ):
            return

        image = QImage.fromData(image_data)

        if not image.isNull():
            self.video_widget.show_preview_image(image)

    # Playback controls
    def toggle_playback(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            start_ms = int(self.trim_start_input.value() * 1000)
            end_ms = int(self.trim_end_input.value() * 1000)
            position = self.player.position()
            if position < start_ms or position >= end_ms:
                self.player.setPosition(start_ms)
            self.player.play()

    def update_play_button(self, state):
        playing = (
            state == QMediaPlayer.PlaybackState.PlayingState
        )

        self.play_button.setText("Ⅱ" if playing else "▶")

        if playing:
            self.preview_request_path = None
            self.video_widget.clear_preview_image()

    def begin_seek(self):
        self.seeking = True

    def finish_seek(self):
        self.seeking = False

    def update_position(self, position):
        end_ms = int(self.trim_end_input.value() * 1000)
        if (
            self.current_file is not None
            and self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
            and end_ms > 0
            and position >= end_ms
        ):
            self.player.pause()
            self.player.setPosition(end_ms)
            position = end_ms

        if not self.seeking:
            self.position_slider.set_position(position)

        self.time_label.setText(
            f"{self.format_player_time(position)} / "
            f"{self.format_player_time(self.player.duration())}"
        )

    def update_duration(self, duration):
        self.source_duration_ms = max(0, int(duration))
        duration_seconds = self.source_duration_ms / 1000.0
        if duration_seconds > 0:
            self.trim_start_input.setMaximum(max(0.0, duration_seconds - 0.1))
            self.trim_end_input.setMaximum(duration_seconds)
            if self.trim_end_tracks_source:
                blocker = QSignalBlocker(self.trim_end_input)
                self.trim_end_input.setValue(duration_seconds)
                del blocker
                self.trim_end_input.setMinimum(
                    min(duration_seconds, self.trim_start_input.value() + 0.1)
                )
        self.position_slider.set_duration(duration)
        self.apply_trim_range(seek_if_needed=False)
        self.position_slider.setEnabled(duration > 0)

        self.time_label.setText(
            f"{self.format_player_time(self.player.position())} / "
            f"{self.format_player_time(duration)}"
        )

    @staticmethod
    def format_player_time(milliseconds):
        seconds = max(0, int(milliseconds / 1000))
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)

        return (
            f"{hours:02}:{minutes:02}:{secs:02}"
            if hours else f"{minutes:02}:{secs:02}"
        )

    def handle_player_error(self, error, error_string):
        if error != QMediaPlayer.Error.NoError:
            self.play_button.setEnabled(False)

            QMessageBox.warning(
                self,
                APP_NAME,
                f"{self.t['play_error']}\n{error_string}"
            )

    def start_export(self):
        if self.current_file is None or not self.current_file.is_file():
            return

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            QMessageBox.warning(self, APP_NAME, self.t["ffprobe_missing"])
            return

        start_seconds = max(0.0, self.trim_start_input.value())
        end_seconds = min(
            self.trim_end_input.value(),
            self.source_duration_ms / 1000.0
        )
        duration = end_seconds - start_seconds
        if duration <= 0:
            QMessageBox.warning(
                self, APP_NAME,
                "The selected time range is invalid."
                if self.language == "en" else
                "El intervalo de tiempo seleccionado no es válido."
                if self.language == "es" else
                "Выбран неверный временной диапазон."
            )
            return

        # Ask for both the destination and container before starting FFmpeg.
        format_options = [
            ("MP4", ".mp4"),
            ("MKV", ".mkv"),
            ("MOV", ".mov"),
            ("WebM", ".webm"),
        ]
        dialog = QDialog(self)
        dialog.setWindowTitle(
            "Export video" if self.language == "en" else
            "Exportar video" if self.language == "es" else "Экспорт видео"
        )
        dialog.setMinimumWidth(480)
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.setSpacing(12)

        location_label = QLabel(
            "Save location" if self.language == "en" else
            "Ubicación" if self.language == "es" else "Путь сохранения"
        )
        location_row = QHBoxLayout()
        location_input = QLineEdit()
        location_input.setText(str(self.current_file.with_name(
            self.current_file.stem + "_edited.mp4"
        )))
        browse_button = QPushButton(
            "Browse…" if self.language == "en" else
            "Examinar…" if self.language == "es" else "Обзор…"
        )
        location_row.addWidget(location_input, 1)
        location_row.addWidget(browse_button)

        format_label = QLabel(
            "Format" if self.language == "en" else
            "Formato" if self.language == "es" else "Формат"
        )
        format_combo = QComboBox()
        for label, extension in format_options:
            format_combo.addItem(label, extension)

        def update_extension(index):
            extension = format_combo.itemData(index)
            current = Path(location_input.text())
            if current.name:
                location_input.setText(str(current.with_suffix(extension)))

        def browse_destination():
            extension = format_combo.currentData()
            filters = {
                ".mp4": "MP4 video (*.mp4)",
                ".mkv": "Matroska video (*.mkv)",
                ".mov": "QuickTime video (*.mov)",
                ".webm": "WebM video (*.webm)",
            }
            selected, _ = QFileDialog.getSaveFileName(
                dialog,
                "Choose export location" if self.language == "en" else
                "Elegir ubicación de exportación" if self.language == "es" else
                "Выберите место сохранения",
                location_input.text(),
                filters[extension]
            )
            if selected:
                location_input.setText(str(Path(selected).with_suffix(extension)))

        format_combo.currentIndexChanged.connect(update_extension)
        browse_button.clicked.connect(browse_destination)
        dialog_layout.addWidget(location_label)
        dialog_layout.addLayout(location_row)
        dialog_layout.addWidget(format_label)
        dialog_layout.addWidget(format_combo)

        estimate_label_title = QLabel(
            "Estimated file size" if self.language == "en" else
            "Peso estimado del archivo" if self.language == "es" else
            "Примерный размер файла"
        )
        estimate_label_title.setObjectName("SectionTitle")
        estimate_value = QLabel("—")
        estimate_value.setObjectName("InfoValue")
        estimate_note = QLabel(
            "Approximate value; the actual size depends on video complexity and encoding."
            if self.language == "en" else
            "Es una estimación; el tamaño real depende del contenido y la compresión."
            if self.language == "es" else
            "Приблизительное значение; фактический размер зависит от содержимого и кодирования."
        )
        estimate_note.setObjectName("Muted")
        estimate_note.setWordWrap(True)

        def update_size_estimate(*_):
            selected_ext = format_combo.currentData()
            selected_fps = self.fps_combo.currentData()
            if selected_fps is None:
                selected_fps = self.video_metadata.get("fps_value") or 30.0
            selected_bitrate = self.bitrate_input.value()
            if selected_bitrate <= 0:
                selected_bitrate = self.video_metadata.get("bitrate_value") or 0.0
            if selected_bitrate <= 0:
                # CRF mode has no fixed bitrate; use a rough resolution/FPS model.
                width_for_estimate = max(16, self.output_width_input.value())
                height_for_estimate = max(16, self.output_height_input.value())
                selected_bitrate = (width_for_estimate * height_for_estimate * selected_fps * 0.08) / 1_000_000
            audio_rate = 0.128 if selected_ext == ".webm" else 0.192
            has_audio = bool(self.video_metadata.get("audio_codec"))
            total_mbps = selected_bitrate + (audio_rate if has_audio else 0.0)
            estimated_bytes = duration * total_mbps * 1_000_000 / 8 * 1.03
            estimate_value.setText(format_size(estimated_bytes))

        dialog_layout.addWidget(estimate_label_title)
        dialog_layout.addWidget(estimate_value)
        dialog_layout.addWidget(estimate_note)
        format_combo.currentIndexChanged.connect(update_size_estimate)
        self.bitrate_input.valueChanged.connect(update_size_estimate)
        self.fps_combo.currentIndexChanged.connect(update_size_estimate)
        self.output_width_input.valueChanged.connect(lambda value: update_size_estimate())
        self.output_height_input.valueChanged.connect(lambda value: update_size_estimate())
        update_size_estimate()

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.button(QDialogButtonBox.Ok).setText(
            "Export" if self.language == "en" else
            "Exportar" if self.language == "es" else "Экспорт"
        )
        buttons.button(QDialogButtonBox.Cancel).setText(
            "Cancel" if self.language == "en" else
            "Cancelar" if self.language == "es" else "Отмена"
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        output_text = location_input.text().strip()
        if not output_text:
            QMessageBox.warning(
                self, APP_NAME,
                "Choose an output location." if self.language == "en" else
                "Selecciona una ubicación de salida." if self.language == "es" else
                "Выберите место сохранения."
            )
            return
        output = Path(output_text).expanduser()
        selected_extension = format_combo.currentData()
        output = output.with_suffix(selected_extension)
        if output.resolve() == self.current_file.resolve():
            QMessageBox.warning(
                self, APP_NAME,
                "Choose a different output file." if self.language == "en" else
                "Elige un archivo de salida diferente." if self.language == "es" else
                "Выберите другой выходной файл."
            )
            return
        if output.exists():
            answer = QMessageBox.question(
                self, APP_NAME,
                "The file already exists. Replace it?" if self.language == "en" else
                "El archivo ya existe. ¿Deseas reemplazarlo?" if self.language == "es" else
                "Файл уже существует. Заменить его?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if answer != QMessageBox.Yes:
                return

        width = self.output_width_input.value()
        height = self.output_height_input.value()
        fps = self.fps_combo.currentData()
        bitrate = self.bitrate_input.value()
        volume_percent = self.volume_slider.value()

        # H.264 requires even dimensions. Keep the chosen aspect ratio while
        # rounding down to the nearest even output size.
        width = max(16, width - (width % 2))
        height = max(16, height - (height % 2))

        args = [
            "-y", "-hide_banner", "-loglevel", "error",
            "-progress", "pipe:1", "-nostats",
            "-ss", f"{start_seconds:.3f}",
            "-i", str(self.current_file),
            "-t", f"{duration:.3f}",
            "-map", "0:v:0", "-map", "0:a?",
            "-vf", f"scale={width}:{height}:flags=lanczos,setsar=1",
        ]
        if fps is not None:
            args += ["-r", str(fps)]
        if self.video_metadata.get("audio_codec"):
            args += ["-af", f"volume={volume_percent / 100.0:.2f}"]

        selected_format = format_combo.currentData()
        if selected_format == ".webm":
            args += ["-c:v", "libvpx-vp9", "-deadline", "good", "-cpu-used", "4"]
            if bitrate > 0:
                args += ["-b:v", f"{bitrate:.2f}M"]
            else:
                args += ["-crf", "32", "-b:v", "0"]
            args += ["-c:a", "libopus", "-b:a", "128k"]
        else:
            args += ["-c:v", "libx264", "-preset", "medium"]
            if bitrate > 0:
                target = f"{bitrate:.2f}M"
                args += ["-b:v", target, "-maxrate", target, "-bufsize", f"{bitrate * 2:.2f}M"]
            else:
                args += ["-crf", "20"]
            args += ["-c:a", "aac", "-b:a", "192k"]
            if selected_format in (".mp4", ".mov"):
                args += ["-movflags", "+faststart"]
        args += [str(output)]

        self.export_output_path = output
        self.export_duration_seconds = duration
        self.export_stdout_buffer = ""
        self.export_stderr_buffer = ""
        self.export_progress = QProgressDialog(
            "Preparing export…" if self.language == "en" else
            "Preparando la exportación…" if self.language == "es" else
            "Подготовка экспорта…",
            "Cancel" if self.language == "en" else
            "Cancelar" if self.language == "es" else "Отмена",
            0, 100, self
        )
        self.export_progress.setWindowTitle(
            "Exporting video" if self.language == "en" else
            "Exportando video" if self.language == "es" else "Экспорт видео"
        )
        self.export_progress.setWindowModality(Qt.WindowModal)
        self.export_progress.setMinimumDuration(0)
        self.export_progress.setValue(0)
        self.export_progress.canceled.connect(self.cancel_export)

        self.export_process = QProcess(self)
        self.export_process.setProgram(ffmpeg)
        self.export_process.setArguments(args)
        self.export_process.readyReadStandardOutput.connect(self.read_export_progress)
        self.export_process.readyReadStandardError.connect(self.read_export_errors)
        self.export_process.finished.connect(self.finish_export)
        self.export_process.errorOccurred.connect(self.export_process_error)
        self.export_button.setEnabled(False)
        self.export_process.start()

    def read_export_progress(self):
        if not self.export_process:
            return
        chunk = bytes(self.export_process.readAllStandardOutput()).decode(
            "utf-8", errors="replace"
        )
        self.export_stdout_buffer += chunk
        while "\n" in self.export_stdout_buffer:
            line, self.export_stdout_buffer = self.export_stdout_buffer.split("\n", 1)
            if line.startswith("out_time_ms="):
                try:
                    elapsed = int(line.split("=", 1)[1]) / 1_000_000
                    percent = int(max(0, min(100, elapsed / self.export_duration_seconds * 100)))
                    if self.export_progress:
                        self.export_progress.setValue(percent)
                        self.export_progress.setLabelText(
                            ("Exporting… " if self.language == "en" else
                             "Exportando… " if self.language == "es" else
                             "Экспорт… ") + f"{percent}%"
                        )
                except (ValueError, ZeroDivisionError):
                    pass
            elif line.strip() == "progress=end" and self.export_progress:
                self.export_progress.setValue(100)

    def read_export_errors(self):
        if self.export_process:
            self.export_stderr_buffer += bytes(
                self.export_process.readAllStandardError()
            ).decode("utf-8", errors="replace")

    def cancel_export(self):
        if self.export_process and self.export_process.state() != QProcess.ProcessState.NotRunning:
            self.export_process.kill()

    def export_process_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.export_button.setEnabled(self.current_file is not None)
            if self.export_progress:
                self.export_progress.close()
                self.export_progress = None
            QMessageBox.critical(
                self, APP_NAME,
                "FFmpeg could not be started." if self.language == "en" else
                "No se pudo iniciar FFmpeg." if self.language == "es" else
                "Не удалось запустить FFmpeg."
            )

    def finish_export(self, exit_code, exit_status):
        self.read_export_progress()
        self.read_export_errors()
        if self.export_progress:
            self.export_progress.close()
            self.export_progress = None
        self.export_button.setEnabled(self.current_file is not None)

        success = (
            exit_code == 0
            and exit_status == QProcess.ExitStatus.NormalExit
            and self.export_output_path is not None
            and self.export_output_path.is_file()
            and self.export_output_path.stat().st_size > 0
        )
        if success:
            QMessageBox.information(
                self, APP_NAME,
                f"Export completed successfully:\n{self.export_output_path}"
                if self.language == "en" else
                f"Exportación completada correctamente:\n{self.export_output_path}"
                if self.language == "es" else
                f"Экспорт успешно завершён:\n{self.export_output_path}"
            )
        else:
            details = self.export_stderr_buffer.strip()[-2500:]
            QMessageBox.critical(
                self, APP_NAME,
                ("Export failed or was canceled.\n\n" if self.language == "en" else
                 "La exportación falló o fue cancelada.\n\n" if self.language == "es" else
                 "Экспорт не выполнен или отменён.\n\n") + (details or "FFmpeg did not provide an error message.")
            )
        self.export_process = None
        self.export_output_path = None

    def return_to_import(self):
        self.preview_request_path = None

        if self.preview_process.state() != QProcess.ProcessState.NotRunning:
            self.preview_process.kill()
            self.preview_process.waitForFinished(1000)

        self.player.stop()
        self.player.setSource(QUrl())
        self.video_widget.clear_preview_image()
        self.stack.setCurrentIndex(0)

    # File selection
    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.t["browse"],
            self.last_directory if Path(self.last_directory).is_dir() else str(Path.home()),
            "Video files (*.mp4 *.mkv *.mov *.avi *.webm *.flv *.wmv "
            "*.m4v *.mpg *.mpeg *.ts *.mts *.m2ts *.3gp);;"
            "All files (*.*)"
        )

        if path:
            self.last_directory = str(Path(path).resolve().parent)
            self.import_file(path)

    # FFprobe metadata inspection
    def read_video_metadata(self, path):
        ffprobe = shutil.which("ffprobe")

        if not ffprobe:
            return None, "missing"

        command = [
            ffprobe,
            "-v", "error",
            "-show_entries",
            "format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate,bit_rate,duration,sample_rate,channels",
            "-of", "json",
            str(path)
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=45,
                check=True
            )

            data = json.loads(result.stdout or "{}")
            streams = data.get("streams", [])

            video_streams = [
                stream for stream in streams
                if stream.get("codec_type") == "video"
            ]

            if not video_streams:
                return None, "invalid"

            video = video_streams[0]

            audio_streams = [
                stream for stream in streams
                if stream.get("codec_type") == "audio"
            ]

            audio = audio_streams[0] if audio_streams else None
            file_info = data.get("format", {})

            # Prefer the video's own bitrate. The container bitrate also
            # includes audio and overhead, so it must not be shown as exact.
            video_bitrate = bitrate_mbps(video.get("bit_rate"))
            estimated = False

            if video_bitrate is None:
                total_bitrate = bitrate_mbps(file_info.get("bit_rate"))
                known_audio = [
                    bitrate_mbps(stream.get("bit_rate"))
                    for stream in audio_streams
                ]

                if (
                    total_bitrate is not None
                    and known_audio
                    and all(value is not None for value in known_audio)
                ):
                    estimate = total_bitrate - sum(known_audio)

                    if estimate > 0:
                        video_bitrate = estimate
                        estimated = True

            duration = video.get("duration") or file_info.get("duration")
            size = file_info.get("size") or Path(path).stat().st_size
            fps = (
                video.get("avg_frame_rate")
                or video.get("r_frame_rate")
            )

            metadata = {
                "duration": format_duration(duration),
                "duration_seconds": (
                    float(duration) if duration not in (None, "") else None
                ),
                "width": int(video.get("width") or 0),
                "height": int(video.get("height") or 0),
                "resolution": (
                    f"{video.get('width', '?')} × "
                    f"{video.get('height', '?')}"
                ),
                "fps": format_fps(fps),
                "fps_value": parse_rate(fps),
                "video_codec": video.get("codec_name") or "—",
                "audio_codec": (
                    audio.get("codec_name") if audio else None
                ),
                "bitrate": (
                    f"{'≈ ' if estimated else ''}{video_bitrate:.2f} Mbps"
                    if video_bitrate is not None else None
                ),
                "file_size": format_size(size),
                "sample_rate": (
                    f"{audio.get('sample_rate')} Hz"
                    if audio and audio.get("sample_rate") else None
                ),
                "channels": (
                    str(audio.get("channels"))
                    if audio and audio.get("channels") else None
                ),
                "bitrate_value": video_bitrate,
                "bitrate_estimated": estimated,
            }

            return metadata, "ok"

        except subprocess.TimeoutExpired:
            return None, "invalid"

        except (
            subprocess.SubprocessError,
            OSError,
            ValueError,
            TypeError,
            KeyError,
            IndexError
        ):
            return None, "invalid"

    def import_file(self, raw_path):
        path = Path(raw_path).expanduser()

        if not path.is_file():
            QMessageBox.warning(
                self, APP_NAME, self.t["invalid_path"]
            )
            return

        if path.suffix.lower() not in VIDEO_EXTENSIONS:
            QMessageBox.warning(
                self, APP_NAME, self.t["unsupported"]
            )
            return

        metadata, status = self.read_video_metadata(path)

        if status == "missing":
            QMessageBox.warning(
                self, APP_NAME, self.t["ffprobe_missing"]
            )
            return

        if status != "ok":
            QMessageBox.warning(
                self, APP_NAME, self.t["metadata_error"]
            )
            return

        self.current_file = path.resolve()
        self.last_directory = str(self.current_file.parent)
        self.video_metadata = metadata
        self.reset_controls_for_video(metadata)
        self.volume_slider.setValue(100)

        self.file_name.setText(path.name)
        self.file_path.setText(str(path.resolve()))
        self.file_path.setToolTip(str(path.resolve()))

        for key, label in self.metadata_labels.items():
            value = metadata.get(key)

            if value is None:
                value = (
                    self.t["no_audio"]
                    if key == "audio_codec"
                    else self.t["bitrate_unavailable"]
                )

            label.setText(str(value))

        bitrate = metadata.get("bitrate_value")
        self.bitrate_input.setValue(
            bitrate if bitrate is not None else 0.0
        )

        if metadata.get("bitrate_estimated"):
            self.bitrate_note.setText(self.t["bitrate_estimated"])
        else:
            self.bitrate_note.setText(self.t["bitrate_help"])

        self.player.stop()
        self.player.setSource(QUrl())

        self.seeking = False
        self.position_slider.set_position(0)
        self.position_slider.set_duration(0)
        self.position_slider.setEnabled(False)
        self.time_label.setText("00:00 / 00:00")
        self.play_button.setEnabled(True)

        self.player.setSource(
            QUrl.fromLocalFile(str(self.current_file))
        )

        self.start_preview_frame(self.current_file)
        self.export_button.setEnabled(shutil.which("ffmpeg") is not None)
        self.export_button.setToolTip("")
        self.stack.setCurrentIndex(1)

        self.statusBar().showMessage(
            f"{self.current_file.name}  •  "
            f"{metadata['resolution']}  •  {metadata['fps']}"
        )

    # Drop files anywhere on the main window.
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()

            if path:
                self.import_file(path)
                event.acceptProposedAction()
                return

        event.ignore()


def main():
    # Locate bundled resources when running as a packaged application.
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
        ffmpeg_path = base_path / "ffmpeg"
        os.environ["PATH"] = str(ffmpeg_path) + os.pathsep + os.environ.get("PATH", "")
    else:
        base_path = Path(__file__).resolve().parent

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setFont(QFont("Segoe UI", 10))

    app_icon = QIcon(str(base_path / "pess.ico"))
    app.setWindowIcon(app_icon)

    window = MainWindow()
    window.show_saved_window_mode()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
