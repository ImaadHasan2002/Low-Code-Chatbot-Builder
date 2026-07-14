import { FileUploadPage } from "@/components/knowledge-base/file-upload-page"

export default function KnowledgeBaseImagesPage() {
  return (
    <FileUploadPage
      title="Images"
      description="Upload image files as workspace knowledge sources with source metadata."
      accept="image/*,.svg"
      uploadLabel="Upload Image"
      visibleTypes={["image"]}
      emptyLabel="No images found"
    />
  )
}
