from django.db import models

# Create your models here.

class Article(models.Model):

    title = models.CharField('标题', max_length=100)
    author = models.CharField('作者',max_length=20)
    url = models.CharField('链接',max_length=500,default="")
    # 目录分类
    category = models.ForeignKey('Category', verbose_name='分类',
                                 null=True, on_delete=models.DO_NOTHING,related_name='article')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    # auto_now_add : 创建时间戳，不会被覆盖

    def __str__(self):
        return self.title

    #分页时用到 -表示逆序
    class Meta:
        ordering = ['-created_time']

class Category(models.Model):
    """
        另外一个表,储存文章的分类信息
        文章表的外键指向
    """
    category = models.CharField('类名', max_length=20)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.category
