# Research Findings: Physical AI & Humanoid Robotics Course

## R1: Docusaurus Theme Selection

**Decision:** Use docusaurus-theme-classic with custom styling
**Rationale:** The classic theme provides the most flexibility for educational content with built-in support for sidebar navigation, code blocks, and MDX components. It's well-documented and widely used in educational contexts.
**Alternatives considered:**
- docusaurus-theme-bootstrap: More complex setup, less educational-focused
- Custom theme: Higher development time, maintenance overhead
- Infima-based themes: Limited educational features out-of-box

## R2: Educational Content Patterns

**Decision:** Follow established patterns from successful educational Docusaurus sites
**Rationale:** Research of existing educational Docusaurus implementations (like the official React documentation, TypeScript docs, and educational courses) shows that structured navigation with clear progression paths works best for learning.
**Best practices identified:**
- Clear hierarchy: Course → Chapters → Lessons → Subsections
- Consistent navigation with "previous/next" buttons
- Progress indicators for course completion
- Integrated search functionality
- Mobile-responsive design for learning on various devices

## R3: Interactive Elements Assessment

**Decision:** Use MDX components for interactive elements with external tools for complex simulations
**Rationale:** Docusaurus MDX supports React components, allowing for custom interactive elements like quizzes and code playgrounds. For complex robotics simulations, external tools like embedded Repl.it or CodeSandbox can be used.
**Strategy:**
- Simple code examples: Inline with Docusaurus code blocks
- Interactive quizzes: Custom MDX components
- Simulations: Embedded external tools or videos
- 3D models: Interactive viewers like Sketchfab embeds

## R4: Asset Management Strategy

**Decision:** Organized folder structure with optimized file formats
**Rationale:** Clear organization improves maintainability and performance. Optimized assets ensure fast loading times for learners.
**Asset management plan:**
- Images: Optimized PNG/JPG with WebP alternatives
- Diagrams: SVG for scalability, with PNG fallbacks
- Videos: MP4 format with proper compression
- Code samples: Organized by chapter/lesson with consistent naming
- Naming convention: [chapter-lesson]-[asset-type]-[description].[ext]