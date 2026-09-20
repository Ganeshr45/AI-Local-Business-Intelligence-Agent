import { Business } from "@/lib/types"

type Props = {
  target: Business | null
  competitors: Business[]
}

export default function CompetitorTable({ target, competitors }: Props) {
  const rows = target ? [target, ...competitors] : competitors

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <h3 className="text-base font-semibold text-slate-800 mb-4">Competitor Comparison</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b border-slate-100">
              <th className="py-2 pr-4">Business</th>
              <th className="py-2 pr-4">Rating</th>
              <th className="py-2 pr-4">Reviews</th>
              <th className="py-2 pr-4">Price Level</th>
              <th className="py-2 pr-4">Website</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((b) => (
              <tr key={b.id} className={"border-b border-slate-50 " + (b.is_target ? "bg-blue-50/50 font-medium" : "")}>
                <td className="py-2 pr-4">{b.name}{b.is_target ? " (You)" : ""}</td>
                <td className="py-2 pr-4">{b.rating !== null ? `${b.rating}★` : "unavailable"}</td>
                <td className="py-2 pr-4">{b.review_count ?? "unavailable"}</td>
                <td className="py-2 pr-4">{b.price_level !== null ? "₹".repeat(b.price_level) : "unavailable"}</td>
                <td className="py-2 pr-4">
                  {b.website ? (
                    <a href={b.website} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                      visit
                    </a>
                  ) : (
                    "none found"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
