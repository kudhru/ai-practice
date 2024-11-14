'use client'

import React, { useState, useEffect } from 'react'
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, CheckCircle, XCircle, HelpCircle, Settings, Menu } from "lucide-react"
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
import { DropdownSelector } from "@/components/ui/dropdown-selector"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { LoadingOverlay } from "@/components/ui/loading-overlay"

// Dynamically import Monaco Editor to avoid SSR issues
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false })

interface TestCase {
  input: string
  expectedOutput: string
}

interface Question {
  id?: number
  name: string
  text: string
  testCases: TestCase[]
  hint: string
  programming_language: string
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
  programming_language: string
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

// Add proper error types
interface ApiError {
  status?: number;
  message: string;
}

// Add API URL from environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const LANGUAGE_OPTIONS = [
  { value: 'ocaml', label: 'OCaml' },
  { value: 'java', label: 'Java' },
  { value: 'c', label: 'C' }
];

const apiCall = async (endpoint: string, method: string, body?: unknown, token?: string) => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  try {
    const response = await fetch(`${API_URL}/api/${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      if (response.status === 401) {
        auth.removeToken();
        throw { status: 401, message: 'Session expired. Please login again.' } as ApiError;
      }
      throw { status: response.status, message: errorData.detail || 'API call failed' } as ApiError;
    }

    return response.json()
  } catch (error) {
    console.error(`API call to ${endpoint} failed:`, error)
    throw error as ApiError;
  }
}

function LoginForm({ onLogin }: { onLogin: (token: string) => void }) {
  const [error, setError] = useState<string | null>(null)

  const handleGoogleSuccess = async (response: { credential?: string }) => {
    try {
      if (!response?.credential) {
        setError('No credentials received from Google');
        return;
      }

      // Pass the credential (ID token) to your backend
      onLogin(response.credential);
    } catch (error) {
      const apiError = error as ApiError;
      console.error('Login error:', apiError);
      setError(apiError.message || 'Login failed. Please try again.');
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

// Add this helper function before QuestionSettingsForm
const getTopicsForLanguage = (language: string) => {
  switch (language) {
    case 'java':
      return ['Arrays', 'Strings', 'Inheritance', 'Polymorphism', 'Lists', 'Maps', 'Sets', 'Generics', 'Thread Pools'];
    case 'c':
      return ['Arrays', 'Strings', 'Dynamic Memory Allocation', 'Lists', 'Sorting'];
    case 'ocaml':
      return ['Functions', 'Recursive Functions', 'Pattern Matching', 'Lists', 'Arrays', 'Strings', 'Sorting', 'Map', 'Fold'];
    default:
      return [];
  }
};

function QuestionSettingsForm({ initialSettings, onSave }: { initialSettings: QuestionParams; onSave: (params: QuestionParams) => void }) {
  const [difficulty, setDifficulty] = useState(initialSettings.difficulty);
  const [topics, setTopics] = useState(initialSettings.topics);
  const [isSaved, setIsSaved] = useState(false);

  // Add useEffect to update form when initialSettings change
  useEffect(() => {
    setDifficulty(initialSettings.difficulty);
    setTopics(initialSettings.topics);
  }, [initialSettings]);

  const handleTopicChange = (topic: string) => {
    setTopics(prev => 
      prev.includes(topic) ? prev.filter(t => t !== topic) : [...prev, topic]
    );
  };

  const handleSave = () => {
    onSave({ 
      difficulty, 
      topics, 
      programming_language: initialSettings.programming_language 
    });
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  // Get topics based on current programming language
  const allTopics = getTopicsForLanguage(initialSettings.programming_language);

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
  );
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

function CodeEditor({ code, onChange, language }: { code: string; onChange: (value: string) => void; language: string }) {
  return (
    <Card className="h-[calc(100vh-16rem)]">
      <CardHeader className="py-2">
        <CardTitle>Code Editor</CardTitle>
      </CardHeader>
      <CardContent className="p-0 h-[calc(100%-3rem)]">
        <MonacoEditor
          height="100%"
          language={language}
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

export default function QuizEnhanced() {
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
    topics: ['Lists', 'Maps', 'Sets'],
    programming_language: 'java'
  })
  const [isGeneratingQuestion, setIsGeneratingQuestion] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [solvedQuestions, setSolvedQuestions] = useState<SolvedQuestion[]>([])
  const [isSidebarVisible, setIsSidebarVisible] = useState(true)
  const [initialQuestionLoaded, setInitialQuestionLoaded] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState('java');

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

  const handleGenerateQuestion = async (settings?: QuestionParams) => {
    if (!token) return;

    setIsGeneratingQuestion(true);
    setError(null);
    setGenerationProgress(0);
    
    try {
      // First fetch solved questions
      console.log('Updating the solved questions');
      const updatedSolvedQuestions = await apiCall('solved_questions', 'GET', null, token);
      console.log('Updated solved questions:', updatedSolvedQuestions);
      setSolvedQuestions(updatedSolvedQuestions);

      const question = await apiCall(
        'generate_question', 
        'POST', 
        settings || questionSettings,  // Use passed settings if available
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
        question: question,
        programming_language: selectedLanguage
      }, token);
      
      setTestResults(response.results);
    } catch (error) {
      const apiError = error as ApiError;
      setError(apiError.message || 'Failed to run test cases. Please try again.');
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
        question: question,
        programming_language: selectedLanguage,
      }, token);
      
      setTestResults(response.results);
    } catch (error) {
      const apiError = error as ApiError;
      setError(apiError.message || 'Failed to run test cases. Please try again.');
      return;
    }

    try {
      const result = await apiCall('submit', 'POST', {
        code: code,
        question: question,
        test_results: testResults,
        programming_language: selectedLanguage
      }, token);
      
      setFeedback(result);
      
      const updatedSolvedQuestions = await apiCall('solved_questions', 'GET', null, token);
      setSolvedQuestions(updatedSolvedQuestions);
    } catch (error) {
      const apiError = error as ApiError;
      setError(apiError.message || 'Failed to submit answer. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  const handleSaveSettings = async (settings: QuestionParams) => {
    if (!token) {
      console.error('No authentication token available');
      setError('Please sign in to save settings');
      return;
    }

    try {
      const languageSettings = {
        difficulty: settings.difficulty,
        topics: settings.topics
      };
      
      await apiCall(
        `user/settings/${settings.programming_language}`, 
        'PUT', 
        languageSettings,
        token
      );
      setQuestionSettings(settings);
    } catch (error) {
      console.error('Failed to save settings:', error);
      setError('Failed to save settings. Please try again.');
    }
  };

  const handleSelectSolvedQuestion = (solvedQuestion: SolvedQuestion) => {
    setQuestion(solvedQuestion.question);
    setCode(solvedQuestion.userCode);
    setFeedback(solvedQuestion.feedback);
    setTestResults(solvedQuestion.testResults);
    setSelectedLanguage(solvedQuestion.question.programming_language);
  }

  const toggleSidebar = () => {
    setIsSidebarVisible(prev => !prev)
  }

  useEffect(() => {
    if (token && !question && !initialQuestionLoaded) {
      handleGenerateQuestion();
      setInitialQuestionLoaded(true);
    }
  }, [token, question, initialQuestionLoaded]);

  const handleLanguageChange = async (newLanguage: string) => {
    setSelectedLanguage(newLanguage);
    try {
      const settings = await apiCall(`user/settings/${newLanguage}`, 'GET', null, token!);
      setQuestionSettings({
        ...settings,
        programming_language: newLanguage
      });

      // Clear current question and feedback
      setQuestion(null);
      setFeedback(null);
      setTestResults([]);
      setCode('');

      // Generate new question with the updated language
      await handleGenerateQuestion({
        ...settings,
        programming_language: newLanguage
      });
    } catch (error) {
      const apiError = error as ApiError;
      console.error('Failed to handle language change:', apiError);
      setError(apiError.message || 'Failed to change language. Please try again.');
    }
  };

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
                <CardTitle>Login</CardTitle>
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
                  <h1 className="text-2xl font-bold">GenAI-Based Practice Tool For Programming</h1>
                </div>
                <div className="flex items-center gap-2">
                  <DropdownSelector
                    value={selectedLanguage}
                    onValueChange={handleLanguageChange}
                    options={LANGUAGE_OPTIONS}
                    placeholder="Select language"
                    className="w-[180px]"
                  />
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
                    <CodeEditor code={code} onChange={setCode} language={selectedLanguage} />
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
                                Here&apos;s a high-level approach to solve the problem:
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
                        onClick={() => handleGenerateQuestion()} 
                        className="w-full"
                        disabled={isGeneratingQuestion}
                      >
                        {isGeneratingQuestion ? 'Generating Question using GenAI...' : 'Generate New Question'}
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
      <LoadingOverlay 
        isLoading={isGeneratingQuestion || isSubmitting}
        message={isGeneratingQuestion ? "Generating Question using GenAI..." : "Submitting solution and generating feedback using GenAI..."}
      />
    </GoogleOAuthProvider>
  )
}