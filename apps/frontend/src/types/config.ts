export interface ThemeConfig {
    theme: string;
    position: string;
    primaryColor: string;
    secondaryColor: string;
    textColor: string;
    headerText: string;
    inputPlaceholder: string;
    width: string;
    height: string;
    borderRadius: string;
    launcher: boolean;
    showHeader: boolean;
}


export interface AdvancedConfig {
    huggingfaceToken?: string;
    embeddingModel: string;
    pdfParser: string;
    csvParser: string;
    splitterType: string;
    chunkSize: number;
    chunkOverlap: number;
    separator: string;
    maxTokens: number;
    useTunedModel: boolean;
    tunedModelName: string;
    temperature: number;
    llmModel?: string;
    systemPrompt: string;
    blockWords: string[];
}
