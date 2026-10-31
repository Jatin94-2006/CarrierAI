// CareerAI Mock Data and State Architecture
// STRICT REQUIREMENT: ZERO EMOJIS ANYWHERE. All visuals use Lucide icons & CSS.

export const CANDIDATE_PROFILE = {
  name: "Candidate",
  email: "",
  role: "Software Engineer",
  targetCompany: "",
  experienceLevel: "Pending Assessment",
  resumeScore: null,
  jobMatchScore: null,
  interviewReadiness: null,
  isAssessed: false,
  skills: [],
  recentActivity: []
};

export const SAMPLE_JOB_DESCRIPTION = `Job Title: Full Stack Developer (React & Node.js)
Company: Nexus Innovations
Location: Remote / Hybrid

About The Role:
We are looking for an ambitious Full Stack Developer to build robust, scalable web applications. You will collaborate closely with product managers and designers to engineer responsive user interfaces and high-performance backend microservices.

Key Responsibilities:
• Build modern, high-performance web applications using React.js, TypeScript, and Tailwind CSS.
• Design, implement, and maintain RESTful APIs and backend services using Node.js, Express, and MongoDB.
• Write clean, testable, and maintainable code with unit and integration tests (Jest, React Testing Library).
• Manage application containerization and deployments with Docker and CI/CD pipelines (GitHub Actions).
• Optimize web applications for maximum speed, scalability, and SEO compliance.

Requirements & Technical Qualifications:
• Strong command of core JavaScript (ES6+), HTML5, and CSS3.
• 1+ years experience building production apps with React (Hooks, Context, State Management).
• Experience developing backend services with Node.js and Express.
• Hands-on database design with MongoDB (NoSQL) or PostgreSQL (Relational).
• Proficiency with Git version control, branching strategies, and pull requests.
• Familiarity with Docker, cloud environments (AWS/GCP), and modern CI/CD pipelines is a plus.
• Excellent communication, problem-solving, and collaboration mindset.`;

// High-Score Result (Score >= 75)
export const HIGH_SCORE_ANALYSIS = {
  overallScore: 82,
  status: "Strong Profile",
  summary: "Your resume has a strong alignment with the target Full Stack Developer role. Your frontend foundations and project portfolio satisfy core benchmarks.",
  isInterviewReady: true,
  categories: [
    { name: "Resume Quality", score: 88, benchmark: 75, desc: "ATS syntax, section hierarchy, and clean typography" },
    { name: "Technical Skills", score: 84, benchmark: 80, desc: "JavaScript, HTML5, CSS3, and React fundamentals" },
    { name: "Experience Relevance", score: 76, benchmark: 70, desc: "1.5 years frontend project experience" },
    { name: "Projects", score: 85, benchmark: 75, desc: "Production-grade portfolio and GitHub activity" },
    { name: "Education", score: 80, benchmark: 70, desc: "Computer Science coursework and certifications" },
    { name: "Job Description Match", score: 82, benchmark: 75, desc: "Direct coverage of primary required frameworks" }
  ]
};

// Low-Score Result (Score < 75) - Triggers automatic gap analysis
export const LOW_SCORE_ANALYSIS = {
  overallScore: 64,
  status: "Developing Profile",
  summary: "Your resume shows good foundational knowledge, but currently presents notable gaps in backend architecture, database modeling, and containerization required for this role.",
  isInterviewReady: false,
  categories: [
    { name: "Resume Quality", score: 72, benchmark: 75, desc: "Formatting is clear, but quantifiable impact metrics are needed" },
    { name: "Technical Skills", score: 62, benchmark: 80, desc: "Frontend is acceptable; backend lacks Node and MongoDB depth" },
    { name: "Experience Relevance", score: 58, benchmark: 70, desc: "Limited evidence of multi-tier full stack production experience" },
    { name: "Projects", score: 68, benchmark: 75, desc: "Projects emphasize client-side logic rather than full stack APIs" },
    { name: "Education", score: 75, benchmark: 70, desc: "Strong academic background in engineering basics" },
    { name: "Job Description Match", score: 54, benchmark: 75, desc: "Critical deficit in 3 required backend qualifications" }
  ]
};

