# Quickstart Guide: Physical AI & Humanoid Robotics Course Development

## Setting Up Your Local Development Environment

### Prerequisites
- Node.js version 16 or higher
- npm or yarn package manager
- Git for version control
- A code editor (VS Code recommended)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd [repository-directory]
   ```

2. **Install dependencies**
   ```bash
   npm install
   # OR if using yarn
   yarn install
   ```

3. **Start the development server**
   ```bash
   npm run start
   # OR if using yarn
   yarn start
   ```
   This will start a local server at `http://localhost:3000` with live reloading.

4. **Open your browser** to `http://localhost:3000` to view the course.

## Creating New Content

### Adding a New Lesson

1. **Navigate to the appropriate chapter folder** in `/docs/physical-ai-humanoid-course/chapter-XX/`

2. **Create a new markdown file** with the naming convention `lesson-YY.md`

3. **Use the following template** for the new lesson:

```markdown
---
title: "Lesson Title"
sidebar_label: "Lesson YY: Lesson Title"
description: "Brief description of what students will learn"
keywords: ["keyword1", "keyword2", "keyword3"]
---

import { CourseLesson } from '@site/src/components/CourseLesson';

<CourseLesson>

## Learning Objectives

- Objective 1
- Objective 2
- Objective 3

## Key Concepts

- Concept 1
- Concept 2
- Concept 3

## Theory Summary

Provide a comprehensive explanation of the theoretical foundations relevant to this lesson topic.

## Hands-on Activity / Lab

Detailed practical exercise that allows students to apply the concepts learned.

## Tools & Components Required

- List of software, hardware, or other resources needed
- Installation instructions if necessary

## Code Snippets

If applicable, include relevant code examples with explanations.

## Step-by-step Instructions

1. Step 1 description
2. Step 2 description
3. Step 3 description

## Review Questions

1. Question 1?
2. Question 2?
3. Question 3?

## Mini Assessment / Quiz

Short assessment to evaluate comprehension of key concepts.

## Practical Task

Applied task that reinforces the lesson's core concepts.

## Expected Outcomes

Description of what students should be able to do after completing the lesson.

</CourseLesson>
```

### Creating New Assets

1. **Add images/diagrams** to `/docs/physical-ai-humanoid-course/assets/images/` or `/docs/physical-ai-humanoid-course/assets/diagrams/`

2. **Add code samples** to `/docs/physical-ai-humanoid-course/assets/code-samples/`

3. **Add videos** to `/docs/physical-ai-humanoid-course/assets/videos/`

4. **Reference assets** in lessons using relative paths:
   ```markdown
   ![Alt text](./assets/images/image-name.png)
   ```

## Content Creation Workflow

### From Draft to Published

1. **Create content draft** in the appropriate location
2. **Self-review** for accuracy, clarity, and adherence to the lesson template
3. **Commit changes** with descriptive commit messages
4. **Submit pull request** for team review
5. **Address feedback** from reviewers
6. **Merge to main branch** when approved
7. **Deploy** to production environment

### Review Process

- **Technical accuracy**: Verify all technical information is correct
- **Educational effectiveness**: Ensure content is clear and teaches the intended concepts
- **Accessibility**: Check that content is accessible to all learners
- **Consistency**: Verify adherence to style guide and formatting standards

## Common Commands

- `npm start` - Start local development server
- `npm run build` - Build static site for production
- `npm run serve` - Serve built site locally for testing
- `npm run docusaurus` - Display available Docusaurus commands
- `npm run deploy` - Deploy to configured hosting platform

## Troubleshooting

### Common Issues

**Issue**: Page doesn't update after changes
- **Solution**: Check that hot reloading is enabled and restart the development server if needed

**Issue**: Images not displaying
- **Solution**: Verify image paths are correct and files exist in the specified location

**Issue**: Code blocks not syntax highlighting
- **Solution**: Ensure language identifier is specified (e.g., ```javascript)

**Issue**: Sidebar navigation not showing new content
- **Solution**: Verify the new content is referenced in `sidebars.js` and follows naming conventions