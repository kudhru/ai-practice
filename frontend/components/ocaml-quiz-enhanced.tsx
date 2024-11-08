'use client'

import React, { useState, useEffect } from 'react'
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, CheckCircle, XCircle, HelpCircle, Settings, Menu } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import dynamic from 'next/dynamic'
import { auth } from '@/utils/auth'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// Dynamically import Monaco Editor to avoid SSR issues
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false })

interface TestCase {
  input: string
  expectedOutput: string
}

interface Question {
  name: string
  text: string
  testCases: TestCase[]
  hint: string
}

interface Feedback {
  isCorrect: boolean
  feedback: string
  strengths: string[]
  weaknesses: string[]
}

interface QuestionParams {
  difficulty: string
  topics: string[]
}

interface SolvedQuestion {
  question: Question
  userCode: string
  feedback: Feedback
  testResults: TestCaseResult[]
}

// Add new interface extending TestCase
interface TestCaseResult extends TestCase {
  actualOutput: string;
}

// API call handler
const apiCall = async (endpoint: string, method: string, body?: any, token?: string) => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  console.log(`API Call to ${endpoint}:`, {
    method,
    headers,
    body,
  });

  try {
    const response = await fetch(`http://localhost:8000/api/${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error(`API Error:`, errorData);
      if (response.status === 401) {
        auth.removeToken();
        throw new Error('Session expired. Please login again.');
      }
      throw new Error(`API call failed: ${response.statusText}. ${JSON.stringify(errorData)}`)
    }

    return response.json()
  } catch (error) {
    console.error(`API call to ${endpoint} failed:`, error)
    throw error
  }
}

function LoginForm({ onLogin }: { onLogin: (token: string) => void }) {
  const [error, setError] = useState<string | null>(null)

  const handleGoogleSuccess = async (response: any) => {
    try {
      console.log('Google login response:', response);
      
      if (!response?.credential) {
        setError('No credentials received from Google');
        return;
      }

      // Pass the credential (ID token) to your backend
      onLogin(response.credential);
      
    } catch (error) {
      console.error('Login error:', error);
      setError('Login failed. Please try again.');
    }
  };

  return (
    <div className="space-y-4">
      <GoogleLogin
        onSuccess={handleGoogleSuccess}
        onError={() => setError('Google login failed. Please try again.')}
        useOneTap={false}
        auto_select={false}
        type="standard"
        theme="outline"
        size="large"
        width="300"
        context="signin"
      />
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  )
}

function QuestionSettingsForm({ initialSettings, onSave }: { initialSettings: QuestionParams; onSave: (params: QuestionParams) => void }) {
  const [difficulty, setDifficulty] = useState(initialSettings.difficulty)
  const [topics, setTopics] = useState(initialSettings.topics)
  const [isSaved, setIsSaved] = useState(false)

  const allTopics = [
    'Let and In expressions',
    'Let definitions',
    'Functions',
    'Recursive Functions',
    'Variants',
    'Records',
    'Tuples',
    'Pattern Matching',
    'Map',
    'Fold'
  ]

  const handleTopicChange = (topic: string) => {
    setTopics(prev => 
      prev.includes(topic) ? prev.filter(t => t !== topic) : [...prev, topic]
    )
  }

  const handleSave = () => {
    onSave({ difficulty, topics })
    setIsSaved(true)
    setTimeout(() => setIsSaved(false), 2000)
  }

  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="difficulty">Difficulty Level</Label>
        <Select value={difficulty} onValueChange={setDifficulty}>
          <SelectTrigger id="difficulty">
            <SelectValue placeholder="Select difficulty" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Easy">Easy</SelectItem>
            <SelectItem value="Medium">Medium</SelectItem>
            <SelectItem value="Hard">Hard</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label>Topics</Label>
        <div className="grid grid-cols-2 gap-2">
          {allTopics.map(topic => (
            <div key={topic} className="flex items-center space-x-2">
              <Checkbox 
                id={topic} 
                checked={topics.includes(topic)}
                onCheckedChange={() => handleTopicChange(topic)}
              />
              <Label htmlFor={topic}>{topic}</Label>
            </div>
          ))}
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <Button onClick={handleSave}>Save Settings</Button>
        {isSaved && <CheckCircle className="text-green-500 h-5 w-5" />}
      </div>
    </div>
  )
}

function QuestionPanel({ question }: { question: Question }) {
  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle>{question.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="prose dark:prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {question.text}
          </ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  )
}

function TestCasePanel({ testCases, testResults }: { 
  testCases: TestCase[]; 
  testResults: TestCaseResult[];
}) {
  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle>Test Cases</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {testCases.map((testCase, index) => (
            <div key={index} className="border p-3 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <div>
                    <span className="font-semibold mr-2">Input:</span>
                    <code>{testCase.input}</code>
                  </div>
                  <div>
                    <span className="font-semibold mr-2">Expected Output:</span>
                    <code>{testCase.expectedOutput}</code>
                  </div>
                  {testResults[index] && (
                    <div>
                      <span className="font-semibold mr-2">Actual Output:</span>
                      <code className={
                        testResults[index].actualOutput === testCase.expectedOutput 
                          ? "text-green-500" 
                          : "text-red-500"
                      }>
                        {testResults[index].actualOutput}
                      </code>
                    </div>
                  )}
                </div>
                {testResults[index] && (
                  testResults[index].actualOutput === testCase.expectedOutput ? (
                    <CheckCircle className="text-green-500 ml-4" />
                  ) : (
                    <XCircle className="text-red-500 ml-4" />
                  )
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function CodeEditor({ code, onChange }: { code: string; onChange: (value: string) => void }) {
  return (
    <Card className="h-[calc(100vh-16rem)]">
      <CardHeader className="py-2">
        <CardTitle>OCaml Code Editor</CardTitle>
      </CardHeader>
      <CardContent className="p-0 h-[calc(100%-3rem)]">
        <MonacoEditor
          height="100%"
          language="ocaml"
          theme="vs-dark"
          value={code}
          onChange={(value) => onChange(value || '')}
          options={{
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 14,
          }}
        />
      </CardContent>
    </Card>
  )
}

function FeedbackPanel({ feedback }: { feedback: Feedback }) {
  return (
    <Card className="mt-4">
      <CardHeader>
        <CardTitle className="flex items-center">
          {feedback.isCorrect ? (
            <><CheckCircle className="mr-2 text-green-500" /> Correct</>
          ) : (
            <><XCircle className="mr-2 text-red-500" /> Incorrect</>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="mb-4">{feedback.feedback}</p>
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-green-600">Strengths:</h3>
            <ul className="list-disc list-inside">
              {feedback.strengths.map((strength, index) => (
                <li key={index}>{strength}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-red-600">Areas for Improvement:</h3>
            <ul className="list-disc list-inside">
              {feedback.weaknesses.map((weakness, index) => (
                <li key={index}>{weakness}</li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function SolvedQuestionsSidebar({ solvedQuestions, onSelectQuestion }: { 
  solvedQuestions: SolvedQuestion[]; 
  onSelectQuestion: (question: SolvedQuestion) => void;
}) {
  return (
    <Card className="h-full overflow-auto">
      <CardHeader>
        <CardTitle>Solved Questions</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {solvedQuestions.map((solvedQuestion, index) => (
            <li key={index}>
              <Button 
                variant="ghost" 
                className="w-full justify-start" 
                onClick={() => onSelectQuestion(solvedQuestion)}
              >
                {solvedQuestion.question.name}
              </Button>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

export default function OcamlQuizEnhanced() {
  const [token, setToken] = useState<string | null>(null)
  const [question, setQuestion] = useState<Question | null>(null)
  const [code, setCode] = useState('')
  const [feedback, setFeedback] = useState<Feedback | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isRunningTests, setIsRunningTests] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [testResults, setTestResults] = useState<TestCaseResult[]>([]);
  const [questionSettings, setQuestionSettings] = useState<QuestionParams>({
    difficulty: 'Easy',
    topics: ['Functions', 'Recursive Functions']
  })
  const [isGeneratingQuestion, setIsGeneratingQuestion] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [solvedQuestions, setSolvedQuestions] = useState<SolvedQuestion[]>([])
  const [isSidebarVisible, setIsSidebarVisible] = useState(true)

  useEffect(() => {
    const validateExistingSession = async () => {
      const savedToken = auth.getToken();
      if (!savedToken) return;

      try {
        // Use the refresh endpoint to validate and refresh the token
        const refreshResponse = await apiCall(
          'refresh', 
          'POST', 
          null, 
          savedToken
        );

        if (refreshResponse.access_token) {
          // Session is still valid, update token and restore state
          auth.setToken(refreshResponse.access_token);
          setToken(refreshResponse.access_token);
          
          // Fetch user data
          const solvedQuestions = await apiCall(
            'solved_questions', 
            'GET', 
            null, 
            refreshResponse.access_token
          );
          setSolvedQuestions(solvedQuestions);
        }
      } catch (error) {
        // Token is invalid/expired, clear it
        console.error('Session refresh failed:', error);
        auth.removeToken();
      }
    };

    validateExistingSession();
  }, []);

  const handleLogin = async (googleCredential: string) => {
    try {
      console.log('Sending Google credential to backend...');
      
      // Send Google credential to backend
      const loginResponse = await apiCall('login', 'POST', { 
        token: googleCredential  // This should be the ID token
      });
      
      console.log('Login response:', loginResponse);
      
      if (loginResponse.session_token) {
        // Save the session token
        auth.setToken(loginResponse.session_token);
        setToken(loginResponse.session_token);
        
        // Fetch solved questions
        const solvedQuestions = await apiCall(
          'solved_questions', 
          'GET', 
          null, 
          loginResponse.session_token
        );
        setSolvedQuestions(solvedQuestions);
      } else {
        throw new Error('No session token received');
      }
    } catch (error) {
      console.error('Login failed:', error);
      auth.removeToken();
      setError('Login failed. Please try again.');
    }
  };

  // Add logout functionality
  const handleLogout = () => {
    auth.removeToken();
    setToken(null);
    setSolvedQuestions([]);
    setQuestion(null);
    setCode('');
    setFeedback(null);
  }

  const handleGenerateQuestion = async () => {
    if (!token) return;

    setIsGeneratingQuestion(true);
    setError(null);
    setGenerationProgress(0);
    
    try {
      console.log('Updating the solved questions');
      const updatedSolvedQuestions = await apiCall('solved_questions', 'GET', null, token);
      console.log('Updated solved questions:', updatedSolvedQuestions);
      
      setSolvedQuestions(updatedSolvedQuestions);
      console.log('Generating question with settings:', questionSettings);
      
      const question = await apiCall(
        'generate_question', 
        'POST', 
        questionSettings,
        token
      );
      
      console.log('Generated question:', question);
      setQuestion(question);
      setTestResults([]);
      setCode('');
      setFeedback(null);
    } catch (error) {
      console.error('Failed to generate question:', error);
      setError('Failed to generate question. Please try again.');
    } finally {
      setIsGeneratingQuestion(false);
      setGenerationProgress(0);
    }
  };

  const handleRunTests = async () => {
    if (!question || !token) return;

    setIsRunningTests(true);
    setError(null);
    
    try {
        const response = await apiCall('run_tests', 'POST', {
            code: code,
            question: question
        }, token);
        
        setTestResults(response.results);
    } catch (err) {
        setError('Failed to run test cases. Please try again.');
    } finally {
        setIsRunningTests(false);
    }
  }

  const handleSubmit = async () => {
    if (!question || !token) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await apiCall('run_tests', 'POST', {
          code: code,
          question: question
      }, token);
      
      setTestResults(response.results);
    } catch (err) {
      setError('Failed to run test cases. Please try again.');
    }

    try {
        const result = await apiCall('submit', 'POST', {
            code: code,
            question: question,
            test_results: testResults
        }, token);
        
        setFeedback(result);
        
        const updatedSolvedQuestions = await apiCall('solved_questions', 'GET', null, token);
        setSolvedQuestions(updatedSolvedQuestions);
    } catch (err) {
        setError('Failed to submit answer. Please try again.');
    } finally {
        setIsSubmitting(false);
    }
  }

  const handleSaveSettings = (newSettings: QuestionParams) => {
    setQuestionSettings(newSettings)
  }

  const handleSelectSolvedQuestion = (solvedQuestion: SolvedQuestion) => {
    setQuestion(solvedQuestion.question)
    setCode(solvedQuestion.userCode)
    setFeedback(solvedQuestion.feedback)
    setTestResults(solvedQuestion.testResults)
  }

  const toggleSidebar = () => {
    setIsSidebarVisible(prev => !prev)
  }

  useEffect(() => {
    if (token && !question) {
      handleGenerateQuestion()
    }
  }, [token, questionSettings])

  const handleApiError = (error: any) => {
    if (error.status === 401) {
      auth.removeToken();
      setToken(null);
      setError('Session expired. Please login again.');
    }
    throw error;
  }

  return (
    <GoogleOAuthProvider 
      clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ''}
      onScriptLoadError={() => console.error('Google script failed to load:')}
    >
      <div className="container mx-auto p-4 min-h-screen flex flex-col">
        {!token ? (
          <div className="flex items-center justify-center flex-grow">
            <Card className="w-96">
              <CardHeader>
                <CardTitle>Log In to OCaml Quiz</CardTitle>
              </CardHeader>
              <CardContent>
                <LoginForm onLogin={handleLogin} />
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="flex-grow flex">
            {isSidebarVisible && (
              <div className="w-64 transition-all duration-300 ease-in-out">
                <SolvedQuestionsSidebar 
                  solvedQuestions={solvedQuestions} 
                  onSelectQuestion={handleSelectSolvedQuestion}
                />
              </div>
            )}
            <div className="flex-grow flex flex-col ml-4">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center">
                  <Button 
                    variant="outline" 
                    size="icon" 
                    onClick={toggleSidebar} 
                    className="mr-2"
                    aria-label={isSidebarVisible ? "Hide solved questions" : "Show solved questions"}
                  >
                    <Menu className="h-4 w-4" />
                  </Button>
                  <h1 className="text-2xl font-bold">OCaml Quiz</h1>
                </div>
                <div className="flex items-center gap-2">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="outline" size="icon">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Question Settings</DialogTitle>
                      </DialogHeader>
                      <QuestionSettingsForm 
                        initialSettings={questionSettings} 
                        onSave={handleSaveSettings} 
                      />
                    </DialogContent>
                  </Dialog>
                  <Button variant="outline" onClick={handleLogout}>
                    Logout
                  </Button>
                </div>
              </div>
              {error && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}
              {question ? (
                <div className="flex-grow flex flex-col lg:flex-row gap-4">
                  <div className="w-full lg:w-1/2 space-y-4">
                    <QuestionPanel question={question} />
                    <TestCasePanel testCases={question.testCases} testResults={testResults} />
                  </div>
                  <div className="w-full lg:w-1/2 flex flex-col">
                    <CodeEditor code={code} onChange={setCode} />
                    <div className="mt-4 space-y-2">
                      <div className="flex justify-between">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button variant="outline">
                              <HelpCircle className="mr-2 h-4 w-4" />
                              Hint
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Hint</DialogTitle>
                              <DialogDescription>
                                Here's a high-level approach to solve the problem:
                              </DialogDescription>
                            </DialogHeader>
                            <pre className="bg-muted p-4 rounded-md whitespace-pre-wrap">
                              {question.hint}
                            </pre>
                          </DialogContent>
                        </Dialog>
                        <Button onClick={handleRunTests} disabled={isRunningTests}>
                          {isRunningTests ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Running Tests...
                            </>
                          ) : (
                            'Run Tests'
                          )}
                        </Button>
                        <Button onClick={handleSubmit} disabled={isSubmitting}>
                          {isSubmitting ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Submitting...
                            </>
                          ) : (
                            'Submit'
                          )}
                        </Button>
                      </div>
                      <Button 
                        variant="outline" 
                        onClick={handleGenerateQuestion} 
                        className="w-full"
                        disabled={isGeneratingQuestion}
                      >
                        {isGeneratingQuestion ? 'Generating Question...' : 'Generate New Question'}
                      </Button>
                      {isGeneratingQuestion && (
                        <Progress value={generationProgress} className="w-full" />
                      )}
                    </div>
                    {feedback && <FeedbackPanel feedback={feedback} />}
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </GoogleOAuthProvider>
  )
}