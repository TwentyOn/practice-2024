# practice-2024
Данное задание выполнено в рамках производственной практики 07.2024г

функционал продукта: на фотографиях (RGB-изображениях) детектирует “точки-интереса”. В качестве “точек-интереса” (Point-of-Interest) выступают углы прямоугольников (или близких к ним фигур), присутствующих на изображениях. Прямоугольники образуются гранями параллелепипедов перпендикулярные (или “почти перпендикулярные”) к оптической оси камеры.

Работа осуществляется следующим образом: после запуска локального сервера, передачи изображения POST-запросом и прохождения обработки, в качестве ответа пользователю возвращается json-строка с парами ключ-значение, где ключом является ID задетектированного объекта (прямоугольника), а значением являются координаты в формате {A: x1-y1, B: x2-y2, C: x3-y3, D: x4-y4}. Где A, B, C, D — углы прямоугольника, левый верхний, правый верхний, левый нижний и правый нижний соответственно. Пары значений xN-yN представляют собой значение координат по осям х и у.

После возврата ответа пользователю в директории проекта сохраняются следующие файлы:
- [results_coordinates](https://github.com/TwentyOn/practice-2024/blob/main/practice_pointDetector/imageProcessing_project/results_coordinates.json) - представляет собой json-файл с найденными координатами объектов
- [result_image](https://github.com/TwentyOn/practice-2024/blob/main/practice_pointDetector/imageProcessing_project/result_image.jpg?raw=true) - представляет собой изображение с визуализацией углов прямоугольника и его контуров:

# Необходимые компоненты
- Python 3.10^
- Виртуальное окружение (Anaconda или д.р)
- Docker

# Создание виртуального окружения
Создание:

```conda create --name ImageProcessing python=3.10```

Запуск:

```conda activate ImageProcessing```

# Установка необходимых библиотек

Установка нужных библиотек выполняется с помощью файла requirements.txt следующей командой:


```pip install -r requirements.txt```

# Локальный запуск
Создание миграций:


```python manage.py migrate```


Запуск сервера:


```python manage.py runserver```


- После запуска сервера проект будет доступен по локальному адресу: http://127.0.0.1:8000
- Документация для взаимодействия с API в виде Postman-коллекции представленна в файле [POSTMAN_request_API_DRF](https://github.com/TwentyOn/practice-2024/blob/main/practice_pointDetector/imageProcessing_project/POSTMAN_request_API_DRF.postman_collection.json)
- Для отправки POST-запроса необходима авторизация по адресу: http://127.0.0.1:8000/api/token/
  - логин: admin
  - пароль: admin

После авторизации будет предоставлен авторизационный токен (access) и токен refresh. 

Вы можете использовать токен refresh в случае, если срок действия авторизационного токена истек, по адресу: http://127.0.0.1:8000/api/token/refresh/ и получить новый токен.

Токен авторизации передаётся в параметре "Headers" по ключу Authorization. Подробности можно увидеть в файле-документации Postman


Для взаимодействия с докуменцией swagger необходимо перейти по адресу: http://127.0.0.1:8000/api/token/schema/swagger-ui

# Запуск API с помощью Docker

Сборка Docker-образа и запуск контейнера:


```docker-compose build ``` 


```docker-compose up ```

Выполнение маграций:


``` python manage.py migrate ```

Для сбора статики:

```python manage.py collectstatic --noinput```


Запуск сервера:


```python manage.py runserver```

После запуска сервера взаимодействие с API происходит по аналогичным url-адресам, описаным в разделе "Локальный запуск"
