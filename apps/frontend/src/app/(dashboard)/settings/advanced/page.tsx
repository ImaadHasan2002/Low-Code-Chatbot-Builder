"use client"

import { useState, useEffect } from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useAdvancedConfig } from "@/hooks/use-advanced-config"

const modelConfigSchema = z.object({
  // HuggingFace Integration
  huggingfaceToken: z.string().optional(),
  useCustomEmbeddingModel: z.boolean().default(false),
  customEmbeddingModelName: z.string().optional(),
  
  // Embedding Configuration
  embeddingModel: z.string().min(1, "Please select an embedding model"),
  
  // Parser Configuration
  splitterType: z.string().min(1, "Please select a splitter type"),
  pdfParser: z.string().min(1, "Please select a PDF parser"),
  csvParser: z.string().min(1, "Please select a CSV parser"),
  
  // Text Splitting Configuration
  chunkSize: z.number().min(1).max(2000),
  chunkOverlap: z.number().min(0).max(500),
  separator: z.string(),
  
  // LLM Configuration
  maxTokens: z.number().min(1).max(10000),
  useTunedModel: z.boolean().default(false),
  tunedModelName: z.string(),
  learningRate: z.number().optional(),
  epochs: z.number().optional(),
  batchSize: z.number().optional(),
  gradientAccumulation: z.number().optional(),
  quantization: z.number().optional(),
  loraR: z.number().optional(),
  loraAlpha: z.number().optional(),
  loraDropout: z.number().optional(),
  temperature: z.number().min(0).max(1),
  llmModel: z.string().optional(),
  systemPrompt: z.string(),
  
  // Web Scraping Configuration
  scrapingMaxPages: z.number().min(1).max(500).optional(),
  scrapingMaxDepth: z.number().min(1).max(10).optional(),
  scrapingTimeout: z.number().min(1).max(60).optional(),
  scrapingSameDomainOnly: z.boolean().optional(),
  
  // Security Configuration
  blockWords: z.array(z.string()),
})

type ModelConfigValues = z.infer<typeof modelConfigSchema>

