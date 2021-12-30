## Thanks to http://www.learningaboutelectronics.com/Articles/How-to-restrict-the-size-of-file-uploads-with-Python-in-Django.php
## for explaining the following code

from django.core.exceptions import ValidationError


def validate_file_size(value):
    filesize = value.size
    
    if filesize > 5242800:
        raise ValidationError("The maximum file size that can be uploaded is 5MB")
    else:
        return value