// Detailed Gap Analysis (Used when score < 75)
export const DETAILED_GAP_DATA = {
  heading: "Areas to Improve",
  subtitle: "These skills and areas are currently limiting your match with the target role.",
  strongSkills: [
    { name: "HTML5", level: 95, required: 85, status: "strong", desc: "Semantic tags, accessibility (a11y), responsive structures" },
    { name: "CSS3 & Styling", level: 90, required: 80, status: "strong", desc: "Flexbox, CSS Grid, animations, responsive design" },
    { name: "JavaScript (ES6+)", level: 88, required: 85, status: "strong", desc: "Closures, promises, async/await, array methods" },
    { name: "Git & GitHub", level: 82, required: 75, status: "strong", desc: "Branching, PRs, merge conflict resolution" }
  ],
  needsImprovement: [
    { name: "React.js", level: 45, required: 85, gap: 40, status: "moderate", desc: "Component lifecycle, custom hooks, context API, state optimization" },
    { name: "TypeScript", level: 35, required: 80, gap: 45, status: "moderate", desc: "Interfaces, generics, type guards, strict typing in React" },
    { name: "REST APIs", level: 55, required: 85, gap: 30, status: "moderate", desc: "HTTP verbs, status codes, JWT authentication, error handling" }
  ],
  missingSkills: [
    { name: "Node.js & Express", level: 20, required: 80, gap: 60, status: "missing", desc: "Server architecture, middleware, asynchronous I/O, routing" },
    { name: "MongoDB & Mongoose", level: 25, required: 75, gap: 50, status: "missing", desc: "Schema design, aggregation pipelines, indexing, CRUD operations" },
    { name: "Docker & Containerization", level: 10, required: 70, gap: 60, status: "missing", desc: "Dockerfiles, multi-stage builds, docker-compose for dev" }
  ],
  recommendations: [
    {
      id: "rec-1",
      skill: "React.js",
      title: "Modern React & Hooks Architecture",
      badge: "freeCodeCamp",
      level: "Beginner -> Intermediate",
      estimatedHours: "8 hours",
      whyMatters: "React is strongly required for the target role, while your current resume provides limited evidence of practical React custom hooks and state management.",
      link: "https://www.freecodecamp.org"
    },
    {
      id: "rec-2",
      skill: "Node.js & Express",
      title: "Backend Microservices with Node.js & Express",
      badge: "Microsoft Learn",
      level: "Zero -> Production Ready",
      estimatedHours: "10 hours",
      whyMatters: "The job requires microservices and backend API design where your profile currently shows a 60% skill deficit.",
      link: "https://learn.microsoft.com"
    },
    {
      id: "rec-3",
      skill: "MongoDB",
      title: "Database Modeling with MongoDB & Mongoose",
      badge: "MongoDB University",
      level: "Intermediate",
      estimatedHours: "6 hours",
      whyMatters: "Full Stack roles at Nexus Innovations require hands-on schema modeling and indexed querying for high volume applications.",
      link: "https://university.mongodb.com"
    },
    {
      id: "rec-4",
      skill: "Docker",
      title: "Containerization with Docker & Docker Compose",
      badge: "NPTEL",
      level: "Fundamental",
      estimatedHours: "4 hours",
      whyMatters: "Containerization is standard across their CI/CD deployment pipelines for reproducible local microservice orchestration.",
      link: "https://nptel.ac.in"
    }
  ],
  finalReportMetrics: {
    overallScore: 64,
    technicalMatch: 62,
    experienceMatch: 58,
    projectRelevance: 68,
    resumeQuality: 72,
    jobMatch: 54
  },
  strengths: [
    "Solid understanding of frontend foundational standards (HTML5, CSS3, modern ES6+)",
    "Consistent Git version control usage and GitHub repository contributions",
    "Clean resume formatting with clear educational credentials"
  ],
  areasToImprove: [
    "Bridge the 60% deficit in backend server programming with Node.js and Express",
    "Add full-stack database implementations (MongoDB or PostgreSQL) to personal portfolio",
    "Incorporate automated unit testing and containerization (Docker) into project descriptions"
  ],
  missingSkillsList: [
    "Node.js & Express microservice design",
    "MongoDB / NoSQL schema design & indexing",
    "Docker containerization & multi-stage builds"
  ],
  recommendedActions: [
    "Complete the 8-hour React State Management masterclass on freeCodeCamp",
    "Build a full-stack CRUD API connecting Node.js to MongoDB Atlas with JWT authentication",
    "Containerize your full-stack application using docker-compose and link the repo on your resume",
    "Re-analyze your profile in CareerAI once backend projects are committed to GitHub"
  ]
};

