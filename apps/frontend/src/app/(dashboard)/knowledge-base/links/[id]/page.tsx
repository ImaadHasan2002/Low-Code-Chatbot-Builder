export default async function KnowledgeBaseLinksPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params;
  return <div>KnowledgeBaseLinksPage {id}</div>
}
