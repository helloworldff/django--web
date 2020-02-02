from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image


# Create your models here.

# 栏目的 Model
class ArticleColumn(models.Model):
	# 栏目标题
	title = models.CharField(max_length=100, blank=True)
	# 创建时间
	created = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.title


class ArticlePost(models.Model):
	# Django2.0 之前的版本外键的on_delete参数可以不填；Django2.0以后on_delete是必填项
	# 外键关联一对多的2个表
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=100)
	body = models.TextField()
	# 文章的创建时间，default=timezone.now 默认写入当前系统时间
	created = models.DateTimeField(default=timezone.now)
	# auto_now = Ture 表示自动写入当前的系统时间
	update = models.DateTimeField(auto_now=True)
	total_views = models.PositiveIntegerField(default=0)
	tags = TaggableManager(blank=True)
	avatar = models.ImageField(upload_to='article/%Y%m%d', blank=True)

	# 文章栏目的 “一对多” 外键
	column = models.ForeignKey(
		ArticleColumn,
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		related_name='article'
	)

	# 内部类 class Meta 用于给 model 定义元数据
	class Meta:
		# ordering 指定模型返回的数据排列
		# -created 表明排序方式按 创建时间的倒序排列
		ordering = ('-created',)

	def __str__(self):
		# 将标题返回
		return self.title

	# 获取文章地址
	def get_absolute_url(self):
		return reverse('article:article_detail', args=[self.id])

	# 保存时处理图片
	def save(self, *args, **kwargs):
		# 调用原有的 save() 的功能
		article = super(ArticlePost, self).save(*args, **kwargs)

		# 固定宽度缩放图片大小
		if self.avatar and not kwargs.get('update_fields'):
			image = Image.open(self.avatar)
			(x, y) = image.size
			new_x = 400
			new_y = int(new_x * (y / x))
			resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
			resized_image.save(self.avatar.path)

		return article
