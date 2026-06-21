import request from "./request"

export const accountsApi = {
  register(data) { return request.post("/accounts/register/", data) },
  login(data) { return request.post("/accounts/login/", data) },
  getProfile(userId) {
    const url = userId ? `/accounts/profile/${userId}/` : "/accounts/profile/"
    return request.get(url)
  },
  updateProfile(data) { return request.put("/accounts/profile/", data) },
  uploadAvatar(formData) { return request.post("/accounts/profile/avatar/", formData) },
  getFollowers(userId) { return request.get(`/accounts/${userId}/followers/`) },
  getFollowing(userId) { return request.get(`/accounts/${userId}/following/`) },
  changePassword(data) { return request.post('/accounts/password/change/', data) },
  bindEmail(data) { return request.post('/accounts/email/bind/', data) },
  sendEmailCode(data) { return request.post('/accounts/email/send-code/', data) },
  bindEmailWithCode(data) { return request.post('/accounts/email/bind-with-code/', data) },
  unbindEmail() { return request.post("/accounts/email/unbind/") },
  sendPhoneCode(data) { return request.post("/accounts/phone/send-code/", data) },
  bindPhoneWithCode(data) { return request.post("/accounts/phone/bind-with-code/", data) },
  unbindPhone() { return request.post("/accounts/phone/unbind/") },
  updatePrivacy(data) { return request.put('/accounts/privacy/', data) },
  cancelAccount(data) { return request.post('/accounts/cancel/', data) },
}

