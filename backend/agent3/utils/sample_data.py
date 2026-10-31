"""
Agent 3: Course Suggestion Agent
Sample / demo data used when API keys are not configured.
This gives a realistic output shape that the frontend and Agent 5 can consume.
"""

SAMPLE_TECHNICAL = [
    {
        "title": "Python Tutorial for Beginners – Full Course",
        "platform": "freeCodeCamp",
        "skill": "Python",
        "skill_category": "Technical",
        "difficulty": "Beginner",
        "description": "A comprehensive Python tutorial covering variables, loops, functions, OOP and more. Perfect for absolute beginners.",
        "url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
        "resource_type": "Video",
        "is_free": True,
        "thumbnail": "https://img.youtube.com/vi/rfscVS0vtbw/hqdefault.jpg",
        "duration": "4.5 hours",
        "source": "sample"
    },
    {
        "title": "Python Tutorial – W3Schools",
        "platform": "W3Schools",
        "skill": "Python",
        "skill_category": "Technical",
        "difficulty": "Beginner",
        "description": "Interactive Python tutorial covering syntax, data types, conditionals, loops, and built-in functions with live examples.",
        "url": "https://www.w3schools.com/python/",
        "resource_type": "Tutorial",
        "is_free": True,
        "thumbnail": None,
        "duration": "Self-paced",
        "source": "sample"
    },
    {
        "title": "Python – GeeksforGeeks",
        "platform": "GeeksforGeeks",
        "skill": "Python",
        "skill_category": "Technical",
        "difficulty": "Intermediate",
        "description": "In-depth Python articles covering core language features, libraries (NumPy, Pandas), and interview problems.",
        "url": "https://www.geeksforgeeks.org/python-programming-language/",
        "resource_type": "Tutorial",
        "is_free": True,
        "thumbnail": None,
        "duration": "Self-paced",
        "source": "sample"
    },
    {
        "title": "SQL Tutorial – W3Schools",
        "platform": "W3Schools",
        "skill": "SQL",
        "skill_category": "Technical",
        "difficulty": "Beginner",
        "description": "Learn SQL from scratch — SELECT, WHERE, JOIN, GROUP BY, subqueries, and more with interactive exercises.",
        "url": "https://www.w3schools.com/sql/",
        "resource_type": "Tutorial",
        "is_free": True,
        "thumbnail": None,
        "duration": "Self-paced",
        "source": "sample"
    },
    {
        "title": "SQLZoo – Interactive SQL Practice",
        "platform": "SQLZoo",
        "skill": "SQL",
        "skill_category": "Technical",
        "difficulty": "Beginner",
        "description": "Hands-on SQL practice with real databases. Covers SELECT basics through complex JOINs and window functions.",
        "url": "https://sqlzoo.net/wiki/SQL_Tutorial",
        "resource_type": "Tutorial",
        "is_free": True,
        "thumbnail": None,
        "duration": "Self-paced",
        "source": "sample"
    },
    {
        "title": "SQL for Data Science – Kaggle Learn",
        "platform": "Kaggle Learn",
        "skill": "SQL",
        "skill_category": "Technical",
        "difficulty": "Beginner",
        "description": "Free micro-course by Kaggle covering SQL basics for data science including BigQuery.",
        "url": "https://www.kaggle.com/learn/intro-to-sql",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "3 hours",
        "source": "sample"
    },
    {
        "title": "Power BI for Beginners – Microsoft Learn",
        "platform": "Microsoft Learn",
        "skill": "Power BI",
        "skill_category": "Technical",
        "difficulty": "Beginner",
        "description": "Official Microsoft Learn path for Power BI covering data modeling, DAX, and report building.",
        "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "8 hours",
        "source": "sample"
    },
    {
        "title": "Power BI Full Course – YouTube",
        "platform": "YouTube",
        "skill": "Power BI",
        "skill_category": "Technical",
        "difficulty": "Beginner",
        "description": "Complete Power BI tutorial from dashboard creation to publishing and sharing reports.",
        "url": "https://www.youtube.com/watch?v=TmhQCQr_4GE",
        "resource_type": "Video",
        "is_free": True,
        "thumbnail": "https://img.youtube.com/vi/TmhQCQr_4GE/hqdefault.jpg",
        "duration": "6 hours",
        "source": "sample"
    },
    {
        "title": "Machine Learning – Kaggle Learn",
        "platform": "Kaggle Learn",
        "skill": "Machine Learning",
        "skill_category": "Technical",
        "difficulty": "Beginner",
        "description": "Free hands-on ML course: model validation, overfitting, random forests and more with Kaggle notebooks.",
        "url": "https://www.kaggle.com/learn/intro-to-machine-learning",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "3 hours",
        "source": "sample"
    },
    {
        "title": "Machine Learning Specialization – Andrew Ng (Audit)",
        "platform": "Coursera (Audit Free)",
        "skill": "Machine Learning",
        "skill_category": "Technical",
        "difficulty": "Intermediate",
        "description": "World-famous ML course by Andrew Ng covering supervised learning, neural networks, and best practices. Audit for free.",
        "url": "https://www.coursera.org/specializations/machine-learning-introduction",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "~3 months",
        "source": "sample"
    },
    {
        "title": "Web Development Full Course – freeCodeCamp",
        "platform": "freeCodeCamp",
        "skill": "Web Development",
        "skill_category": "Technical",
        "difficulty": "Beginner",
        "description": "Complete web development curriculum covering HTML, CSS, JavaScript, responsive design and React.",
        "url": "https://www.freecodecamp.org/learn/",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "Self-paced",
        "source": "sample"
    },
    {
        "title": "Data Analytics – Google (via Coursera Audit)",
        "platform": "Coursera (Audit Free)",
        "skill": "Data Analytics",
        "skill_category": "Technical",
        "difficulty": "Beginner",
        "description": "Google's official data analytics certificate program. Covers spreadsheets, SQL, R, and Tableau. Audit for free.",
        "url": "https://www.coursera.org/professional-certificates/google-data-analytics",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "6 months",
        "source": "sample"
    },
]

