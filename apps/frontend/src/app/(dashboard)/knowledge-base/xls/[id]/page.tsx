export default async function KnowledgeBaseXLSPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params;
  return <div>KnowledgeBaseXLSPage {id}</div>
}