// Mock Questions for AI Interview
export const MOCK_INTERVIEW_QUESTIONS = [
  {
    id: 1,
    question: "Tell me about yourself, your background in web development, and your experience with modern React.",
    category: "Introduction & Experience",
    durationSeconds: 90,
    idealKeywords: ["React Hooks", "Component Lifecycle", "Full Stack projects", "Problem solving"],
    aiSpeech: "Welcome Krish. Let's start with your background. Walk me through your journey in web development and your hands-on experience building applications with React.",
    applicantSampleAnswer: "I am Krish Sharma, a developer focused on modern web applications. Over the past year, I have built several projects using React, HTML5, and JavaScript. I work primarily with functional components, useState, and useEffect, and I prioritize building responsive, accessible web interfaces.",
    score: 8.5,
    feedback: "Good introduction and clear tone. Could be strengthened by highlighting quantifiable impact and state management examples."
  },
  {
    id: 2,
    question: "What is the Virtual DOM in React, and how does reconciliation work when a state change occurs?",
    category: "React Core Concepts",
    durationSeconds: 90,
    idealKeywords: ["Diffing algorithm", "Real DOM updates", "Batching", "Render tree"],
    aiSpeech: "Now dive into React's core mechanics. Explain what the Virtual DOM is and how the diffing and reconciliation algorithm updates the actual DOM.",
    applicantSampleAnswer: "The Virtual DOM is an in-memory representation of the real DOM tree. When component state changes, React creates a new Virtual DOM tree and compares it with the previous one using its diffing algorithm. It calculates the minimal set of changes needed and batches them into the real DOM efficiently.",
    score: 8.8,
    feedback: "Strong technical explanation of the reconciliation cycle with accurate terminology."
  },
  {
    id: 3,
    question: "Explain the architecture of a REST API. What HTTP status codes would you return for validation failure versus an unauthenticated request?",
    category: "Backend & HTTP",
    durationSeconds: 90,
    idealKeywords: ["Statelessness", "400 Bad Request", "401 Unauthorized", "403 Forbidden", "JSON payload"],
    aiSpeech: "Next question: Explain how a RESTful API works, and tell me the specific HTTP status codes you would return for invalid request payloads versus missing authentication credentials.",
    applicantSampleAnswer: "REST stands for Representational State Transfer and relies on stateless client-server communication using standard HTTP methods like GET, POST, PUT, and DELETE. For validation errors or malformed input, I return a 400 Bad Request or 422 Unprocessable Entity. For missing or invalid credentials, I return 401 Unauthorized.",
    score: 9.0,
    feedback: "Flawless precision on HTTP status codes and REST architecture principles."
  },
  {
    id: 4,
    question: "How do you handle asynchronous operations in Node.js, and what is the difference between synchronous blocking code and the event loop?",
    category: "Node.js Fundamentals",
    durationSeconds: 90,
    idealKeywords: ["Event Loop", "Libuv", "Promises", "Async/Await", "Non-blocking I/O"],
    aiSpeech: "Moving on to backend runtimes: How does Node.js handle asynchronous operations without getting blocked on single-threaded execution?",
    applicantSampleAnswer: "Node.js executes single-threaded JavaScript code via the V8 engine, but utilizes libuv and the event loop with worker thread pools to offload asynchronous I/O tasks like file access or database queries. Using async/await and Promises lets us write clean non-blocking code.",
    score: 8.2,
    feedback: "Clear conceptual understanding. Recommended to practice explaining microtasks versus macrotasks queues."
  },
  {
    id: 5,
    question: "Describe a scenario where you faced a tough bug in your application. How did you debug and resolve it?",
    category: "Problem Solving & STAR",
    durationSeconds: 100,
    idealKeywords: ["STAR method", "Browser DevTools", "Network tab", "Root cause analysis", "Resolution"],
    aiSpeech: "Tell me about a challenging bug you encountered in a recent project. How did you diagnose it, trace the root cause, and verify the fix?",
    applicantSampleAnswer: "In an e-commerce cart prototype, items were occasionally duplicating upon rapid checkout clicks. I inspected the Network tab and console logs in Chrome DevTools. I discovered the submit button wasn't disabled during network transit, triggering concurrent POST requests. I implemented a debounced handler and disabled state flag.",
    score: 8.4,
    feedback: "Great real-world scenario and structured troubleshooting workflow using the STAR framework."
  }
];

