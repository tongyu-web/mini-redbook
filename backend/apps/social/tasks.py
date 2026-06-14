from django.db.models import F
from django.db import transaction
from .models import Like, Favorite, FavoriteFolder, Follow
from config.constants import NOTE_STATUS_PUBLISHED

class SocialTask:
    @staticmethod
    def toggle_like(user, note_id):
        from apps.notes.models import Note
        with transaction.atomic():
            note = Note.objects.select_for_update().get(pk=note_id, status=NOTE_STATUS_PUBLISHED)
            like = Like.objects.filter(user=user, note=note).first()
            if like:
                like.delete()
                Note.objects.filter(pk=note_id).update(like_count=F("like_count") - 1)
                from apps.accounts.models import User
                User.objects.filter(id=note.user_id).update(like_received_count=F("like_received_count") - 1)
                return {"is_liked": False, "like_count": note.like_count - 1}
            else:
                Like.objects.create(user=user, note=note)
                Note.objects.filter(pk=note_id).update(like_count=F("like_count") + 1)
                from apps.accounts.models import User
                User.objects.filter(id=note.user_id).update(like_received_count=F("like_received_count") + 1)
                return {"is_liked": True, "like_count": note.like_count + 1}

    @staticmethod
    def add_to_favorite(user, note_id, folder_id):
        from apps.notes.models import Note
        with transaction.atomic():
            note = Note.objects.select_for_update().get(pk=note_id)
            folder = FavoriteFolder.objects.get(pk=folder_id, user=user)
            _, created = Favorite.objects.get_or_create(user=user, note=note, folder=folder)
            if created:
                Note.objects.filter(pk=note_id).update(fav_count=F("fav_count") + 1)
                FavoriteFolder.objects.filter(pk=folder_id).update(note_count=F("note_count") + 1)
                from apps.accounts.models import User
                User.objects.filter(id=note.user_id).update(fav_received_count=F("fav_received_count") + 1)
            note.refresh_from_db()
            return {"is_favorited": True, "fav_count": note.fav_count}

    @staticmethod
    def remove_from_favorite(user, note_id, folder_id):
        from apps.notes.models import Note
        with transaction.atomic():
            deleted, _ = Favorite.objects.filter(user=user, note_id=note_id, folder_id=folder_id).delete()
            if deleted:
                Note.objects.filter(pk=note_id).update(fav_count=F("fav_count") - 1)
                FavoriteFolder.objects.filter(pk=folder_id).update(note_count=F("note_count") - 1)
                from apps.accounts.models import User
                User.objects.filter(id=Note.objects.get(pk=note_id).user_id).update(fav_received_count=F("fav_received_count") - 1)
            note = Note.objects.get(pk=note_id)
            return {"is_favorited": False, "fav_count": note.fav_count}

    @staticmethod
    def follow_user(user, target_id):
        if str(user.id) == str(target_id):
            return None
        with transaction.atomic():
            follow, created = Follow.objects.get_or_create(follower=user, following_id=target_id)
            if created:
                from apps.accounts.models import User
                User.objects.filter(id=user.id).update(following_count=F("following_count") + 1)
                User.objects.filter(id=target_id).update(follower_count=F("follower_count") + 1)
                return {"is_following": True}
            follow.delete()
            from apps.accounts.models import User
            User.objects.filter(id=user.id).update(following_count=F("following_count") - 1)
            User.objects.filter(id=target_id).update(follower_count=F("follower_count") - 1)
            return {"is_following": False}
