/** Element Plus 图标名 → HarmonyOS Sans Symbols 字符映射 */
export const iconMap: Record<string, string> = {
  Edit:           '',
  Delete:         '',
  Search:         '',
  Plus:           '',
  Setting:        '',
  User:           '',
  SwitchButton:   '',
  ArrowDown:      '',
  ArrowRight:     '',
  Close:          '',
  Check:          '',
  Warning:        '',
  InfoFilled:     '',
  SuccessFilled:  '',
  CircleClose:    '',
  Loading:        '',
  Upload:         '',
  Download:       '',
  More:           '',
  Refresh:        '',
  CopyDocument:   '',
  ChatDotRound:   '',
  Connection:     '',
  Document:       '',
  Folder:         '',
  View:           '',
  Hide:           '',
  Star:           '',
  StarFilled:     '',
  Menu:           '',
  Operation:      '',
}

export function getIconChar(name: string): string {
  return iconMap[name] || name
}
