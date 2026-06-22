import { ref } from 'vue'
import { defineStore } from 'pinia'
import { parseJdAPI, createSkillFromJdAPI, type JdParseData, type JdSkillData } from '@/apis/jd'

export const useJdStore = defineStore('jd', () => {
  const jdText = ref('')
  const parseResult = ref<JdParseData | null>(null)
  const skillResult = ref<JdSkillData | null>(null)
  const parsing = ref(false)
  const creating = ref(false)

  async function parseJd() {
    if (!jdText.value.trim()) return
    parsing.value = true
    try {
      const res = await parseJdAPI(jdText.value)
      if (res.data.status_code === 200 && res.data.data) {
        parseResult.value = res.data.data
      }
    } finally {
      parsing.value = false
    }
  }

  async function createSkill() {
    if (!parseResult.value) return null
    creating.value = true
    try {
      const res = await createSkillFromJdAPI(parseResult.value)
      if (res.data.status_code === 200 && res.data.data) {
        skillResult.value = res.data.data
        return res.data.data
      }
      return null
    } finally {
      creating.value = false
    }
  }

  function reset() {
    jdText.value = ''
    parseResult.value = null
    skillResult.value = null
  }

  return { jdText, parseResult, skillResult, parsing, creating, parseJd, createSkill, reset }
})
