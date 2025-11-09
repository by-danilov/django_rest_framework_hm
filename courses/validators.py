import re
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

@deconstructible
class YouTubeURLValidator:
    """
    Проверяет, что URL ведёт на YouTube (youtube.com или youtu.be).
    """
    youtube_regex = re.compile(
        r'(https?://)?(www\.)?'
        r'(youtube\.com|youtu\.be)/.+',
        re.IGNORECASE
    )

    def __call__(self, value):
        if not self.youtube_regex.match(value):
            raise ValidationError(
                'Ссылка должна быть на YouTube (youtube.com или youtu.be).'
            )

    def __eq__(self, other):
        return isinstance(other, YouTubeURLValidator)
