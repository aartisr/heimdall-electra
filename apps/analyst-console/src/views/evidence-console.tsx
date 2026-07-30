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

  if (status.isLoading) return <p className="content" aria-live="polite">Loading research status…</p>;
  if (status.isError) return <section className="content error" role="alert"><h2>Research status is unavailable</h2><p>{status.error.message}</p><button type="button" onClick={() => status.refetch()}>Try again</button></section>;
  const data = status.data!;

  return (
    <section className="content" id="evidence-status" aria-labelledby="status-heading" tabIndex={-1}>
      <div className="notice" role="status">
        <strong>{data.scientificStatus}</strong>
        <span>{data.limitation}</span>
      </div>

      <h2 id="status-heading">Evidence sources</h2>
      <div className="table-wrap" tabIndex={0} aria-label="Evidence sources table">
      <table>
        <caption>Declared source purpose, evidence class, status, and limitation.</caption>
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
                <td key={cell.id} data-label={String(cell.column.columnDef.header)}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      </div>

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
      <p className="snapshot">Snapshot generated: <time dateTime={data.generatedAt}>{data.generatedAt}</time>. This UI is read-only and is not the system of record.</p>
    </section>
  );
}
