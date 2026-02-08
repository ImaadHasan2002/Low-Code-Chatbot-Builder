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
    // HuggingFace Integration
    huggingfaceToken?: string;
    useCustomEmbeddingModel?: boolean;
    customEmbeddingModelName?: string;
    
    // Embedding Configuration
    embeddingModel: string;
    
    // Parser Configuration
    pdfParser: string;
    csvParser: string;
    
    // Text Splitting Configuration
    splitterType: string;
    chunkSize: number;
    chunkOverlap: number;
    separator: string;
    
    // LLM Configuration
    maxTokens: number;
    useTunedModel: boolean;
    tunedModelName: string;
    temperature: number;
    llmModel?: string;
    systemPrompt: string;
    
    // Web Scraping Configuration
    scrapingMaxPages?: number;
    scrapingMaxDepth?: number;
    scrapingTimeout?: number;
    scrapingSameDomainOnly?: boolean;
    
    // Security Configuration
    blockWords: string[];
}
