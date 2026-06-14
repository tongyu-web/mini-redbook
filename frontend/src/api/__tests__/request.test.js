import { describe, it, expect, vi, beforeEach } from "vitest"

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value },
    removeItem: (key) => { delete store[key] },
    clear: () => { store = {} },
  }
})()
Object.defineProperty(window, "localStorage", { value: localStorageMock })

// Mock ElMessage
vi.mock("element-plus", () => ({
  ElMessage: { error: vi.fn() },
}))

// Mock router
vi.mock("../router", () => ({
  default: { push: vi.fn() },
}))

describe("Axios interceptors", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it("should attach token to request headers", async () => {
    localStorage.setItem("access_token", "test-jwt-token")
    const { default: request } = await import("../request")
    const config = request.interceptors.request.handlers[0].fulfilled({
      headers: {},
    })
    expect(config.headers.Authorization).toBe("Bearer test-jwt-token")
  })

  it("should unwrap data when code=0", async () => {
    const { default: request } = await import("../request")
    const mockResponse = { data: { code: 0, data: { id: 1 }, message: "ok" } }
    const result = request.interceptors.response.handlers[0].fulfilled(mockResponse)
    expect(result).toEqual({ id: 1 })
  })

  it("should show error when code!=0", async () => {
    const { default: request } = await import("../request")
    const mockResponse = { data: { code: 4001, data: null, message: "参数错误" } }
    await expect(
      request.interceptors.response.handlers[0].fulfilled(mockResponse)
    ).rejects.toThrow("参数错误")
  })

  it("should clear token and redirect on 401", async () => {
    const { default: request } = await import("../request")
    localStorage.setItem("access_token", "old-token")
    const { ElMessage } = await import("element-plus")
    const { default: router } = await import("../router")

    const error = { response: { status: 401, data: { message: "未登录" } } }
    await expect(
      request.interceptors.response.handlers[0].rejected(error)
    ).rejects.toEqual(error)

    expect(localStorage.getItem("access_token")).toBeNull()
    expect(router.push).toHaveBeenCalledWith("/login")
  })
})
