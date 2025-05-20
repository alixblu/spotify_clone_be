from djongo import models
from bson import ObjectId
from django.utils import timezone
from django.core.exceptions import ValidationError
from user_management.models import User

class Playlist(models.Model):
    _id = models.ObjectIdField(primary_key=True, auto_created=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cover_img = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    isfromDB = models.BooleanField(default=True)  
    isHidden = models.BooleanField(default=False)

    class Meta:
        db_table = "playlists"
    def __str__(self):
        return self.name
    
class Artist(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId, auto_created=True)
    artist_name = models.CharField(max_length=255)
    profile_img = models.URLField(blank=True, null=True)
    biography = models.TextField(blank=True)
    label = models.CharField(max_length=50, default="Artist")
    isfromDB = models.BooleanField(default=True)
    isHidden = models.BooleanField(default=False)

    class Meta:
        db_table = "artists"
    def __str__(self):
        return self.artist_name
    
class Album(models.Model):
    _id = models.ObjectIdField(primary_key=True, auto_created=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album_name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    cover_img = models.URLField(blank=True, null=True)
    release_date = models.DateField()
    total_tracks = models.IntegerField()
    isfromDB = models.BooleanField(default=True)
    isHidden = models.BooleanField(default=False)

    class Meta:
        db_table = "albums"

    def __str__(self):
        return self.album_name
    
class Song(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId, auto_created=True)
    album_id = models.ForeignKey(Album, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)
    duration = models.TimeField()
    # Tạm thời gắn FileField cho video, audio và img, 
    # Sau này thay FileField bằng URLField/CharField để lưu URL từ Cloudinary
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    audio_file = models.FileField(upload_to='audios/', blank=True, null=True)
    img = models.URLField(blank=True, null=True)
    isfromDB = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    isHidden = models.BooleanField(default=False)

    class Meta:
        db_table = "songs"
    def __str__(self):
        return self.title


# Follow model
class Follow(models.Model):
    """
    Model quan hệ follow giữa:
    - User -> User (follow cá nhân)
    - User -> Artist (follow nghệ sĩ)
    """
    _id = models.ObjectIdField(primary_key=True, default=ObjectId, auto_created=True)
    
    # Người thực hiện follow (luôn là User)
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    
    # Đối tượng được follow (User)
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_followers',
        null=True,
        blank=True
    )
    
    # Đối tượng được follow (Artist)
    target_artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='artist_followers',
        null=True,
        blank=True
    )
    
    # Thời gian follow
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )

    class Meta:
        db_table = "follows"
        unique_together = [
            ('follower', 'target_user'),  # 1 user chỉ follow 1 user khác 1 lần
            ('follower', 'target_artist')  # 1 user chỉ follow 1 artist 1 lần
        ]
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['target_user']),
            models.Index(fields=['target_artist']),
        ]

    def __str__(self):
        target = self.target_user or self.target_artist
        return f"{self.follower.username} follows {target.name}"

    def clean(self):
        """Validation chính"""
        if self.target_user and self.follower == self.target_user:
            raise ValidationError("Không thể tự follow chính mình")
        
        if not (self.target_user or self.target_artist):
            raise ValidationError("Phải chọn ít nhất 1 đối tượng để follow")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def target(self):
        """Truy cập nhanh đối tượng được follow"""
        return self.target_user or self.target_artist



# UserLibrary model, class này để người dùng thêm các playlist, album của người khác vào thư viện của mình
# class UserLibraryItem(models.Model):
#     """
#     Model cho phép người dùng lưu album/playlist vào thư viện cá nhân
#     Sử dụng GenericForeignKey để hỗ trợ nhiều loại nội dung
#     """
#     class ItemType(models.TextChoices):
#         ALBUM = 'album', 'Album'
#         PLAYLIST = 'playlist', 'Playlist'
#         # Có thể mở rộng thêm: ARTIST = 'artist', 'Artist'
    
#     _id = models.ObjectIdField(
#         primary_key=True,
#         default=ObjectId,
#         editable=False
#     )
    
#     user = models.ForeignKey(
#         'User',
#         on_delete=models.CASCADE,
#         related_name='library_items',
#         verbose_name="Người dùng"
#     )
    
#     # Hệ thống Generic Foreign Key
#     content_type = models.ForeignKey(
#         ContentType,
#         on_delete=models.CASCADE,
#         limit_choices_to={'model__in': ['album', 'playlist']}
#     )
#     object_id = models.ObjectIdField(verbose_name="ID đối tượng")
#     content_object = GenericForeignKey('content_type', 'object_id')
    
#     added_at = models.DateTimeField(
#         default=timezone.now,
#         verbose_name="Thời gian thêm",
#         db_index=True
#     )
    
#     # Thêm trường metadata nếu cần
#     is_favorite = models.BooleanField(
#         default=False,
#         verbose_name="Yêu thích"
#     )
    
#     class Meta:
#         db_table = "user_library_items"
#         verbose_name = "Mục thư viện"
#         verbose_name_plural = "Các mục thư viện"
#         unique_together = ('user', 'content_type', 'object_id')
#         ordering = ['-added_at']
#         indexes = [
#             models.Index(fields=['content_type', 'object_id']),
#             models.Index(fields=['user', 'content_type']),
#         ]

#     def __str__(self):
#         return f"{self.user.username} - {self.get_content_type_display()} {self.object_id}"

#     def clean(self):
#         """Validation tùy chỉnh"""
#         # Kiểm tra đối tượng tồn tại
#         if not self.content_type.get_object_for_this_type(_id=self.object_id).exists():
#             raise ValidationError(f"{self.get_content_type_display()} không tồn tại")

#     @property
#     def item_type(self):
#         """Thuộc tính tương thích ngược"""
#         return self.content_type.model

#     @property
#     def item_id(self):
#         """Thuộc tính tương thích ngược"""
#         return self.object_id