import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { getMe, logout } from "../lib/api"

export default function Settings() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    getMe()
      .then(r => setProfile(r.data))
      .catch(() => navigate("/login"))
      .finally(() => setLoading(false))
  }, [])

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  if (loading) return <div style={{ padding: 24 }}>Chargement...</div>

  const PLAN_LIMITS = { free: 1, pro: 50 }
  const QUERY_LIMITS = { free: 50, pro: 1000 }
  const docLimit = PLAN_LIMITS[profile.plan] || 1
  const queryLimit = QUERY_LIMITS[profile.plan] || 50

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", padding: 24 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <h1 style={{ margin: 0 }}>Paramètres</h1>
        <button onClick={() => navigate("/app")}>← Retour</button>
      </div>

      {/* Compte */}
      <section style={{ marginBottom: 32, padding: 20, border: "1px solid #eee", borderRadius: 8 }}>
        <h2 style={{ marginTop: 0 }}>Mon compte</h2>
        <p><strong>Email :</strong> {profile.email}</p>
        <p><strong>Plan :</strong> {profile.plan === "pro" ? "Pro" : "Gratuit"}</p>
      </section>

      {/* Quota */}
      <section style={{ marginBottom: 32, padding: 20, border: "1px solid #eee", borderRadius: 8 }}>
        <h2 style={{ marginTop: 0 }}>Utilisation</h2>
        <p>
          <strong>Documents :</strong> {profile.docs_uploaded} / {docLimit}
        </p>
        <div style={{ background: "#eee", borderRadius: 4, height: 8, marginBottom: 16 }}>
          <div style={{
            background: "#0070f3",
            width: `${Math.min((profile.docs_uploaded / docLimit) * 100, 100)}%`,
            height: "100%",
            borderRadius: 4
          }} />
        </div>
        <p>
          <strong>Requêtes ce mois :</strong> {profile.queries_used} / {queryLimit}
        </p>
        <div style={{ background: "#eee", borderRadius: 4, height: 8 }}>
          <div style={{
            background: "#0070f3",
            width: `${Math.min((profile.queries_used / queryLimit) * 100, 100)}%`,
            height: "100%",
            borderRadius: 4
          }} />
        </div>
      </section>

      {/* Danger zone */}
      <section style={{ padding: 20, border: "1px solid #ff4444", borderRadius: 8 }}>
        <h2 style={{ marginTop: 0, color: "#ff4444" }}>Zone de danger</h2>
        <p style={{ color: "#666", fontSize: 14 }}>
          La déconnexion supprime votre session locale.
        </p>
        <button
          onClick={handleLogout}
          style={{ background: "#ff4444", color: "white", border: "none", padding: "10px 20px", borderRadius: 6, cursor: "pointer" }}
        >
          Se déconnecter
        </button>
      </section>
    </div>
  )
}