SAMPLE_SOFT = [
    {
        "title": "Communication Skills – NPTEL",
        "platform": "NPTEL",
        "skill": "Communication",
        "skill_category": "Soft",
        "difficulty": "Beginner",
        "description": "Free NPTEL course on English communication for technical professionals covering writing, speaking, and presentations.",
        "url": "https://nptel.ac.in/courses/109/104/109104093/",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "12 weeks",
        "source": "sample"
    },
    {
        "title": "Business English Communication – SWAYAM",
        "platform": "SWAYAM",
        "skill": "Communication",
        "skill_category": "Soft",
        "difficulty": "Beginner",
        "description": "SWAYAM course on business communication and professional English for the workplace.",
        "url": "https://swayam.gov.in/nd1_noc19_hs45/preview",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "8 weeks",
        "source": "sample"
    },
    {
        "title": "Leadership & Management – TCS iON",
        "platform": "TCS iON",
        "skill": "Leadership",
        "skill_category": "Soft",
        "difficulty": "Beginner",
        "description": "Free TCS iON course on leadership styles, team management, and decision making for professionals.",
        "url": "https://learning.tcsionhub.in/hub/national/",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "Self-paced",
        "source": "sample"
    },
    {
        "title": "Leadership Skills – YouTube (Simon Sinek)",
        "platform": "YouTube",
        "skill": "Leadership",
        "skill_category": "Soft",
        "difficulty": "Beginner",
        "description": "A curated playlist of Simon Sinek's leadership talks covering trust, purpose, and team culture.",
        "url": "https://www.youtube.com/c/SimonSinek",
        "resource_type": "Playlist",
        "is_free": True,
        "thumbnail": None,
        "duration": "Self-paced",
        "source": "sample"
    },
    {
        "title": "Teamwork & Collaboration – SWAYAM",
        "platform": "SWAYAM",
        "skill": "Teamwork",
        "skill_category": "Soft",
        "difficulty": "Beginner",
        "description": "Free SWAYAM course on workplace teamwork, collaboration frameworks, and conflict resolution.",
        "url": "https://swayam.gov.in/",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "6 weeks",
        "source": "sample"
    },
    {
        "title": "Problem Solving & Critical Thinking – GeeksforGeeks",
        "platform": "GeeksforGeeks",
        "skill": "Problem Solving",
        "skill_category": "Soft",
        "difficulty": "Beginner",
        "description": "Articles and practice problems focused on analytical thinking, logic puzzles, and structured problem-solving approaches.",
        "url": "https://www.geeksforgeeks.org/puzzles/",
        "resource_type": "Tutorial",
        "is_free": True,
        "thumbnail": None,
        "duration": "Self-paced",
        "source": "sample"
    },
    {
        "title": "Time Management – NPTEL",
        "platform": "NPTEL",
        "skill": "Time Management",
        "skill_category": "Soft",
        "difficulty": "Beginner",
        "description": "NPTEL lectures on productivity, prioritization frameworks (Eisenhower Matrix, Pomodoro), and goal setting.",
        "url": "https://nptel.ac.in/courses/110/106/110106061/",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "4 weeks",
        "source": "sample"
    },
    {
        "title": "Public Speaking – TED-Ed",
        "platform": "YouTube",
        "skill": "Public Speaking",
        "skill_category": "Soft",
        "difficulty": "Beginner",
        "description": "TED-Ed videos on overcoming public speaking anxiety, structuring talks, and confident delivery.",
        "url": "https://www.youtube.com/playlist?list=PLJicmE8fK0EiEzttYMD1zYkT-SmNf323z",
        "resource_type": "Playlist",
        "is_free": True,
        "thumbnail": None,
        "duration": "Self-paced",
        "source": "sample"
    },
    {
        "title": "Interview Skills & Career Readiness – TCS iON",
        "platform": "TCS iON",
        "skill": "Interview Skills",
        "skill_category": "Soft",
        "difficulty": "Beginner",
        "description": "TCS iON free course on interview preparation, resume writing, group discussions, and professional etiquette.",
        "url": "https://learning.tcsionhub.in/hub/national/",
        "resource_type": "Course",
        "is_free": True,
        "thumbnail": None,
        "duration": "Self-paced",
        "source": "sample"
    },
]


def get_sample_data(technical_skills: list, soft_skills: list) -> dict:
    """
    Return filtered sample recommendations based on requested skills.
    If no skills match, return all sample data.
    """
    tech_lower = [s.lower() for s in technical_skills]
    soft_lower = [s.lower() for s in soft_skills]

    if tech_lower:
        tech_recs = [
            r for r in SAMPLE_TECHNICAL
            if r["skill"].lower() in tech_lower
        ]
        # If no exact match, return all technical samples
        if not tech_recs:
            tech_recs = SAMPLE_TECHNICAL
    else:
        tech_recs = SAMPLE_TECHNICAL

    if soft_lower:
        soft_recs = [
            r for r in SAMPLE_SOFT
            if r["skill"].lower() in soft_lower
        ]
        if not soft_recs:
            soft_recs = SAMPLE_SOFT
    else:
        soft_recs = SAMPLE_SOFT

    return {
        "technical": tech_recs,
        "soft": soft_recs
    }
