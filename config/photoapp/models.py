import io

from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager

class Photo(models.Model):
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='photos/')
    watermarked_image = models.ImageField(upload_to='watermarks/', blank=True, null=True)
    submitter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    tags = TaggableManager()
    uploaded_images_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.watermarked_image:
            super().save(*args, **kwargs)

            watermark_path = 'static/watermarks/watermark.png'
            watermarked_image = self.apply_watermark(self.image.path, watermark_path)

            self.watermarked_image.save(f'{self.image.name.split(".")[0]}_watermarked.png',
                                        ContentFile(watermarked_image.getvalue()), save=False)
            self.save(update_fields=['watermarked_image'])

        else:
            super().save(*args, **kwargs)

    def apply_watermark(self, image_path, watermark_path):
        img = Image.open(image_path)
        watermark = Image.open(watermark_path)

        width, height = img.size
        resized_watermark = watermark.resize((width, height))

        mask = resized_watermark.split()[3]

        img.paste(resized_watermark, (0, 0), mask)

        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        return output