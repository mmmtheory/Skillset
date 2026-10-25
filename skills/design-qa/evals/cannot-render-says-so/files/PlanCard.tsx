export function PlanCard({ name, price, current }: { name: string; price: number; current: boolean }) {
  return (
    <div className="card" style={{ padding: 22, borderRadius: 6 }}>
      <h3 style={{ fontSize: 24, color: "#141414" }}>{name}</h3>
      <p className="price">${price}/mo</p>
      <button style={{ background: "#1b3b53", color: "#fff", width: "100%" }}>Get started</button>
    </div>
  );
}
