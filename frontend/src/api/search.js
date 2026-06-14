import request from "./request"

export const searchApi = {
  search(params) { return request.get("/search/", { params }) },
  suggest(q) { return request.get("/search/suggest/", { params: { q } }) },
  hotTags() { return request.get("/search/hot-tags/") },
  recommend() { return request.get("/search/recommend/") },
  getHistory() { return request.get("/search/history/") },
  clearHistory() { return request.delete("/search/history/") },
}
