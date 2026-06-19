import request from "./request"

export const notesApi = {
  getNotes(page = 1) { return request.get(`/notes/?page=${page}`) },
  getNotesByCategory(category, page = 1) { return request.get(`/notes/?category=${category}&page=${page}`) },
  getNote(id) { return request.get(`/notes/${id}/`) },
  createNote(formData) { return request.post("/notes/", formData) },
  updateNote(id, data) { return request.patch(`/notes/${id}/`, data) },
  deleteNote(id) { return request.delete(`/notes/${id}/`) },
  getUserNotes(userId) { return request.get(`/notes/user/${userId}/`) },
  getLikedNotes() { return request.get("/notes/liked/") },
  getDrafts() { return request.get("/notes/drafts/") },
  getRecycle() { return request.get("/notes/recycle/") },
  restoreNote(id) { return request.post(`/notes/recycle/restore/${id}/`) },
  hardDeleteNote(id) { return request.delete(`/notes/recycle/hard-delete/${id}/`) },
  cleanupRecycle() { return request.post("/notes/recycle/cleanup/") },
  getTags() { return request.get("/notes/tags/") },
  getComments(noteId, page = 1) { return request.get(`/notes/${noteId}/comments/?page=${page}`) },
  postComment(noteId, data) { return request.post(`/notes/${noteId}/comments/`, data) },
}