// Interview Final Performance Report (Used when candidate completed interview)
export const INTERVIEW_REPORT_DATA = {
  candidateName: "Candidate",
  targetRole: "Full Stack Developer",
  date: "October 30, 2026",
  overallScore: 78,
  performanceGrade: "Good Performance",
  readinessRating: "Job-Ready with Targeted Practice",
  metrics: {
    technicalKnowledge: 82,
    communication: 74,
    problemSolving: 80,
    confidence: 71,
    answerRelevance: 85
  },
  strengths: [
    "Good technical fundamentals in core JavaScript, DOM operations, and React Virtual DOM concepts",
    "Precise recall of HTTP status codes, RESTful API principles, and asynchronous programming",
    "Relevant project experience solving real-world UI edge cases (debouncing & network race conditions)"
  ],
  areasToImprove: [
    "Explain technical concepts more clearly with tangible production architecture examples",
    "Improve confidence by reducing filler words during open-ended questions",
    "Give more structured answers using the STAR method for behavioral questions"
  ],
  aiCoachFeedback: "You have a strong technical foundation, but your answers can become more structured and confident. Focus on explaining concepts using simple examples and using the STAR method for behavioral questions. With 2 more practice iterations on backend systems and Docker, your interview readiness will jump past 88%.",
  questionAnalyses: [
    {
      qNum: 1,
      question: "Tell me about yourself, your background, and your experience with React.",
      score: 8.5,
      category: "Introductory",
      feedback: "Good introduction but the answer could be more structured by highlighting quantifiable impact."
    },
    {
      qNum: 2,
      question: "What is the Virtual DOM in React, and how does reconciliation work?",
      score: 8.8,
      category: "Technical",
      feedback: "Accurate description of diffing and batching. Adding a brief mention of React Fiber would elevate this answer."
    },
    {
      qNum: 3,
      question: "Explain REST API architecture and HTTP status codes for errors.",
      score: 9.0,
      category: "Technical Architecture",
      feedback: "Strong technical explanation with clear distinction between 400 Bad Request and 401 Unauthorized."
    },
    {
      qNum: 4,
      question: "How do you handle asynchronous operations in Node.js?",
      score: 8.2,
      category: "Backend Systems",
      feedback: "Solid grasp of non-blocking I/O and Promises. Recommended to practice explaining the Event Loop microtask queue."
    },
    {
      qNum: 5,
      question: "Describe a tough bug you encountered and how you solved it.",
      score: 8.4,
      category: "Behavioral / Problem Solving",
      feedback: "Well-articulated debugging example showing practical use of browser developer tools and race condition fixes."
    }
  ]
};
