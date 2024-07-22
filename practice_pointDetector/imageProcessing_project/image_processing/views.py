import json
import cv2
import numpy as np
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Image
from .serializers import ImageSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from django.http import HttpResponse


class ImageViewSet(generics.RetrieveAPIView):
    #queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        images = Image.objects.all()
        serializer = ImageSerializer(images, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        file = request.FILES['image']
        image = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)
        gray = 255 - cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 51, 3)
        canny = cv2.Canny(gray, 120, 255, 1)
        # thresh = 255 - thresh

        output_corn = []

        # Morph open
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (14, 14))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

        # Find distorted rectangle contour and draw onto a mask
        cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for contour in cnts:
            corn_out = []
            if (cv2.contourArea(contour) > 2750):
                (x, y, w, h) = cv2.boundingRect(contour)
                if x < 100 or x > 500 or (y + h) - y > 210 or y < 40:
                    continue
                else:
                    color = 265
                    color -= 20
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    cv2.circle(image, (x, y), 4, (255, 120, 255), -1)
                    cv2.circle(image, (x + w, y), 4, (0, 255, 0), -1)
                    cv2.circle(image, (x, y + h), 4, (color, 0, 0), -1)
                    cv2.circle(image, (x + w, y + h), 4, (255, 120, 255), -1)
                    coord = (f"A: {x}-{y} "
                             f"B: {x + w}-{y} "
                             f"C: {x}-{y + h} "
                             f"D:{x + w}-{y + h}")
                    corn_out.append(coord)
                    output_corn.append(corn_out)

        corners = cv2.goodFeaturesToTrack(canny, maxCorners=50, qualityLevel=0.5, minDistance=100)

        """for corner in corners:
            x, y = corner.ravel()
            cv2.circle(image, (int(x), int(y)), 8, (255, 120, 255), -1)
            print("({}, {})".format(x, y))"""

        # cv2.imshow("thresh", thresh)
        # cv2.imshow("canny", canny)
        # cv2.imshow("opening", opening)
        # cv2.imshow("image", image)
        cv2.imwrite('result_image.jpg', image)
        # cv2.waitKey(0)
        keys = ['ID:' + str(i) for i in range(1, len(output_corn) + 1)]
        for i in range(len(output_corn)):
            outputdict_corn = dict(zip(keys, output_corn))

        with open('results_coordinates.json', 'w') as json_file:
            json.dump(outputdict_corn, json_file)

        return Response({'output_corn': outputdict_corn}, status=status.HTTP_200_OK)

