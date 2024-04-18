from django.db import models


class FarsNews(models.Model):
    title = models.TextField(null=True, verbose_name='title')
    sub_title = models.TextField(null=True, verbose_name='sub_title')
    link_of_content = models.TextField(null=True, verbose_name='link_of_content')
    content = models.TextField(null=True, verbose_name='content')
    date = models.CharField(max_length=255, null=True, verbose_name='date')
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='created_at')


    def __str__(self):
        return f'{self.id}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'fars news - economy'
        verbose_name_plural = 'fars news - economy'