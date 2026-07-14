import { FileUploadPage } from "@/components/knowledge-base/file-upload-page"

export default function KnowledgeBaseVideosPage() {
  return (
    <FileUploadPage
      title="Videos"
      description="Upload video files as workspace knowledge sources with source metadata."
      accept="video/*,.mov,.mp4,.webm,.avi,.mpeg,.mpg"
      uploadLabel="Upload Video"
      visibleTypes={["video"]}
      emptyLabel="No videos found"
    />
  )
}
