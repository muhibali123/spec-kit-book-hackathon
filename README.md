# Spec-Kit Book Hackathon 📚🤖

**Spec-Kit Book Hackathon** is a cutting-edge educational platform created for the GIAIC AI/Spec-Driven Online Hackathon. This project combines interactive documentation with AI-driven learning assistance, making it easy for users to explore content and get instant help through an integrated RAG (Retrieval-Augmented Generation) chatbot.  

---

## 🌟 Features

- **Interactive Learning Platform:** Built using **Docusaurus**, providing a clean, fast, and organized documentation experience.  
- **RAG AI Chatbot Integration:** Users can ask questions about the content and get instant AI-generated answers using **OpenAI Agents / ChatKit SDKs**.  
- **Dynamic & Searchable Content:** Easy navigation through chapters and lessons with a fully structured sidebar.  
- **Modern UI Components:** Responsive and visually appealing interface with custom components like Hero sections, Features, and TOC previews.  
- **Fast Deployment:** Deployed on **GitHub Pages** for instant access and easy sharing.  

---

## 📂 Project Structure

Physical-AI-humanoid/
├─ chapters/ # All chapter lessons (.mdx files)
├─ src/
│ ├─ components/ # Custom React components
│ ├─ pages/ # Static pages like Home, About
│ └─ css/ # Styling for custom components
├─ static/ # Images, icons, and other static assets
├─ docusaurus.config.ts # Docusaurus configuration
├─ package.json # Project dependencies
└─ README.md # Project documentation

yaml
Copy code

---

## ⚙️ Installation & Setup

To run this project locally:

```bash
# Clone the repository
git clone https://github.com/<your-username>/spec-kit-book-hackathon.git

# Navigate to the project folder
cd spec-kit-book-hackathon

# Install dependencies
npm install

# Run locally
npm start
Visit http://localhost:3000 to explore the platform.

🚀 Deployment
This project is deployed on GitHub Pages. The latest version can be accessed here.

🛠️ Tech Stack
Frontend & Docs: Docusaurus

AI Integration: OpenAI Agents / ChatKit SDKs

Backend (Optional): FastAPI + Qdrant Cloud

Styling: Tailwind CSS + Custom CSS

Deployment: GitHub Pages

🤝 Contribution
Contributions, suggestions, and feedback are welcome! Please create a pull request or open an issue for improvements.

📜 License
This project is licensed under the MIT License.

⚡ Hackathon Notes
This project was created as part of the GIAIC AI/Spec-Driven Online Hackathon.

The main goal was to create a book with interactive AI features for fast learning and reference.
