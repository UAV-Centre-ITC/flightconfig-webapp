from django.db import models

# Create your models here.
class OriginalImage(models.Model):
    org_img_name = models.CharField(max_length=100)
    cap_date = models.DateTimeField('date captured')
    org_img = models.ImageField(upload_to='')

    def __str__(self):
        return self.org_img_name

class DetectionImage(models.Model):
    ori_img = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    det_img_name = models.CharField(max_length=100)
    det_json_name = models.BooleanField(default=False)
    det_img = models.ImageField(upload_to='')
    # det_info = models.TextField(null=True, default='0')

    def __str__(self):
        return self.det_img_name

class SegmentationImage(models.Model):
    ori_img = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    seg_img_name = models.CharField(max_length=100)
    seg_img = models.ImageField(upload_to='')

    def __str__(self):
        return self.seg_img_name
