import uuid
import random
from typing import List, Dict, Any, Tuple
from app.config import settings
from app.core.logging import logger
from app.schemas.resume import (
    ResumeStructuredData, CandidateInfo, CategorizedSkills,
    EducationItem, ExperienceItem, InternshipItem, ProjectItem,
    CertificationItem, AchievementItem, ExtractionMetadata
)
from app.schemas.job import JobStructuredData
from app.schemas.persona import SyntheticPersonaItem
from app.matching.ats_engine import ats_engine
from app.ai.groq_client import groq_client
from app.ai.prompts import SYNTHETIC_CANDIDATE_BATCH_PROMPT

class SyntheticPersonaGenerator:
    """
    Generates exactly 100 unique, realistic, job-specific synthetic candidate profiles
    distributed across 7 competency bands:
    - very_high: 10
    - high: 20
    - upper_middle: 20
    - middle: 20
    - lower_middle: 15
    - low: 10
    - very_low: 5
    Total: 100
    """
    def __init__(self):
        self.bands = settings.SYNTHETIC_BAND_DISTRIBUTION

    def generate_and_score_pool(
        self,
        job: JobStructuredData,
        session_id: str
    ) -> List[SyntheticPersonaItem]:
        """
        Generates 100 unique profiles and scores each profile using the EXACT SAME ATS Engine.
        """
        logger.info(f"Generating 100 synthetic benchmark profiles for job '{job.title}'...")
        all_items: List[SyntheticPersonaItem] = []
        candidate_counter = 1

        for band, count in self.bands.items():
            # Generate in batches of up to 10
            generated_in_band = 0
            while generated_in_band < count:
                batch_size = min(settings.SYNTHETIC_BATCH_SIZE, count - generated_in_band)
                batch_profiles = self._generate_batch(job, band, batch_size, candidate_counter)
                
                for profile in batch_profiles:
                    candidate_counter += 1
                    # Score using the exact same ATS Engine as the real candidate
                    score, breakdown, _, _ = ats_engine.evaluate(profile, job)
                    
                    item = SyntheticPersonaItem(
                        id=str(uuid.uuid4()),
                        competency_band=band,
                        profile=profile,
                        ats_score=score,
                        score_breakdown=breakdown.model_dump()
                    )
                    all_items.append(item)
                    generated_in_band += 1

        logger.info(f"Successfully generated and evaluated {len(all_items)} synthetic profiles.")
        return all_items

    def _generate_batch(
        self,
        job: JobStructuredData,
        band: str,
        count: int,
        start_index: int
    ) -> List[ResumeStructuredData]:
        """Generates a batch of synthetic profiles for a specific band."""
        if groq_client.is_available() and settings.USE_GROQ_FOR_SYNTHETIC_POOL:
            prompt = SYNTHETIC_CANDIDATE_BATCH_PROMPT.replace("{band}", band).replace("{count}", str(count))
            user_msg = f"Target Job: {job.title}\nRequired Skills: {', '.join(job.required_skills)}\nPreferred: {', '.join(job.preferred_skills)}"
            ai_data = groq_client.call_structured(prompt, user_msg, temperature=0.7)
            if ai_data and "candidates" in ai_data and len(ai_data["candidates"]) >= count:
                try:
                    res = []
                    for c_raw in ai_data["candidates"][:count]:
                        # Ensure schema fields
                        p = ResumeStructuredData(**c_raw)
                        res.append(p)
                    return res
                except Exception as e:
                    logger.warning(f"Groq synthetic batch schema mismatch: {e}. Using deterministic archetype generator.")

        # Deterministic Realistic Archetype Generator
        return [self._create_archetype_profile(job, band, start_index + i) for i in range(count)]

    def _create_archetype_profile(
        self,
        job: JobStructuredData,
        band: str,
        index: int
    ) -> ResumeStructuredData:
        """
        Creates a realistic, varied candidate profile tailored to the job and guided by the competency band.
        """
        all_req = list(job.required_skills)
        all_pref = list(job.preferred_skills)
        random.seed(index * 42 + hash(job.title))

        # Skill selection guided by band
        if band == "very_high":
            # 100% req skills + most preferred skills + internships + solid projects
            skills = all_req + random.sample(all_pref, min(len(all_pref), 3)) + ["Git", "Linux", "Docker"]
            has_internship = True
            project_count = 3
            outcomes = "Reduced response latency by 35% and scaled system to 10k daily requests."
        elif band == "high":
            # ~85% req skills + some preferred skills
            skills = random.sample(all_req, max(1, int(len(all_req) * 0.85))) + random.sample(all_pref, min(len(all_pref), 2))
            has_internship = random.choice([True, False])
            project_count = 2
            outcomes = "Built responsive REST APIs with unit test coverage of 80%."
        elif band == "upper_middle":
            # ~70% req skills
            skills = random.sample(all_req, max(1, int(len(all_req) * 0.70))) + ["Git"]
            has_internship = False
            project_count = 2
            outcomes = "Integrated persistent database models and validated user authentication."
        elif band == "middle":
            # ~50% req skills
            skills = random.sample(all_req, max(1, int(len(all_req) * 0.50)))
            has_internship = False
            project_count = 1
            outcomes = "Completed functioning prototype for university coursework."
        elif band == "lower_middle":
            # ~35% req skills
            skills = random.sample(all_req, max(1, int(len(all_req) * 0.35))) + ["HTML", "CSS"]
            has_internship = False
            project_count = 1
            outcomes = "Basic project demonstration."
        elif band == "low":
            # 1 req skill or only tangential
            skills = random.sample(all_req, 1) + ["Word", "Excel", "Communication"]
            has_internship = False
            project_count = 1
            outcomes = "Introductory project."
        else: # very_low
            # Completely unrelated
            skills = ["Data Entry", "MS Office", "Customer Support"]
            has_internship = False
            project_count = 0
            outcomes = ""

        # Dedup skills
        skills = list(dict.fromkeys(skills))

        # Projects
        projects = []
        for p_idx in range(project_count):
            p_techs = random.sample(skills, min(len(skills), 3)) if skills else ["Python"]
            projects.append(ProjectItem(
                title=f"{job.title} Service {index}-{p_idx+1}",
                description=f"Developed backend architecture utilizing {', '.join(p_techs)}.",
                technologies=p_techs,
                contribution="Led module implementation, route creation, and testing.",
                features=["REST API endpoints", "Database connection", "Error handling"],
                outcomes=outcomes
            ))

        # Internships
        internships = []
        if has_internship:
            internships.append(InternshipItem(
                organization="Technology Labs Inc.",
                role="Software Engineering Intern",
                duration="6 months",
                start_date="01/2023",
                end_date="06/2023",
                responsibilities=["Assisted with backend microservice design", "Wrote unit tests"],
                technologies=skills[:3]
            ))

        return ResumeStructuredData(
            candidate=CandidateInfo(
                name=f"Synthetic Candidate #{index:03d}",
                headline=f"Candidate aiming for {job.title}",
                summary=f"Graduate portfolio tailored for {job.title} screening benchmark."
            ),
            education=[
                EducationItem(
                    degree="B.Tech" if band not in ["low", "very_low"] else "B.Com",
                    branch="Computer Science" if band not in ["low", "very_low"] else "General",
                    institution="Tier-2 Regional Institute",
                    graduation_year=2024,
                    evidence="Bachelor degree certified"
                )
            ],
            skills=CategorizedSkills(
                programming_languages=[s for s in skills if s in ["Python", "JavaScript", "Java", "C++", "Go", "SQL"]],
                frameworks=[s for s in skills if s in ["FastAPI", "Flask", "Django", "React", "Node.js"]],
                tools=[s for s in skills if s in ["Git", "Docker", "Linux"]]
            ),
            all_skills_flat=skills,
            projects=projects,
            internships=internships,
            extraction_metadata=ExtractionMetadata(
                source_format="synthetic_generator",
                extraction_status="completed",
                schema_version="1.0"
            )
        )

synthetic_generator = SyntheticPersonaGenerator()
