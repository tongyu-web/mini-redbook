from django.db.models import F
from django.utils import timezone
from io import BytesIO
from PIL import Image as PILImage
from django.core.files.base import ContentFile
from .models import Note, Media, NoteTag, Tag
from config.constants import NOTE_STATUS_PUBLISHED, NOTE_STATUS_DRAFT, MAX_VIDEO_DURATION

def compress_image(image_file, max_size=(1920, 1920), quality=85):
    """压缩图片到指定最大尺寸和质量"""
    try:
        img = PILImage.open(image_file)
        img_format = img.format or "JPEG"
        if img_format == "PNG" and img.mode == "RGBA":
            img = img.convert("RGB")
            img_format = "JPEG"
        img.thumbnail(max_size, PILImage.LANCZOS)
        buf = BytesIO()
        img.save(buf, format=img_format, quality=quality, optimize=True)
        ext = "jpg" if img_format == "JPEG" else "png"
        name = image_file.name.rsplit(".", 1)[0] + "." + ext
        return ContentFile(buf.getvalue(), name=name)
    except Exception:
        return image_file

class NoteTask:
    @staticmethod
    def compress_and_save_media(note, images=None, video=None):
        """处理图片压缩或视频保存"""
        if images:
            for i, img in enumerate(images):
                compressed = compress_image(img)
                Media.objects.create(note=note, file=compressed, media_type=0, order=i)

    @staticmethod
    def publish_note(user, validated_data, images=None, video=None):
        data = validated_data
        status = NOTE_STATUS_PUBLISHED
        if data.get("as_draft"):
            status = NOTE_STATUS_DRAFT
        note = Note.objects.create(
            user=user, title=data["title"],
            content=data.get("content", ""),
            type=data.get("type", 0),
            status=status
        )
        if images:
            note.cover_img = images[0]
            note.save(update_fields=["cover_img"])
            NoteTask.compress_and_save_media(note, images=images)
        if video:
            note.cover_img = video.get("cover")
            note.type = 1
            note.save(update_fields=["cover_img", "type"])
            Media.objects.create(note=note, file=video.get("file"), media_type=1, order=0)
        tag_ids = data.get("tag_ids", [])
        tag_names = data.get("tag_names", [])
        all_tag_ids = list(tag_ids)
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            all_tag_ids.append(tag.id)
        if all_tag_ids:
            for tid in all_tag_ids:
                NoteTag.objects.create(note=note, tag_id=tid)
            Tag.objects.filter(id__in=all_tag_ids).update(note_count=F("note_count") + 1)
        from apps.accounts.models import User
        User.objects.filter(id=user.id).update(note_count=F("note_count") + 1)
        return note

    @staticmethod
    def save_draft(user, validated_data, images=None, video=None):
        data = validated_data
        note = Note.objects.create(
            user=user, title=data.get("title", ""),
            content=data.get("content", ""),
            type=data.get("type", 0),
            status=NOTE_STATUS_DRAFT
        )
        if images:
            NoteTask.compress_and_save_media(note, images=images)
        return note

    @staticmethod
    def edit_note(note, validated_data, images=None, video=None):
        for key, value in validated_data.items():
            if key in ("images", "tag_ids", "tag_names", "as_draft"):
                continue
            setattr(note, key, value)
        note.is_edited = True
        if images:
            note.media_list.all().delete()
            note.cover_img = images[0]
            NoteTask.compress_and_save_media(note, images=images)
        if "tag_ids" in validated_data or "tag_names" in validated_data:
            NoteTag.objects.filter(note=note).delete()
            all_ids = list(validated_data.get("tag_ids", []))
            for name in validated_data.get("tag_names", []):
                tag, _ = Tag.objects.get_or_create(name=name)
                all_ids.append(tag.id)
            for tid in all_ids:
                NoteTag.objects.create(note=note, tag_id=tid)
        note.save()
        return note

    @staticmethod
    def soft_delete(note):
        note.status = 2
        note.taken_down_at = timezone.now()
        note.save(update_fields=["status", "taken_down_at"])
        from apps.accounts.models import User
        User.objects.filter(id=note.user_id).update(note_count=F("note_count") - 1)
        Tag.objects.filter(notetag__note=note).update(note_count=F("note_count") - 1)
