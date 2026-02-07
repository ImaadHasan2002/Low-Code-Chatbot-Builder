export default async function KnowledgeBaseImagesPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params;
  return <div>KnowledgeBaseImagesPage {id}</div>
}
