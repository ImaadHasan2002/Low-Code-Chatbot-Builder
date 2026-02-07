export default async function KnowledgeBasePDFsPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params;
  return <div>KnowledgeBasePDFsPage {id}</div>
}
