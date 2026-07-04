class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super()
    this._buffer = []
    this._targetSamples = 3200  // 200ms at 16kHz
    this.port.onmessage = (e) => {
      if (e.data && e.data.type === 'flush') this._flush()
    }
  }

  _flush() {
    if (this._buffer.length > 0) {
      const chunk = new Int16Array(this._buffer)
      this._buffer = []
      this.port.postMessage(chunk.buffer, [chunk.buffer])
    }
  }

  process(inputs) {
    const input = inputs[0]
    if (!input || !input[0]) return true

    const float32 = input[0]
    const inputSampleRate = sampleRate

    const ratio = inputSampleRate / 16000
    const outputLength = Math.floor(float32.length / ratio)
    const resampled = new Float32Array(outputLength)

    for (let i = 0; i < outputLength; i++) {
      const srcIndex = i * ratio
      const low = Math.floor(srcIndex)
      const high = Math.min(low + 1, float32.length - 1)
      const frac = srcIndex - low
      resampled[i] = float32[low] * (1 - frac) + float32[high] * frac
    }

    const int16 = new Int16Array(outputLength)
    for (let i = 0; i < outputLength; i++) {
      const s = Math.max(-1, Math.min(1, resampled[i]))
      int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
    }

    for (let i = 0; i < int16.length; i++) {
      this._buffer.push(int16[i])
      if (this._buffer.length >= this._targetSamples) {
        const chunk = new Int16Array(this._buffer)
        this._buffer = []
        this.port.postMessage(chunk.buffer, [chunk.buffer])
      }
    }

    return true
  }
}

registerProcessor('pcm-processor', PCMProcessor)