export default function AdvancedSettingsPage() {
  const { getAdvancedConfigQuery, updateAdvancedConfigMutation } = useAdvancedConfig();
  const { isLoading, isError, data: advancedConfigData } = getAdvancedConfigQuery;

  const form = useForm<ModelConfigValues>({
    resolver: zodResolver(modelConfigSchema),
    defaultValues: {
      huggingfaceToken: "",
      useCustomEmbeddingModel: false,
      customEmbeddingModelName: "",
      embeddingModel: "multilingual-e5-large",
      pdfParser: "PyPDFParser",
      csvParser: "CSVParser",
      splitterType: "character",
      chunkSize: 500,
      chunkOverlap: 30,
      separator: "\n",
      maxTokens: 1000,
      useTunedModel: false,
      tunedModelName: "mistralai/Mistral-7B-v0.1-finetuned",
      learningRate: 0.000005,
      epochs: 2,
      batchSize: 4,
      gradientAccumulation: 4,
      quantization: 8,
      loraR: 16,
      loraAlpha: 32,
      loraDropout: 0.05,
      temperature: 0.2,
      llmModel: "openai/gpt-4o-mini",
      systemPrompt: "You are a helpful assistant that can answer questions based on the context provided and don't make up information.",
      scrapingMaxPages: 50,
      scrapingMaxDepth: 3,
      scrapingTimeout: 10,
      scrapingSameDomainOnly: true,
      blockWords: ['secret', 'confidential', 'private'],
    },
  })

  useEffect(() => {
    if (advancedConfigData) {
      form.reset(advancedConfigData);
    }
  }, [advancedConfigData, form]);

  const useTunedModel = form.watch("useTunedModel")
  const useCustomEmbeddingModel = form.watch("useCustomEmbeddingModel")

  function onSubmit(data: ModelConfigValues) {
    console.log(data)
    updateAdvancedConfigMutation.mutate(data)
  }

  if (isLoading) {
    return (
      <div className="container mx-auto py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">Advanced Model Configuration</h1>
          <div className="space-y-4">
            <div className="h-8 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
          </div>
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="container mx-auto py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">Advanced Model Configuration</h1>
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600">Error loading advanced configuration. Please try again later.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Advanced Model Configuration</h1>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          
          <Card>
            <CardHeader>
              <CardTitle>Model Access</CardTitle>
              <CardDescription>
                Configure access tokens for external model providers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FormField
                control={form.control}
                name="huggingfaceToken"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Hugging Face Token</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Enter your Huggingface token to access Huggingface models" 
                        {...field} 
                      />
                    </FormControl>
                    <FormDescription>
                      Your API token will be encrypted and stored securely
                    </FormDescription>
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>


          <Card>
            <CardHeader>
              <CardTitle>LLM Model Configuration</CardTitle>
              <CardDescription>
                Configure the LLM model to use
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <FormField
                control={form.control}
                name="llmModel"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>LLM Model</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select LLM model" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="openai/gpt-4o-mini">openai/gpt-4o-mini</SelectItem>                        
                        <SelectItem value="mistralai/Mistral-7B-v0.1-finetuned">mistralai/Mistral-7B-v0.1-finetuned</SelectItem>
                        <SelectItem value="meta-llama/Llama-2-7b-chat-hf-finetuned">meta-llama/Llama-2-7b-chat-hf-finetuned</SelectItem>
                        <SelectItem value="google/gemma-7b-it-finetuned">google/gemma-7b-it-finetuned</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="temperature"
                render={({ field: { value, onChange } }) => (
                  <FormItem>
                    <div className="flex justify-between">
                      <FormLabel>Temperature</FormLabel>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                    <FormControl>
                      <Slider
                        min={0}
                        max={1}
                        step={0.1}
                        value={[value]}
                        onValueChange={(vals) => onChange(vals[0])}
                        className="pt-2"
                      />
                    </FormControl>
                    <FormDescription>
                      Temperature for the model
                    </FormDescription>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="systemPrompt"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>System Prompt</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Enter your system prompt"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      System prompt for the model
                    </FormDescription>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="blockWords"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Block Words</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Enter your block words e.g. 'privacy', 'confidential', 'secret'"
                        {...field}
                      />  
                    </FormControl>
                    <FormDescription>
                      Words should be separated by commas
                    </FormDescription>
                  </FormItem>
                )}
              />

            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Document Processing</CardTitle>
              <CardDescription>
                Configure how documents are processed and embedded
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <FormField
                control={form.control}
                name="embeddingModel"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Embedding Model</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select embedding model" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="stsb-roberta-large">stsb-roberta-large</SelectItem>
                        <SelectItem value="mixedbread-ai/mxbai-embed-large-v1">mixedbread-ai/mxbai-embed-large-v1</SelectItem>
                        <SelectItem value="multilingual-e5-large">multilingual-e5-large</SelectItem>
                        <SelectItem value="BAAI/bge-large-en-v1.5">BAAI/bge-large-en-v1.5 (HuggingFace)</SelectItem>
                        <SelectItem value="sentence-transformers/all-mpnet-base-v2">all-mpnet-base-v2 (HuggingFace)</SelectItem>
                        <SelectItem value="intfloat/e5-large-v2">e5-large-v2 (HuggingFace)</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="useCustomEmbeddingModel"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">Use Custom HuggingFace Model</FormLabel>
                      <FormDescription>
                        Load a custom embedding model from HuggingFace
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              {useCustomEmbeddingModel && (
                <FormField
                  control={form.control}
                  name="customEmbeddingModelName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Custom Embedding Model Name</FormLabel>
                      <FormControl>
                        <Input 
                          placeholder="e.g., sentence-transformers/all-MiniLM-L6-v2" 
                          {...field} 
                        />
                      </FormControl>
                      <FormDescription>
                        Enter a HuggingFace model identifier (e.g., organization/model-name)
                      </FormDescription>
                    </FormItem>
                  )}
                />
              )}

              <FormField
                control={form.control}
                name="pdfParser"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>PDF Parser</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger> 
                          <SelectValue placeholder="Select PDF parser" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="PyPDFParser">PyPDFParser</SelectItem>
                        <SelectItem value="PDFMinerParser">PDFMinerParser</SelectItem>
                        <SelectItem value="PDFPlumberParser">PDFPlumberParser</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="csvParser"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>CSV Parser</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger> 
                          <SelectValue placeholder="Select CSV parser" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="CSVParser">CSVParser</SelectItem>
                        <SelectItem value="PandasCSVParser">PandasCSVParser</SelectItem>
                        <SelectItem value="BatchCSVParser">BatchCSVParser</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="splitterType"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Splitter Type</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select splitter type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="character">Character</SelectItem>
                        <SelectItem value="token">Token</SelectItem>
                        <SelectItem value="recursive">Recursive</SelectItem>
                        <SelectItem value="markdown">Markdown</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="chunkSize"
                render={({ field: { value, onChange } }) => (
                  <FormItem>
                    <div className="flex justify-between">
                      <FormLabel>Chunk Size</FormLabel>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                    <FormControl>
                      <Slider
                        min={100}
                        max={2000}
                        step={50}
                        value={[value]}
                        onValueChange={(vals) => onChange(vals[0])}
                        className="pt-2"
                      />
                    </FormControl>
                    <FormDescription>
                      The size of text chunks for processing (higher values mean fewer chunks but may lose context)
                    </FormDescription>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="chunkOverlap"
                render={({ field: { value, onChange } }) => (
                  <FormItem>
                    <div className="flex justify-between">
                      <FormLabel>Chunk Overlap</FormLabel>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                    <FormControl>
                      <Slider
                        min={0}
                        max={200}
                        step={10}
                        value={[value]}
                        onValueChange={(vals) => onChange(vals[0])}
                        className="pt-2"
                      />
                    </FormControl>
                    <FormDescription>
                      Overlap between chunks to maintain context between segments
                    </FormDescription>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="separator"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Separator</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="e.g., newline '\n'" 
                        {...field} 
                      />
                    </FormControl>
                    <FormDescription>
                      Character or string used to separate chunks (e.g., newline, paragraph)
                    </FormDescription>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="maxTokens"
                render={({ field: { value, onChange } }) => (
                  <FormItem>
                    <div className="flex justify-between">
                      <FormLabel>Max Tokens</FormLabel>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                    <FormControl>
                      <Slider
                        min={100}
                        max={4000}
                        step={100}
                        value={[value]}
                        onValueChange={(vals) => onChange(vals[0])}
                        className="pt-2"
                      />
                    </FormControl>
                    <FormDescription>
                      Maximum number of tokens to process in a single request
                    </FormDescription>
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Web Scraping Configuration</CardTitle>
              <CardDescription>
                Configure settings for recursive web scraping
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <FormField
                control={form.control}
                name="scrapingMaxPages"
                render={({ field: { value, onChange } }) => (
                  <FormItem>
                    <div className="flex justify-between">
                      <FormLabel>Maximum Pages to Scrape</FormLabel>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                    <FormControl>
                      <Slider
                        min={1}
                        max={500}
                        step={1}
                        value={[value || 50]}
                        onValueChange={(vals) => onChange(vals[0])}
                        className="pt-2"
                      />
                    </FormControl>
                    <FormDescription>
                      Maximum number of pages to scrape from a website
                    </FormDescription>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="scrapingMaxDepth"
                render={({ field: { value, onChange } }) => (
                  <FormItem>
                    <div className="flex justify-between">
                      <FormLabel>Maximum Crawl Depth</FormLabel>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                    <FormControl>
                      <Slider
                        min={1}
                        max={10}
                        step={1}
                        value={[value || 3]}
                        onValueChange={(vals) => onChange(vals[0])}
                        className="pt-2"
                      />
                    </FormControl>
                    <FormDescription>
                      How many links deep to follow from the starting page
                    </FormDescription>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="scrapingTimeout"
                render={({ field: { value, onChange } }) => (
                  <FormItem>
                    <div className="flex justify-between">
                      <FormLabel>Request Timeout (seconds)</FormLabel>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                    <FormControl>
                      <Slider
                        min={1}
                        max={60}
                        step={1}
                        value={[value || 10]}
                        onValueChange={(vals) => onChange(vals[0])}
                        className="pt-2"
                      />
                    </FormControl>
                    <FormDescription>
                      Timeout for each HTTP request during scraping
                    </FormDescription>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="scrapingSameDomainOnly"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">Same Domain Only</FormLabel>
                      <FormDescription>
                        Only scrape pages from the same domain as the starting URL
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Fine-tuned Models</CardTitle>
              <CardDescription>
                Configure fine-tuned models from Hugging Face
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <FormField
                control={form.control}
                name="useTunedModel"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">
                        Use fine-tuned model from Hugging Face
                      </FormLabel>
                      <FormDescription>
                        Enable to use a custom fine-tuned model for better performance
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              {useTunedModel && (
                <>
                  <FormField
                    control={form.control}
                    name="tunedModelName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Fine-tuned LLM</FormLabel>
                        <Select 
                          onValueChange={field.onChange} 
                          defaultValue={field.value}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select fine-tuned model" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="mistralai/Mistral-7B-v0.1-finetuned">mistralai/Mistral-7B-v0.1-finetuned</SelectItem>
                            <SelectItem value="meta-llama/Llama-2-7b-chat-hf-finetuned">meta-llama/Llama-2-7b-chat-hf-finetuned</SelectItem>
                            <SelectItem value="google/gemma-7b-it-finetuned">google/gemma-7b-it-finetuned</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormItem>
                    )}
                  />
                  
                  <div className="mt-6">
                    <h3 className="text-lg font-medium mb-4">Parameter Setup</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <FormField
                        control={form.control}
                        name="learningRate"
                        render={({ field: { value, onChange } }) => (
                          <FormItem>
                            <div className="flex justify-between">
                              <FormLabel>Learning Rate</FormLabel>
                              <span className="text-sm text-muted-foreground">{value}</span>
                            </div>
                            <FormControl>
                              <Input 
                                type="number"
                                step="0.0000001"
                                min="0.0000001"
                                max="0.1"
                                value={value}
                                onChange={(e) => onChange(parseFloat(e.target.value))}
                              />
                            </FormControl>
                            <FormDescription>
                              The step size at which the model parameters are updated during training. It controls the magnitude of the updates to the model's weights.
                            </FormDescription>
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="epochs"
                        render={({ field: { value, onChange } }) => (
                          <FormItem>
                            <div className="flex justify-between">
                              <FormLabel>Epochs</FormLabel>
                              <span className="text-sm text-muted-foreground">{value}</span>
                            </div>
                            <FormControl>
                              <Input 
                                type="number"
                                step="1"
                                min="1"
                                max="100"
                                value={value}
                                onChange={(e) => onChange(parseInt(e.target.value))}
                              />
                            </FormControl>
                            <FormDescription>
                              One complete pass through the entire training dataset during the training process. It's a measure of how many times the algorithm has seen the entire dataset.
                            </FormDescription>
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="batchSize"
                        render={({ field: { value, onChange } }) => (
                          <FormItem>
                            <div className="flex justify-between">
                              <FormLabel>Batch Size</FormLabel>
                              <span className="text-sm text-muted-foreground">{value}</span>
                            </div>
                            <FormControl>
                              <Input 
                                type="number"
                                step="1"
                                min="1"
                                max="128"
                                value={value}
                                onChange={(e) => onChange(parseInt(e.target.value))}
                              />
                            </FormControl>
                            <FormDescription>
                              The number of training examples used in one iteration of training. It affects the speed and stability of the learning process.
                            </FormDescription>
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="gradientAccumulation"
                        render={({ field: { value, onChange } }) => (
                          <FormItem>
                            <div className="flex justify-between">
                              <FormLabel>Gradient Accumulation</FormLabel>
                              <span className="text-sm text-muted-foreground">{value}</span>
                            </div>
                            <FormControl>
                              <Input 
                                type="number"
                                step="1"
                                min="1"
                                max="32"
                                value={value}
                                onChange={(e) => onChange(parseInt(e.target.value))}
                              />
                            </FormControl>
                            <FormDescription>
                              Gradient accumulation involves updating model weights after accumulating gradients over multiple batches instead of after each individual batch.
                            </FormDescription>
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="quantization"
                        render={({ field: { value, onChange } }) => (
                          <FormItem>
                            <div className="flex justify-between">
                              <FormLabel>Quantization</FormLabel>
                              <span className="text-sm text-muted-foreground">{value}</span>
                            </div>
                            <FormControl>
                              <Select 
                                onValueChange={(val) => onChange(parseInt(val))} 
                                value={value?.toString()}
                              >
                                <SelectTrigger>
                                  <SelectValue placeholder="Select bit precision" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="8">8-bit</SelectItem>
                                  <SelectItem value="4">4-bit</SelectItem>
                                  <SelectItem value="16">16-bit</SelectItem>
                                </SelectContent>
                              </Select>
                            </FormControl>
                            <FormDescription>
                              Quantization is a technique used to reduce the precision of numerical values, typically from 32-bit floating point numbers to lower bit representations.
                            </FormDescription>
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="loraR"
                        render={({ field: { value, onChange } }) => (
                          <FormItem>
                            <div className="flex justify-between">
                              <FormLabel>LoRA r</FormLabel>
                              <span className="text-sm text-muted-foreground">{value}</span>
                            </div>
                            <FormControl>
                              <Input 
                                type="number"
                                step="1"
                                min="1"
                                max="64"
                                value={value}
                                onChange={(e) => onChange(parseInt(e.target.value))}
                              />
                            </FormControl>
                            <FormDescription>
                              LoRA r is a hyperparameter associated with the rank of the low-rank approximation used in LoRA.
                            </FormDescription>
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="loraAlpha"
                        render={({ field: { value, onChange } }) => (
                          <FormItem>
                            <div className="flex justify-between">
                              <FormLabel>LoRA Alpha</FormLabel>
                              <span className="text-sm text-muted-foreground">{value}</span>
                            </div>
                            <FormControl>
                              <Input 
                                type="number"
                                step="1"
                                min="1"
                                max="128"
                                value={value}
                                onChange={(e) => onChange(parseInt(e.target.value))}
                              />
                            </FormControl>
                            <FormDescription>
                              LoRA alpha is a hyperparameter used in LoRA for controlling the strength of the adaptation.
                            </FormDescription>
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="loraDropout"
                        render={({ field: { value, onChange } }) => (
                          <FormItem>
                            <div className="flex justify-between">
                              <FormLabel>LoRA Dropout</FormLabel>
                              <span className="text-sm text-muted-foreground">{value}</span>
                            </div>
                            <FormControl>
                              <Input 
                                type="number"
                                step="0.01"
                                min="0"
                                max="1"
                                value={value}
                                onChange={(e) => onChange(parseFloat(e.target.value))}
                              />
                            </FormControl>
                            <FormDescription>
                              LoRA dropout is a hyperparameter used in LoRA to control the dropout rate during fine-tuning.
                            </FormDescription>
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          <div className="flex justify-end">
            <Button type="submit">Save Configuration</Button>
          </div>
          </form>
        </Form>
      </div>
    </div>
  )
}