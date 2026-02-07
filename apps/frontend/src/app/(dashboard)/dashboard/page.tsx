"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { Progress } from "@/components/ui/progress";

// Mock data for demonstration
const satisfactionData = [
  { name: 'Very Satisfied', value: 45 },
  { name: 'Satisfied', value: 30 },
  { name: 'Neutral', value: 15 },
  { name: 'Dissatisfied', value: 10 },
];

const dailyQueries = [
  { date: '2024-03-01', queries: 120 },
  { date: '2024-03-02', queries: 150 },
  { date: '2024-03-03', queries: 180 },
  { date: '2024-03-04', queries: 160 },
  { date: '2024-03-05', queries: 200 },
  { date: '2024-03-06', queries: 220 },
  { date: '2024-03-07', queries: 190 },
];

const responseTimeData = [
  { time: '0-1s', count: 150 },
  { time: '1-2s', count: 200 },
  { time: '2-3s', count: 100 },
  { time: '3-5s', count: 50 },
  { time: '>5s', count: 20 },
];

const categoryData = [
  { name: 'Product Info', value: 35 },
  { name: 'Support', value: 25 },
  { name: 'General', value: 20 },
  { name: 'Technical', value: 15 },
  { name: 'Other', value: 5 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const modelPerformanceData = [
  { epoch: 0.27, train_loss: 1.361000, accuracy: 0.65, validation_loss: 1.45 },
  { epoch: 0.55, train_loss: 0.907700, accuracy: 0.72, validation_loss: 1.12 },
  { epoch: 0.82, train_loss: 0.802800, accuracy: 0.78, validation_loss: 0.95 },
  { epoch: 1.09, train_loss: 0.785500, accuracy: 0.81, validation_loss: 0.88 },
  { epoch: 1.36, train_loss: 0.744500, accuracy: 0.83, validation_loss: 0.82 },
  { epoch: 1.64, train_loss: 0.694600, accuracy: 0.85, validation_loss: 0.79 },
  { epoch: 1.91, train_loss: 0.676800, accuracy: 0.86, validation_loss: 0.77 },
  { epoch: 2.18, train_loss: 0.682100, accuracy: 0.87, validation_loss: 0.76 },
  { epoch: 2.45, train_loss: 0.670100, accuracy: 0.88, validation_loss: 0.75 },
  { epoch: 2.73, train_loss: 0.657200, accuracy: 0.89, validation_loss: 0.74 },
  { epoch: 3.00, train_loss: 0.664700, accuracy: 0.89, validation_loss: 0.74 }
];

const modelMetrics = {
  currentAccuracy: 89,
  bestAccuracy: 89,
  averageResponseTime: 0.8,
  modelSize: "1.2GB",
  lastTrainingDate: "2024-03-07",
  totalTrainingTime: "2.5 hours"
};

export default function AnalyticsPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Queries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,120</div>
            <p className="text-xs text-muted-foreground">+12% from last week</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">85%</div>
            <Progress value={85} className="mt-2" />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1.8s</div>
            <p className="text-xs text-muted-foreground">-0.2s from last week</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">450</div>
            <p className="text-xs text-muted-foreground">+8% from last week</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Daily Queries</CardTitle>
                <CardDescription>Number of queries handled per day</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={dailyQueries}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="queries" stroke="#8884d8" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>User Satisfaction</CardTitle>
                <CardDescription>Distribution of user satisfaction ratings</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={satisfactionData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {satisfactionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Response Time Distribution</CardTitle>
              <CardDescription>Distribution of response times for queries</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={responseTimeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="categories" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Query Categories</CardTitle>
              <CardDescription>Distribution of queries by category</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Model Training Progress</CardTitle>
                <CardDescription>Training and validation loss over epochs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={modelPerformanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="epoch" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="train_loss" stroke="#8884d8" name="Training Loss" />
                      <Line type="monotone" dataKey="validation_loss" stroke="#82ca9d" name="Validation Loss" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Model Accuracy</CardTitle>
                <CardDescription>Training accuracy over epochs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={modelPerformanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="epoch" />
                      <YAxis domain={[0, 1]} />
                      <Tooltip />
                      <Line type="monotone" dataKey="accuracy" stroke="#ff7300" name="Accuracy" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Current Accuracy</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{modelMetrics.currentAccuracy}%</div>
                <Progress value={modelMetrics.currentAccuracy} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Model Size</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{modelMetrics.modelSize}</div>
                <p className="text-xs text-muted-foreground">Last updated: {modelMetrics.lastTrainingDate}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Training Time</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{modelMetrics.totalTrainingTime}</div>
                <p className="text-xs text-muted-foreground">Average response time: {modelMetrics.averageResponseTime}s</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}