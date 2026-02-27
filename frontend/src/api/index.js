import api from "./axios";

export const authApi = {
  register: (data) => api.post("/auth/register", data),
  login: (data) => api.post("/auth/login", data),
  refresh: (data) => api.post("/auth/refresh", data),
  me: () => api.get("/auth/me"),
  updateMe: (data) => api.patch("/auth/me", data),
};

export const friendsApi = {
  list: () => api.get("/friends"),
  invite: (data) => api.post("/friends/invite", data),
  listInvitations: () => api.get("/friends/invitations"),
  remove: (friendId) => api.delete(`/friends/${friendId}`),
};

export const itemsApi = {
  list: () => api.get("/items"),
  create: (data) => api.post("/items", data),
  get: (id) => api.get(`/items/${id}`),
  update: (id, data) => api.patch(`/items/${id}`, data),
  delete: (id) => api.delete(`/items/${id}`),
  listShares: (id) => api.get(`/items/${id}/shares`),
  share: (id, data) => api.post(`/items/${id}/shares`, data),
  revokeShare: (id, shareId) => api.delete(`/items/${id}/shares/${shareId}`),
};

export const groupsApi = {
  list: () => api.get("/groups"),
  create: (data) => api.post("/groups", data),
  get: (id) => api.get(`/groups/${id}`),
  update: (id, data) => api.patch(`/groups/${id}`, data),
  delete: (id) => api.delete(`/groups/${id}`),
  listMembers: (id) => api.get(`/groups/${id}/members`),
  addMember: (id, data) => api.post(`/groups/${id}/members`, data),
  removeMember: (id, userId) => api.delete(`/groups/${id}/members/${userId}`),
};

export const plansApi = {
  list: () => api.get("/plans"),
  create: (data) => api.post("/plans", data),
  get: (id) => api.get(`/plans/${id}`),
  update: (id, data) => api.patch(`/plans/${id}`, data),
  delete: (id) => api.delete(`/plans/${id}`),
  toggleItem: (id, piId, data) => api.patch(`/plans/${id}/items/${piId}`, data),
  complete: (id) => api.post(`/plans/${id}/complete`),
  records: (id) => api.get(`/plans/${id}/records`),
  listShares: (id) => api.get(`/plans/${id}/shares`),
  share: (id, data) => api.post(`/plans/${id}/shares`, data),
  revokeShare: (id, shareId) => api.delete(`/plans/${id}/shares/${shareId}`),
};
