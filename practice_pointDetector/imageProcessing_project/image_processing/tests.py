import json
import os
import unittest
from io import BytesIO

import cv2
import numpy as np
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Image
from .serializers import ImageSerializer
from .models import Image
from .views import ImageViewSet


class TestImageViewSet(TestCase):
    # инициализирует необходимые объекты для выполнения тестов.
    def setUp(self):
        self.user = mixer.blend(User)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.factory = APIRequestFactory()

    # Тест проверяет, что при запросе на получение изображений
    # возвращается код состояния 200 (успешный запрос).
    def test_get_images(self):
        view = ImageViewSet.as_view()
        request = self.factory.get('/api/images/')
        response = view(request)
        self.assertEqual(response.status_code, 200)

    # Тест проверяет что при отправке изображения в форме POST возвращается код состояния 200
    # после успешного сохранения.
    def test_post_image(self):
        file = SimpleUploadedFile("image.jpg", b"file_content", content_type="image/jpg")
        request_data = {'image': file}
        request = self.factory.post('/api/images/', data=request_data, format='multipart')
        request.user = self.user
        response = ImageViewSet.as_view()(request)
        self.assertEqual(response.status_code, 200)

class ImageSerializerTestCase(TestCase):
    def setUp(self):
        # Данные для создания объекта Image
        self.image_data = {
            'fingerprint': 'result_image.jpg', # реальный путь
        }
        # Создание объекта Image
        self.image = Image.objects.create(**self.image_data)
        # Создание экземпляра сериализатора с объектом Image
        self.serializer = ImageSerializer(instance=self.image)

    def test_contains_expected_fields(self):
        # Получение данных сериализатора
        data = self.serializer.data
        # Проверка наличия ожидаемых полей
        self.assertEqual(set(data.keys()), set(['id', 'file', 'url']))

    def test_url_generation(self):
        request = self.client.get('/')
        context = {'request': request}
        # Создание сериализатора с контекстом запроса
        serializer = ImageSerializer(instance=self.image, context=context)
        # Ожидаемый URL
        expected_url = request.build_absolute_uri(self.image.fingerprint.url)
        # Проверка соответствия URL
        self.assertEqual(serializer.data['url'], expected_url)

    def test_serialization(self):
        # Ожидаемые данные сериализации
        expected_data = {
            'id': self.image.id,
            'url': 'result_image.jpg',
        }
        # Проверка соответствия данных сериализации ожидаемым данным
        self.assertEqual(self.serializer.data, expected_data)

    def test_deserialization(self):
        # Данные для обновления объекта Image
        data = {
            'fingerprint': 'result_image.jpg',  # Замените на новый путь для обновления
        }
        # Создание сериализатора с данными для обновления
        serializer = ImageSerializer(instance=self.image, data=data, partial=True)
        # Проверка валидности данных
        self.assertTrue(serializer.is_valid())
        # Сохранение обновленных данных
        serializer.save()
        # Проверка соответствия обновленного поля ожидаемому значению
        self.assertEqual(serializer.instance.fingerprint, 'result_image.jpg')

    class ImageModelTestCase(TestCase):
        def setUp(self):
            # Подготовка данных для тестов
            self.image_data = {
                'image': SimpleUploadedFile(
                    name='test.jpg',
                    content=b'\x47\x49\x46\x38\x37\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x0A\x00\x01\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4C\x01\x00\x3B',
                    content_type='image/jpeg'
                )
            }

        def test_image_creation(self):
            # Создание объекта Image
            image = Image.objects.create(image=self.image_data['image'])
            # Проверка, что объект был создан
            self.assertTrue(isinstance(image, Image))
            # Проверка, что поле image не пустое
            self.assertTrue(image.image)

        def test_image_upload(self):
            # Создание объекта Image
            image = Image.objects.create(image=self.image_data['image'])
            # Проверка, что загруженное изображение сохранено в указанной директории
            self.assertTrue(image.image.name.startswith('images/'))
            # Проверка, что загруженное изображение имеет правильное имя файла
            self.assertEqual(image.image.name.split('/')[-1], 'test.jpg')

        def test_image_file_content(self):
            # Создание объекта Image
            image = Image.objects.create(image=self.image_data['image'])
            # Проверка содержимого загруженного файла
            with image.image.open('rb') as f:
                file_content = f.read()
                self.assertEqual(file_content, self.image_data['image'].read())

    class UtilsTests(unittest.TestCase):
        def generate_image_file(self, color=(0, 0, 0)):
            image = Image.new('RGB', (100, 100), color)
            byte_arr = BytesIO()
            image.save(byte_arr, format='JPEG')
            byte_arr.seek(0)
            return byte_arr

        def test_process_image_invalid_path(self):
            # Проверяем вызов функции с некорректным путем к изображению
            with self.assertRaises(FileNotFoundError):
                ImageViewSet("invalid_path.jpg")

        def test_detect_points_of_interest_valid(self):
            # Генерируем синтетическое черно-белое изображение с простым узором
            image = np.zeros((100, 100), np.uint8)
            cv2.rectangle(image, (30, 30), (70, 70), 255, -1)  # белый квадрат в центре

            # Обрабатываем изображение для получения углов
            points = ImageViewSet(image)

            # Проверяем, что углы были найдены
            self.assertGreater(len(points), 0)

        def test_detect_points_of_interest_empty_image(self):
            # Генерируем пустое изображение
            image = np.zeros((100, 100), np.uint8)

            # Обрабатываем изображение для получения углов
            points = ImageViewSet(image)

            # Проверяем, что углы не были найдены
            self.assertEqual(len(points), 0)

        def test_detect_points_of_interest_save_json(self):
            # Генерируем синтетическое черно-белое изображение с простым узором
            image = np.zeros((100, 100), np.uint8)
            cv2.circle(image, (50, 50), 10, 255, -1)  # белый круг в центре

            # Обрабатываем изображение для получения углов
            points = ImageViewSet(image)

            # Проверяем, что JSON файл был создан и содержит данные
            json_path = 'results.json'
            self.assertTrue(os.path.exists(json_path))

            with open(json_path, 'r') as json_file:
                data = json.load(json_file)
                self.assertEqual(data, points)

            # Удаляем JSON файл после теста
            os.remove(json_path)