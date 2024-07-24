from django.urls import path
from .views import SubmitImageTextView, PingView, TextMessageView

urlpatterns = [
    path("submit_image_message/", SubmitImageTextView.as_view(), name="submit_image_message"),
    path("submit_text_message/", TextMessageView.as_view(), name="submit_text_message"),
    path("ping/", PingView.as_view(), name="ping"),
]
