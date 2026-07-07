export interface NavItem {
  key: string
  label: string
  icon: string
  route: string
}

export const coreTabs: NavItem[] = [
  { key: 'workspace', label: '工作台', icon: 'workspace', route: '/workspace' },
  { key: 'homepage', label: '探索', icon: 'explore', route: '/homepage' },
  { key: 'conversation', label: '会话', icon: 'dialog', route: '/conversation' },
  { key: 'agent', label: '智能体', icon: 'robot', route: '/agent' },
]

export const secondaryItems: NavItem[] = [
  { key: 'mcp-server', label: 'MCP', icon: 'mcp', route: '/mcp-server' },
  { key: 'knowledge', label: '知识库', icon: 'knowledge', route: '/knowledge' },
  { key: 'tool', label: '工具', icon: 'plugin', route: '/tool' },
  { key: 'agent-skill', label: 'Skill', icon: 'skill', route: '/agent-skill' },
  { key: 'interview', label: '面试', icon: 'skill', route: '/interview' },
  { key: 'model', label: '模型', icon: 'model', route: '/model' },
  { key: 'dashboard', label: '数据看板', icon: 'dashboard', route: '/dashboard' },
]

export const allMenuItems: NavItem[] = [...coreTabs, ...secondaryItems]

export function getTitleByRoute(routePath: string): string {
  const item = allMenuItems.find(m => routePath.startsWith(m.route))
  return item?.label || 'KirinChat'
}
