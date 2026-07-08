export interface NavItem {
  key: string
  label: string
  icon: string
  route: string
}

export const coreTabs: NavItem[] = [
  { key: 'workspace', label: '工作台', icon: 'mdi:view-dashboard', route: '/workspace' },
  { key: 'homepage', label: '探索', icon: 'mdi:compass', route: '/homepage' },
  { key: 'conversation', label: '会话', icon: 'mdi:message-text', route: '/conversation' },
  { key: 'agent', label: '智能体', icon: 'mdi:robot', route: '/agent' },
]

export const secondaryItems: NavItem[] = [
  { key: 'mcp-server', label: 'MCP', icon: 'mdi:server-network', route: '/mcp-server' },
  { key: 'knowledge', label: '知识库', icon: 'mdi:book-open-page-variant', route: '/knowledge' },
  { key: 'tool', label: '工具', icon: 'mdi:puzzle', route: '/tool' },
  { key: 'agent-skill', label: 'Skill', icon: 'mdi:lightning-bolt', route: '/agent-skill' },
  { key: 'interview', label: '面试', icon: 'mdi:account-voice', route: '/interview' },
  { key: 'model', label: '模型', icon: 'mdi:brain', route: '/model' },
  { key: 'dashboard', label: '数据看板', icon: 'mdi:chart-box', route: '/dashboard' },
]

export const allMenuItems: NavItem[] = [...coreTabs, ...secondaryItems]

export function getTitleByRoute(routePath: string): string {
  const item = allMenuItems.find(m => routePath.startsWith(m.route))
  return item?.label || 'KirinChat'
}
