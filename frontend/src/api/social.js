import request from "./request"

export const socialApi = {
  toggleFollow(userId) { return request.post(`/social/follow/${userId}/`) },
  toggleLike(noteId) { return request.post(`/social/notes/${noteId}/like/`) },
  getFolders() { return request.get("/social/favorite-folders/") },
  createFolder(data) { return request.post("/social/favorite-folders/", data) },
  deleteFolder(id) { return request.delete(`/social/favorite-folders/${id}/`) },
  addFavorite(data) { return request.post("/social/favorites/", data) },
  removeFavorite(data) { return request.delete("/social/favorites/", { data }) },
  getAllFavorites() { return request.get("/social/favorites/all/") },
  getFavorites(folderId) { return request.get(`/social/favorites/${folderId}/`) },
}
