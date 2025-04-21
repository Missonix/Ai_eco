interface Entitlement {
  entitlement_id: string
  rule_id: string
  course_name: string
  product_name: string
  start_date: string
  end_date: string
  daily_remaining: number
  is_active: boolean
}

interface UserInfo {
  user_id: string
  phone: string
  access_token: string
  entitlements: Entitlement[]
}

// 检查用户是否已登录
export const checkIsLoggedIn = (): boolean => {
  const savedUserInfo = localStorage.getItem('userInfo')
  const accessToken = localStorage.getItem('accessToken')
  return !!(savedUserInfo && accessToken)
}

// 获取用户信息
export const getUserInfo = (): UserInfo | null => {
  const savedUserInfo = localStorage.getItem('userInfo')
  return savedUserInfo ? JSON.parse(savedUserInfo) : null
}

// 检查用户是否有特定功能的访问权限
export const checkFeatureAccess = (ruleId: string): boolean => {
  const userInfo = getUserInfo()
  if (!userInfo || !userInfo.entitlements) return false
  
  return userInfo.entitlements.some((entitlement: Entitlement) => 
    entitlement.rule_id === ruleId && entitlement.is_active
  )
}

// 获取用户可用的功能列表
export const getAvailableFeatures = (): string[] => {
  const userInfo = getUserInfo()
  if (!userInfo || !userInfo.entitlements) return []
  
  return userInfo.entitlements
    .filter((entitlement: Entitlement) => entitlement.is_active)
    .map((entitlement: Entitlement) => entitlement.rule_id)
}
