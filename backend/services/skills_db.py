# Common technical skills for deterministic matching
SKILLS_DB = {
    "languages": {
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "sql", "html", "css", "bash", "shell"
    },
    "frameworks": {
        "react", "angular", "vue", "svelte", "next.js", "nuxt", "node.js", "express", "fastapi", "flask", "django", "spring", "springboot", "laravel", "rails", ".net", "flutter", "react native", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy"
    },
    "tools": {
        "git", "docker", "kubernetes", "aws", "azure", "gcp", "jenkins", "gitlab ci", "github actions", "circleci", "jira", "confluence", "slack", "trello", "asana", "figma", "postman", "swagger", "redis", "mongodb", "postgresql", "mysql", "oracle", "elasticsearch",
        "excel", "word", "powerpoint", "office suite", "microsoft office", "google workspace", "vlookup", "pivot tables", "spreadsheet"
    },
    "concepts": {
        "rest api", "graphql", "microservices", "serverless", "ci/cd", "agile", "scrum", "devops", "machine learning", "deep learning", "nlp", "computer vision", "distributed systems", "cloud computing", "big data", "data science", "cybersecurity", "blockchain"
    },
    "soft_skills": {
        "communication", "problem-solving", "problem solving", "time management", "collaboration", "teamwork", "adaptability", "leadership", "critical thinking", "attention to detail", "presentation", "public speaking", "research", "analytical", "organization"
    }
}

# Flattened set for easy lookup
ALL_SKILLS = set()
for category in SKILLS_DB.values():
    ALL_SKILLS.update(category)
