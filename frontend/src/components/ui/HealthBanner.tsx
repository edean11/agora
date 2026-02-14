import { useHealth } from '../../hooks/useHealth'

function HealthBanner() {
  const { data: health } = useHealth()

  if (!health || health.ollama_available) {
    return null
  }

  return (
    <div className="bg-terracotta text-parchment px-4 py-3 text-center">
      <p className="font-sans text-sm">
        <strong>Ollama is not running.</strong> Please start Ollama (
        <code className="bg-terracotta-dark px-1 rounded">ollama serve</code>) and
        ensure <code className="bg-terracotta-dark px-1 rounded">qwen2.5:32b-instruct</code> is
        pulled.
      </p>
    </div>
  )
}

export default HealthBanner
