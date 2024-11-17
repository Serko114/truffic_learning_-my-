import os
import json
import time
import logging
from typing import Generator
import cv2

from elements.FrameElement import FrameElement
from elements.VideoEndBreakElement import VideoEndBreakElement

logger = logging.getLogger(__name__)
# -------------------задаем переменные---------------------------------------
config = {'src': 'test_videos/test_video.mp4',  # путь до файла обработки или номер камеры (int) или ссылки на m3u8 / rtsp поток
          'skip_secs': 0,  # считываем кадры раз в <skip_secs> секунд
          # json файл с координатами дорог на видео
          'roads_info': 'configs/entry_exit_lanes.json'
          }

print(config)
# ----------------------------------------------------------------------------


class VideoReader:
    """Модуль для чтения кадров с видеопотока"""
    # ------------------------------------------инициализация переменных------------------------------------

    def __init__(self, config: dict) -> None:
        self.video_pth = config["src"]
        self.video_source = f"Processing of {self.video_pth}"
        assert (
            os.path.isfile(self.video_pth)  # проверка файла
            or type(self.video_pth) == int  # проверка камеры
            or "://" in self.video_pth  # проверка гиперссылки
        ), f"VideoReader| Файл {self.video_pth} не найден"  # сообщение об ошибке, если ничего не найдено

        self.stream = cv2.VideoCapture(self.video_pth)  # инициализация видео

        # считываем кадры раз в <skip_secs> секунд, здесь '0'
        self.skip_secs = config["skip_secs"]
        # специально отрицательное при инициализации (костыль)
        self.last_frame_timestamp = -1
        self.first_timestamp = 0  # Значение времени в момент первого кадра потока

        self.break_element_sent = False  # Был ли отправлен элемент прерывания видеопотока

        # устанавливаем ширину и высоту при обработке с видео-камеры (на входе int значение номера камеры)
        if type(self.video_pth) == int:
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # Чтение данных из файла JSON (информация о координатах въезда и выезда дорог)
        with open(config["roads_info"], "r") as file:
            data_json = json.load(file)

        # Преобразование данных координат дорог в формат int
        self.roads_info = {
            key: [int(value) for value in values] for key, values in data_json.items()
        }
    # --------------------------------------------сама функция-------------------------------------------------

    def process(self) -> Generator[FrameElement, None, None]:
        # номер кадра текущего видео
        frame_number = 0

        while True:
            ret, frame = self.stream.read()
            if not ret:
                logger.warning(
                    "Can't receive frame (stream end?). Exiting ...")
                if not self.break_element_sent:
                    self.break_element_sent = True
                    # отправим VideoEndBreakElement чтобы обозначить окончание потока
                    yield VideoEndBreakElement(self.video_pth, self.last_frame_timestamp)
                break

            # Вычисление timestamp в случае если вытягиваем с видоса или камеры (стартуем с 0 сек)
            if type(self.video_pth) == int or "://" in self.video_pth:
                # с камеры:
                if frame_number == 0:
                    self.first_timestamp = time.time()
                timestamp = time.time() - self.first_timestamp
            else:
                # с видео:
                timestamp = self.stream.get(cv2.CAP_PROP_POS_MSEC) / 1000

                # делаем костыль, чтобы не было 0-вых тайстампов под конец стрима, баг cv2
                timestamp = (
                    timestamp
                    if timestamp > self.last_frame_timestamp
                    else self.last_frame_timestamp + 0.1
                )

            # Пропустим некоторые кадры если требуется согласно конфигу
            if abs(self.last_frame_timestamp - timestamp) < self.skip_secs:
                continue

            self.last_frame_timestamp = timestamp

            frame_number += 1

            yield FrameElement(self.video_source, frame, timestamp, frame_number, self.roads_info)
