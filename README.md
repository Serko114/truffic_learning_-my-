# Анализ трафика на круговом движении

Данная программа осуществляет анализ входящего трафика на участке кругового движения. Алгоритм определяет загруженность примыкающих дорог и выводит интерактивную статистику.

Подробный туториал по проекту - [__ссылка на видео__](https://youtu.be/u9EtqHz4Vqc)

## Установка:
Необходима версия Python >= 3.10 (лучше 3.10.14)
```
pip install torch==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```
## Работа с программой:
Перед запуском необходимо в файле __configs/app_config.yaml__ указать все желаемые параметры. Далее можно запускать код.

Классический запуск кода:
```
python main.py
```
Пример запуска в дебаг режиме (профилировщик):
```
python main.py hydra.job_logging.root.level=DEBUG
```
---

Оптимизированный код с помошью multiprocessing позволяет добиться более высокой скорости обработки (>30 fps). Для его запуска необходимо запустить терминальную команду:
```
python main_optimized.py 
```
Для тестирования работы проекта в репозитории уже имеется видео test_videos/test_video.mp4. 
Кроме того, у вас есть возможность загрузить более длинное видео, пройдя по следующей ссылке: [Google Drive ссылка](https://drive.google.com/file/d/18zeVSqqgNoxIerP6XyBE4jenECLLdBkD/view?usp=sharing).

Чтобы запустить проект с определенным видео, необходимо указать путь к нему в файле конфигурации configs/app_config.yaml проекта в разделе video_reader.src.

---
## Примеры работы кода:

__Пример работы алгоритма c выводом статистики__: каждая машина отображается цветом, соответствующим дороге, с которой она прибыла к круговому движению + выводится значение числа видимых машин + значения интенсивности входного потока (число машин в минуту с каждой входящей дороги). <br/>Отображается таким образом при выборе в конфигурации show_node.show_info_statistics=True 

![Traffic statistics 1](content_for_readme/with_statistics_1.gif)
![Traffic statistics 2](content_for_readme/with_statistics_2.gif)

Отключить отображение окна со статистикой можно при выборе в конфигурации show_node.show_info_statistics=False <br/>
Чтобы наблюдать fps обработки как в первом представленном примере, необходимо в конфиге указать show_node.draw_fps_info=True.  <br/>При наличии GPU получается достигнуть порядка 30-40 кадров в секунду в случае запуска __main_optimized.py__

---
__Пример режима демонстрации трекинга машин__ (каждый id своим уникальным цветом отображается) <br/>
Отображается таким образом при выборе в конфигурации show_node.show_track_id_different_colors=True 

![Traffic Tracking](content_for_readme/traffic_tracking.gif)

---
## Включение сторонних сервисов для визуализации результатов:
Программа позволяет вести запись актуальной статистики о машинопотоке в базу данных PostgreSQL и тут же осуществлять визуализацию в виде интерактивного дашборда Grafana.

![Dashboard](content_for_readme/grafana.jpg)


Тем самым у конечного потребителя этого приложения имеется возможность запустить код один раз, подключив на вход RTSP поток или заготовленный видеофайл, и постоянно получать актуальную статистику, а также просматривать историю загруженности участка движения.

### Что нужно сделать для запуска кода в таком режиме:
1. Необходимо в файле configs/app_config.yaml в разделе pipeline указать sent_info_db=True.
2. Необходимо установить все сервисы. Для этого нужно поднять компоуз из контейнеров и создать папки, в которые будут прокинуты вольюмы от них. Чтобы это сделать, требуется в терминале запустить написанный bat-файл:
```
run_services.bat
```
3. Как только убедитесь, что все три контейнеры поднялись и работают, то можно запускать сам код:
```
python main_optimized.py 
```
Для доступа в Grafana необходимо перйти на сайт http://localhost:3111/

Пример того, как в реальном времени строятся графики на дашборде после запуска кода:

![Grafana](content_for_readme/grafana.gif)

---

## Вывод обработанного видеопотока в веб-интерфейс:

Обработанные кадры можно отображать в веб-интерфейсе (вместо отдельного окна OpenCV). Бэкенд сайта реализован с использованием Flask.

Для того, чтобы запустить проект таким образом, необходимо в файле configs/app_config.yaml в разделе pipeline указать show_in_web=True и в show_node указать imshow=False. Далее можно запускать main.py или main_optimized.py и переходить по ссылке http://localhost:8100/

Пример того, как можно запустить проект и иметь возможность одновременно смотреть стрим по порту 8100 и наблюдать интерактивный дашборд в Grafana по порту 3111:

![web+grafana](content_for_readme/web+grafana.gif)

---

## Существующие версии кода:

В проекте специально предусмотрено множество веток, реализующих разные уровни разработки масштабного Computer Vision проекта.

Например, в главной ветке [**main**](https://github.com/Koldim2001/TrafficAnalyzer/tree/main) Docker Compose позволяет поднять сторонние сервисы (Grafana для визуализации и базу данных PostgreSQL). Однако основной код, реализующий бекенд, необходимо запускать локально с помощью имеющегося на компьютере Python.

Дальнейшее развитие проекта заключается в реализации полного Docker Compose из всех имеющихся сервисов, включая сам бекенд. Такая версия доступна в ветке [**prod_docker_version**](https://github.com/Koldim2001/TrafficAnalyzer/tree/prod_docker_version). Код из этой ветки очень просто запустить, и не требуется ничего иметь на компьютере, кроме Docker. Проект запускается единственной командой: `docker-compose -p traffic_analyzer up -d --build`

Следующим этапом развития проекта стало появление ветки [**multicamera**](https://github.com/Koldim2001/TrafficAnalyzer/tree/multicamera). В ней реализовано всё то же, что и в ветке prod_docker_version, но теперь есть удобная возможность масштабировать проект на большое число камер. Для этого потребуется лишь в файле docker-compose добавить новые контейнеры бекенда с указанием пути до нового видео ресурса. При этом вся обработка будет выполняться нативно внутри контейнеров бекенда, включая инференс самой сети. Под каждую новую камеру автоматически поднимается новый инстанс сети YOLO, реализующий детекцию транспорта.

Еще одним дальнейшим вариантом развития стало появление ветки [**feature/triton**](https://github.com/Koldim2001/TrafficAnalyzer/tree/feature/triton). По сути это та же ветка multicamera, но теперь все контейнеры бекенда не реализуют инференс сети внутри, а лишь отправляют запросы по gRPC на дополнительный сервис под названием Triton Inference Server. Благодаря этому можно масштабировать проект без значительного увеличения нагрузки (хотя значения FPS будет чуть ниже из-за того, что теперь для инференса надо отправлять запрос на сервис и получать ответы с него). Однако теперь лишь один контейнер взаимодействует с видеокартой, и инстансы бекенда не требуют GPU для работы.

Еще одним дальнейшим вариантом развития стало появление ветки [**feature/influx**](https://github.com/Koldim2001/TrafficAnalyzer/tree/feature/influx). По сути это та же ветка multicamera, но теперь база данных изменена с PostgreSQL на базу данных рмененных рядов InfluxDB. Данная база данных лучше подходит для работы с потоковыми данными, которые записываются с бекенда. При этом запись в InfluxDB осуществляется с помощью сервиса Telegraf, который читает топик брокера сообщений Kafka, в который отправляет бекенд, и производит автоматическое сохранение данных в Influx.

Структура ветвления Git проекта представлена ниже:

```
main
└── prod_docker_version
    └── multicamera
        ├── feature/triton
        └── feature/influx
```
---

## Рассмотрим, как реализован код:

Каждый кадр последовательно проходит через ноды, и в атрибуты этого объекта постепенно добавляется все больше и больше информации.

```mermaid
graph TD;
    A["VideoReader<br>Считывает кадры из видеофайла"] --> B["DetectionTrackingNodes<br>Реализует детектирование машин + трекинг"];
    B --> C["TrackerInfoUpdateNode<br>Обновляет информацию об актуальных треках"];
    C --> D["CalcStatisticsNode<br>Вычисляет загруженность дорог"];
    D --sent_info_db==False --> F;
    D --sent_info_db==True --> E["SentInfoDBNode<br>Отправляет результаты в базу данных"];
    E --> F["ShowNode<br>Отображает результаты на экране"];
    F --save_video==True --> H["VideoSaverNode<br>Сохраняет обработанные кадры"];
    F --show_in_web==True & save_video==False --> L["FlaskServerVideoNode<br>Обновляет кадры в веб-интерфейсе"];
    H --show_in_web==True --> L
```