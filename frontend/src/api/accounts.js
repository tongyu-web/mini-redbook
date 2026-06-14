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
}
