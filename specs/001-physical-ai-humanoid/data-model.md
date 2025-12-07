# Data Model: Physical AI & Humanoid Robotics Course

## Course Structure

### Course
- **title**: "Physical AI & Humanoid Robotics Course"
- **chapters**: Array of Chapter objects
- **version**: string (semantic versioning)
- **metadata**: object containing course-wide information
- **description**: string (course overview)
- **prerequisites**: Array of prerequisite knowledge areas
- **estimatedDuration**: string (e.g., "12 weeks", "60 hours")

### Chapter
- **id**: string (format: "chapter-XX", e.g., "chapter-01")
- **title**: string (chapter title)
- **overview**: string (2-3 line description)
- **lessons**: Array of Lesson objects
- **position**: number (chapter number in sequence)
- **learningObjectives**: Array of strings (what learners will achieve)
- **prerequisites**: Array of prerequisite knowledge for the chapter
- **estimatedDuration**: string (time to complete chapter)

### Lesson
- **id**: string (format: "lesson-XX", e.g., "lesson-01")
- **title**: string (lesson title)
- **description**: string (1-2 sentence learning outcome)
- **learningObjectives**: Array of measurable objectives
- **keyConcepts**: Array of important terms/concepts
- **theorySummary**: string (explanation of theoretical foundations)
- **handsOnActivity**: string (detailed practical exercise)
- **toolsRequired**: Array of software/hardware requirements
- **codeSnippets**: Array of CodeSnippet objects
- **stepByStepInstructions**: Array of sequential instructions
- **reviewQuestions**: Array of questions to assess understanding
- **miniAssessment**: Array of Question objects
- **practicalTask**: string (applied task for reinforcement)
- **expectedOutcomes**: Array of what students should achieve
- **chapterId**: string (reference to parent chapter)
- **position**: number (lesson number within chapter)
- **duration**: string (estimated time to complete lesson)

### CodeSnippet
- **language**: string (programming language identifier)
- **code**: string (the actual code content)
- **explanation**: string (description of what the code does)
- **fileName**: string (optional filename for file-based examples)
- **isExecutable**: boolean (whether code can be run in a playground)

### Question
- **type**: enum ("multiple-choice" | "short-answer" | "practical" | "essay")
- **content**: string (the actual question text)
- **options**: Array of strings (for multiple-choice questions)
- **correctAnswer**: string | Array of strings (correct response(s))
- **explanation**: string (why this is the correct answer)
- **difficulty**: enum ("beginner" | "intermediate" | "advanced")

### Assessment
- **id**: string (unique identifier)
- **title**: string (assessment title)
- **type**: enum ("quiz" | "practical" | "project")
- **questions**: Array of Question objects
- **passingScore**: number (minimum score to pass)
- **timeLimit**: number (optional time limit in minutes)
- **associatedLessons**: Array of lesson IDs

### Asset
- **id**: string (unique identifier)
- **type**: enum ("image" | "diagram" | "video" | "code-sample" | "document")
- **path**: string (relative path from assets folder)
- **altText**: string (accessibility description)
- **caption**: string (optional descriptive text)
- **associatedLessons**: Array of lesson IDs
- **fileSize**: number (in bytes)
- **dimensions**: object (for images/videos: width, height)

## Relationships

- Course contains many Chapters (1:M)
- Chapter contains many Lessons (1:M)
- Lesson contains many CodeSnippets (1:M)
- Lesson contains many Questions (1:M)
- Lesson uses many Assets (M:M)
- Chapter contains many Assessments (1:M)

## Validation Rules

### Course Validation
- Must have 12 chapters exactly
- Each chapter must have 4 lessons exactly
- Title must not exceed 100 characters
- Description must be between 50-200 characters

### Chapter Validation
- Position must be between 1-12
- Title must not exceed 80 characters
- Overview must be between 20-100 characters
- Must have at least 3 learning objectives
- Estimated duration must follow format "X hours" or "X weeks"

### Lesson Validation
- Position must be between 1-4
- Title must not exceed 80 characters
- Description must be 1-2 sentences (10-40 words)
- Must have 3-7 learning objectives
- Must have 3-10 key concepts
- Hands-on activity must be at least 100 words
- Must include at least 1 code snippet if applicable
- Must have 3-8 review questions
- Must have 1-3 mini assessment questions
- Expected outcomes must be specific and measurable

### CodeSnippet Validation
- Language must be a supported syntax highlighting language
- Code must not exceed 200 lines
- Explanation must be between 10-100 characters

### Question Validation
- Content must be between 10-200 characters
- Multiple choice must have 2-6 options
- Correct answer must match one of the options for multiple-choice
- Difficulty must match the lesson's target audience

## State Transitions

### Content States
- **Draft**: Initial state, content is being created
- **Review**: Content submitted for review
- **Revised**: Content returned for changes
- **Approved**: Content approved for publication
- **Published**: Content live in the course
- **Deprecated**: Content marked for removal/revision

### Course Lifecycle
1. Course is created with basic structure
2. Chapters are developed and validated
3. Lessons are created within chapters
4. Content is reviewed and approved
5. Course is published and made available
6. Course is maintained and updated over time