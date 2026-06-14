import request from "./request"

export const messageApi = {
  getNotifications(params) { return request.get("/messaging/notifications/", { params }) },
  markRead(id) { return request.patch(`/messaging/notifications/${id}/`) },
  markAllRead() { return request.post("/messaging/notifications/read-all/") },
  getUnreadCount() { return request.get("/messaging/notifications/unread-count/") },
  getConversations() { return request.get("/messaging/conversations/") },
  deleteConversation(userId) { return request.delete(`/messaging/conversations/${userId}/`) },
  getMessages(userId) { return request.get(`/messaging/messages/${userId}/`) },
  sendMessage(data) { return request.post("/messaging/messages/", data) },
  blockUser(userId) { return request.post(`/messaging/block/${userId}/`) },
  unblockUser(userId) { return request.delete(`/messaging/block/${userId}/`) },
}
