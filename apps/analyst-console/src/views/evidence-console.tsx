import { useQuery } from "@tanstack/react-query";
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { fetchResearchStatus, type ResearchSource } from "../research-status";

const column = createColumnHelper<ResearchSource>();
const columns = [
  column.accessor("id", { header: "Source" }),
  column.accessor("evidenceClass", { header: "Evidence class" }),
  column.accessor("purpose", { header: "Permitted use" }),
  column.accessor("status", { header: "Status" }),
  column.accessor("limitation", { header: "Limit" }),
];

export function EvidenceConsole() {
  const status = useQuery({
    queryKey: ["research-status", "v1"],
    queryFn: fetchResearchStatus,
  });
  const table = useReactTable({
    data: status.data?.sources ?? [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (status.isLoading) return <p className="content">Loading research status…</p>;
  if (status.isError) return <p className="content error">{status.error.message}</p>;
  const data = status.data!;

  return (
    <section className="content" aria-labelledby="status-heading">
      <div className="notice" role="status">
        <strong>{data.scientificStatus}</strong>
        <span>{data.limitation}</span>
      </div>

      <h2 id="status-heading">Evidence sources</h2>
      <table>
        <thead>
          {table.getHeaderGroups().map((group) => (
            <tr key={group.id}>
              {group.headers.map((header) => (
                <th key={header.id}>
                  {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Gate status</h2>
      <ul className="gates">
        {data.gates.map((gate) => (
          <li key={gate.stage}>
            <span className={"badge " + gate.status}>{gate.status}</span>
            <strong>{gate.stage}</strong>
            <span>{gate.condition}</span>
          </li>
        ))}
      </ul>
      <h2>Claim boundaries</h2>
      <ul className="claims">
        {data.claims.map((claim) => (
          <li key={claim.statement}>
            <span className={"badge " + claim.status}>{claim.status}</span>
            <strong>{claim.scope}</strong>
            <span>{claim.statement} Limit: {claim.limitation}</span>
          </li>
        ))}
      </ul>
      <p className="snapshot">Snapshot generated: {data.generatedAt}. This UI is read-only and is not the system of record.</p>
    </section>
  );
}
