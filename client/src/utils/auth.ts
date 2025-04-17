// 检查用户是否已登录
export const checkIsLoggedIn = (): boolean => {
  const savedUserInfo = localStorage.getItem('userInfo')
  const accessToken = localStorage.getItem('accessToken')
  return !!(savedUserInfo && accessToken)
}

// 获取用户信息
export const getUserInfo = () => {
  const savedUserInfo = localStorage.getItem('userInfo')
  return savedUserInfo ? JSON.parse(savedUserInfo) : null
}
