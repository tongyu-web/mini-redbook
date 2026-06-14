from django.db.models import F
from django.utils import timezone
from .models import Note, Media, NoteTag, Tag
from config.constants import NOTE_STATUS_PUBLISHED, NOTE_STATUS_DRAFT

class NoteTask:
    @staticmethod
    def publish_note(user, validated_data):
        data = validated_data
        note = Note.objects.create(
            user=user, title=data["title"],
            content=data.get("content", ""),
            type=data.get("type", 0),
            status=NOTE_STATUS_PUBLISHED
        )
        images = data.get("images", [])
        if images:
            note.cover_img = images[0]
            note.save(update_fields=["cover_img"])
            for i, img in enumerate(images):
                Media.objects.create(note=note, file=img, media_type=0, order=i)
        tag_ids = data.get("tag_ids", [])
        if tag_ids:
            for tid in tag_ids:
                NoteTag.objects.create(note=note, tag_id=tid)
            Tag.objects.filter(id__in=tag_ids).update(note_count=F("note_count") + 1)
        from apps.accounts.models import User
        User.objects.filter(id=user.id).update(note_count=F("note_count") + 1)
        return note

    @staticmethod
    def save_draft(user, validated_data):
        data = validated_data
        note = Note.objects.create(
            user=user, title=data["title"],
            content=data.get("content", ""),
            type=data.get("type", 0),
            status=NOTE_STATUS_DRAFT
        )
        return note

    @staticmethod
    def edit_note(note, validated_data):
        for key, value in validated_data.items():
            if key in ("images", "tag_ids"):
                continue
            setattr(note, key, value)
        note.is_edited = True
        if "images" in validated_data:
            note.media_list.all().delete()
            for i, img in enumerate(validated_data["images"]):
                Media.objects.create(note=note, file=img, media_type=0, order=i)
        if "tag_ids" in validated_data:
            NoteTag.objects.filter(note=note).delete()
            for tid in validated_data["tag_ids"]:
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
